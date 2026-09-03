"""
VeriForge Grounding Engine
==========================
Deterministic, keyword + category scoring engine.
No LLM calls. No vector database. No external dependencies.

Public API
----------
    from app.grounding.grounder import ground_finding

    result = ground_finding(
        category="sql_injection",
        keywords=["username", "query", "concatenation"],
        snippet="query = 'SELECT * FROM users WHERE name=\\'' + username + '\\''",
    )
    # Returns GroundingResult | GroundingFailure

Scoring Algorithm
-----------------
    score = (category_match × CATEGORY_WEIGHT) + (keyword_overlap × KEYWORD_WEIGHT)

    A finding is grounded only when score >= CONFIDENCE_THRESHOLD.
    Returning grounded=False is always preferred over forcing a low-confidence match.
"""

from __future__ import annotations

import json
import re
import unicodedata
from functools import lru_cache
from pathlib import Path
from typing import Union

from app.grounding.models import (
    GroundingFailure,
    GroundingRequest,
    GroundingResult,
    GroundingSource,
)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

KNOWLEDGE_BASE_PATH = Path(__file__).parent / "knowledge_base.json"

# Scoring weights
CATEGORY_WEIGHT = 5      # bonus for a direct category or alias match
KEYWORD_WEIGHT = 1       # per overlapping keyword

# Minimum raw score to return grounded=True
CONFIDENCE_THRESHOLD = 3

# Maximum raw score (used to normalise confidence to [0, 1])
# = CATEGORY_WEIGHT + (max expected keyword overlap × KEYWORD_WEIGHT)
_MAX_SCORE_CAP = CATEGORY_WEIGHT + 15


# ---------------------------------------------------------------------------
# Knowledge-base loader (cached — loaded once per process)
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def _load_rules() -> list[dict]:
    """Load and return rules from knowledge_base.json (cached)."""
    raw = KNOWLEDGE_BASE_PATH.read_text(encoding="utf-8")
    return json.loads(raw)


# ---------------------------------------------------------------------------
# Text normalisation helpers
# ---------------------------------------------------------------------------

_NON_ALNUM = re.compile(r"[^a-z0-9_]")


def _normalise(text: str) -> str:
    """Lowercase, strip accents, replace non-alphanumeric with space."""
    text = text.lower()
    # Strip unicode combining characters
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    # Replace non-word chars with space
    text = _NON_ALNUM.sub(" ", text)
    return text


def _tokenise(text: str) -> set[str]:
    """Return a set of normalised tokens from text (min length 3)."""
    return {t for t in _normalise(text).split() if len(t) >= 3}


def _normalise_category(cat: str) -> str:
    """Normalise a category slug."""
    return _normalise(cat).replace(" ", "_")


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def _score_rule(rule: dict, norm_category: str, norm_keywords: set[str]) -> int:
    """
    Compute a relevance score for a single rule given the request.

    Parameters
    ----------
    rule           : dict  — one entry from knowledge_base.json
    norm_category  : str   — normalised category from the request
    norm_keywords  : set   — normalised keyword tokens from the request

    Returns
    -------
    int — raw relevance score (0 = no match)
    """
    score = 0

    # --- Category match ---
    rule_category = _normalise_category(rule.get("category", ""))
    rule_aliases = [
        _normalise_category(a) for a in rule.get("category_aliases", [])
    ]

    if norm_category and (
        norm_category == rule_category or norm_category in rule_aliases
    ):
        score += CATEGORY_WEIGHT

    # --- Keyword overlap ---
    rule_keywords: set[str] = set()
    for kw in rule.get("keywords", []):
        rule_keywords.update(_tokenise(kw))

    overlap = norm_keywords & rule_keywords
    score += len(overlap) * KEYWORD_WEIGHT

    return score


# ---------------------------------------------------------------------------
# why_it_applies builder
# ---------------------------------------------------------------------------

def _build_why_it_applies(rule: dict, snippet: str, norm_keywords: set[str]) -> str:
    """
    Construct the 'why_it_applies' field without LLM assistance.
    Uses the rule description plus evidence from the matched keywords.
    """
    rule_kw_set: set[str] = set()
    for kw in rule.get("keywords", []):
        rule_kw_set.update(_tokenise(kw))

    matched = sorted(norm_keywords & rule_kw_set)

    parts: list[str] = [rule["description"]]

    if matched:
        parts.append(
            f"The following indicators in the finding match this rule: "
            f"{', '.join(matched[:6])}."
        )

    if snippet.strip():
        # Show up to 120 chars of the snippet for context
        truncated = snippet.strip()[:120].replace("\n", " ")
        parts.append(
            f"The submitted code pattern — '{truncated}' — "
            f"is consistent with the vulnerable examples documented for {rule['title']}."
        )

    return " ".join(parts)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def ground_finding(
    category: str,
    keywords: list[str],
    snippet: str = "",
) -> Union[GroundingResult, GroundingFailure]:
    """
    Match a code-review finding against the curated knowledge base.

    Parameters
    ----------
    category : str
        Category label from the review engine (e.g. "sql_injection").
        Case-insensitive.
    keywords : list[str]
        Salient tokens from the finding or code snippet.
    snippet : str, optional
        Raw code snippet for additional context in why_it_applies.

    Returns
    -------
    GroundingResult
        When a reliable match is found (score >= CONFIDENCE_THRESHOLD).
    GroundingFailure
        When no rule can be matched with sufficient confidence.
        VeriForge must NEVER force a match — prefer this return value.
    """
    norm_category = _normalise_category(category) if category else ""

    # Build a unified keyword set from the request keywords + snippet tokens
    norm_keywords: set[str] = set()
    for kw in keywords:
        norm_keywords.update(_tokenise(kw))
    if snippet:
        norm_keywords.update(_tokenise(snippet))

    rules = _load_rules()

    # Score every rule
    scored: list[tuple[int, dict]] = []
    for rule in rules:
        s = _score_rule(rule, norm_category, norm_keywords)
        if s > 0:
            scored.append((s, rule))

    if not scored:
        return GroundingFailure()

    # Take the highest-scoring rule
    best_score, best_rule = max(scored, key=lambda x: x[0])

    if best_score < CONFIDENCE_THRESHOLD:
        return GroundingFailure(
            reason=(
                f"Highest match score ({best_score}) is below the confidence "
                f"threshold ({CONFIDENCE_THRESHOLD}). "
                "Insufficient evidence to establish a reliable rule match."
            )
        )

    # Normalise score to [0.0, 1.0]
    confidence = round(min(best_score / _MAX_SCORE_CAP, 1.0), 3)

    source_data = best_rule["source"]
    source = GroundingSource(
        name=source_data["name"],
        title=source_data["title"],
        url=source_data["url"],
        type=source_data["type"],
    )

    why = _build_why_it_applies(best_rule, snippet, norm_keywords)

    return GroundingResult(
        grounded=True,
        rule_id=best_rule["id"],
        title=best_rule["title"],
        category=best_rule["category"],
        cwe=best_rule["cwe"],
        source=source,
        evidence=best_rule["evidence"],
        why_it_applies=why,
        remediation=best_rule["remediation"],
        verification=best_rule["verification"],
        confidence=confidence,
    )


def ground_from_request(req: GroundingRequest) -> Union[GroundingResult, GroundingFailure]:
    """Convenience wrapper that accepts a GroundingRequest model."""
    return ground_finding(
        category=req.category,
        keywords=req.keywords,
        snippet=req.snippet,
    )

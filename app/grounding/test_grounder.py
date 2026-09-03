"""
VeriForge Grounding Layer — Test Suite
=======================================
Run with:
    cd <repo-root>
    python -m pytest app/grounding/test_grounder.py -v

Requirements:
    pip install pytest httpx fastapi pydantic
"""

import json
import pytest
from pathlib import Path

from app.grounding.grounder import ground_finding, _load_rules, CONFIDENCE_THRESHOLD
from app.grounding.models import GroundingResult, GroundingFailure


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

KB_PATH = Path(__file__).parent / "knowledge_base.json"


def all_rule_ids() -> list[str]:
    rules = json.loads(KB_PATH.read_text(encoding="utf-8"))
    return [r["id"] for r in rules]


def all_rule_categories() -> list[tuple[str, str]]:
    """Return (rule_id, category) pairs for parametrised reachability tests."""
    rules = json.loads(KB_PATH.read_text(encoding="utf-8"))
    return [(r["id"], r["category"]) for r in rules]


# ---------------------------------------------------------------------------
# 1. Knowledge-base integrity
# ---------------------------------------------------------------------------


class TestKnowledgeBaseIntegrity:
    def test_kb_loads(self):
        """Knowledge base must load without errors."""
        rules = _load_rules()
        assert isinstance(rules, list)
        assert len(rules) > 0

    def test_all_rules_have_required_fields(self):
        required = {
            "id",
            "title",
            "category",
            "cwe",
            "keywords",
            "source",
            "evidence",
            "remediation",
            "verification",
        }
        rules = _load_rules()
        for rule in rules:
            missing = required - rule.keys()
            assert not missing, f"Rule {rule.get('id')} is missing fields: {missing}"

    def test_all_sources_have_url(self):
        rules = _load_rules()
        for rule in rules:
            url = rule.get("source", {}).get("url", "")
            assert url.startswith("http"), (
                f"Rule {rule['id']} has an invalid source URL: '{url}'"
            )

    def test_no_duplicate_rule_ids(self):
        rules = _load_rules()
        ids = [r["id"] for r in rules]
        assert len(ids) == len(set(ids)), "Duplicate rule IDs found in knowledge base"

    def test_twenty_rules_present(self):
        rules = _load_rules()
        assert len(rules) == 20, f"Expected 20 rules, found {len(rules)}"


# ---------------------------------------------------------------------------
# 2. Happy-path matching — canonical cases
# ---------------------------------------------------------------------------


class TestCanonicalMatches:
    def test_hardcoded_credentials(self):
        result = ground_finding(
            category="secrets",
            keywords=["password", "hardcoded", "db_password"],
            snippet='DB_PASSWORD = "admin123"',
        )
        assert isinstance(result, GroundingResult)
        assert result.grounded is True
        assert result.rule_id == "SEC-001"
        assert result.cwe == "CWE-798"

    def test_sql_injection(self):
        result = ground_finding(
            category="sql_injection",
            keywords=["username", "query", "concatenation", "select"],
            snippet='query = "SELECT * FROM users WHERE name=\'" + username + "\'"',
        )
        assert isinstance(result, GroundingResult)
        assert result.grounded is True
        assert result.rule_id == "SEC-002"
        assert result.cwe == "CWE-89"

    def test_command_injection(self):
        result = ground_finding(
            category="command_injection",
            keywords=["os.system", "user_input", "shell"],
            snippet="os.system('ping ' + user_input)",
        )
        assert isinstance(result, GroundingResult)
        assert result.grounded is True
        assert result.rule_id == "SEC-003"
        assert result.cwe == "CWE-78"

    def test_xss(self):
        result = ground_finding(
            category="xss",
            keywords=["innerHTML", "user_input", "script"],
            snippet="element.innerHTML = userInput;",
        )
        assert isinstance(result, GroundingResult)
        assert result.grounded is True
        assert result.rule_id == "SEC-004"
        assert result.cwe == "CWE-79"

    def test_path_traversal(self):
        result = ground_finding(
            category="path_traversal",
            keywords=["file", "path", "filename", "open"],
            snippet="open('/var/uploads/' + filename)",
        )
        assert isinstance(result, GroundingResult)
        assert result.grounded is True
        assert result.rule_id == "SEC-005"

    def test_missing_authentication(self):
        result = ground_finding(
            category="missing_authentication",
            keywords=["unauthenticated", "admin", "endpoint", "no auth"],
            snippet="",
        )
        assert isinstance(result, GroundingResult)
        assert result.grounded is True
        assert result.rule_id == "SEC-006"

    def test_broken_authorization(self):
        result = ground_finding(
            category="broken_authorization",
            keywords=["idor", "user_id", "ownership", "access control"],
            snippet="",
        )
        assert isinstance(result, GroundingResult)
        assert result.grounded is True
        assert result.rule_id == "SEC-007"

    def test_insecure_password_storage(self):
        result = ground_finding(
            category="insecure_password_storage",
            keywords=["md5", "hashlib", "password", "hash"],
            snippet="hashed = hashlib.md5(password.encode()).hexdigest()",
        )
        assert isinstance(result, GroundingResult)
        assert result.grounded is True
        assert result.rule_id == "SEC-008"

    def test_sensitive_information_exposure(self):
        result = ground_finding(
            category="sensitive_information_exposure",
            keywords=["log", "password", "print", "debug"],
            snippet="logger.info(f'password: {password}')",
        )
        assert isinstance(result, GroundingResult)
        assert result.grounded is True
        assert result.rule_id == "SEC-009"

    def test_security_misconfiguration(self):
        result = ground_finding(
            category="security_misconfiguration",
            keywords=["debug", "debug=True", "development"],
            snippet="app.run(debug=True)",
        )
        assert isinstance(result, GroundingResult)
        assert result.grounded is True
        assert result.rule_id == "SEC-010"

    def test_insecure_cryptography(self):
        result = ground_finding(
            category="insecure_cryptography",
            keywords=["des", "rc4", "md5", "weak", "cipher"],
            snippet="cipher = DES.new(key, DES.MODE_ECB)",
        )
        assert isinstance(result, GroundingResult)
        assert result.grounded is True
        assert result.rule_id == "SEC-011"

    def test_weak_session_management(self):
        result = ground_finding(
            category="weak_session_management",
            keywords=["session", "cookie", "httponly", "secure", "token"],
            snippet="response.set_cookie('session', user_id)",
        )
        assert isinstance(result, GroundingResult)
        assert result.grounded is True
        assert result.rule_id == "SEC-012"

    def test_ssrf(self):
        result = ground_finding(
            category="ssrf",
            keywords=["url", "requests.get", "user_input", "fetch"],
            snippet="requests.get(user_supplied_url)",
        )
        assert isinstance(result, GroundingResult)
        assert result.grounded is True
        assert result.rule_id == "SEC-013"

    def test_csrf(self):
        result = ground_finding(
            category="csrf",
            keywords=["csrf", "token", "form", "post", "missing_csrf"],
            snippet="",
        )
        assert isinstance(result, GroundingResult)
        assert result.grounded is True
        assert result.rule_id == "SEC-014"

    def test_insecure_deserialization(self):
        result = ground_finding(
            category="insecure_deserialization",
            keywords=["pickle", "loads", "untrusted"],
            snippet="data = pickle.loads(request.body)",
        )
        assert isinstance(result, GroundingResult)
        assert result.grounded is True
        assert result.rule_id == "SEC-015"

    def test_dangerous_file_upload(self):
        result = ground_finding(
            category="dangerous_file_upload",
            keywords=["upload", "file", "filename", "save"],
            snippet="file.save('/var/www/uploads/' + file.filename)",
        )
        assert isinstance(result, GroundingResult)
        assert result.grounded is True
        assert result.rule_id == "SEC-016"

    def test_missing_rate_limiting(self):
        result = ground_finding(
            category="missing_rate_limiting",
            keywords=["login", "password", "brute force", "no limit"],
            snippet="",
        )
        assert isinstance(result, GroundingResult)
        assert result.grounded is True
        assert result.rule_id == "SEC-017"

    def test_debug_error_exposure(self):
        result = ground_finding(
            category="debug_error_exposure",
            keywords=["traceback", "exception", "debug", "verbose"],
            snippet="return {'traceback': traceback.format_exc()}",
        )
        assert isinstance(result, GroundingResult)
        assert result.grounded is True
        assert result.rule_id == "SEC-018"

    def test_supply_chain(self):
        result = ground_finding(
            category="supply_chain",
            keywords=["dependency", "package", "outdated", "cve"],
            snippet="",
        )
        assert isinstance(result, GroundingResult)
        assert result.grounded is True
        assert result.rule_id == "SEC-019"

    def test_insecure_randomness(self):
        result = ground_finding(
            category="insecure_randomness",
            keywords=["random", "randint", "predictable", "token"],
            snippet="token = str(random.randint(100000, 999999))",
        )
        assert isinstance(result, GroundingResult)
        assert result.grounded is True
        assert result.rule_id == "SEC-020"


# ---------------------------------------------------------------------------
# 3. No-match / failure cases — CRITICAL safety behaviour
# ---------------------------------------------------------------------------


class TestNoMatch:
    def test_empty_category_and_keywords_returns_failure(self):
        result = ground_finding(category="", keywords=[], snippet="")
        assert isinstance(result, GroundingFailure)
        assert result.grounded is False
        assert "reason" in result.model_dump()

    def test_completely_unknown_category_returns_failure(self):
        result = ground_finding(
            category="totally_made_up_category_xyz",
            keywords=[],
            snippet="",
        )
        assert isinstance(result, GroundingFailure)
        assert result.grounded is False

    def test_weak_signal_below_threshold_returns_failure(self):
        """A single very generic keyword should not produce a match."""
        result = ground_finding(
            category="",
            keywords=["code"],
            snippet="",
        )
        assert isinstance(result, GroundingFailure)
        assert result.grounded is False

    def test_grounding_failure_never_has_rule_id(self):
        result = ground_finding(category="", keywords=[], snippet="")
        data = result.model_dump()
        assert "rule_id" not in data or data.get("grounded") is True


# ---------------------------------------------------------------------------
# 4. Response structure / schema validation
# ---------------------------------------------------------------------------


class TestSchema:
    def test_grounding_result_has_all_required_fields(self):
        result = ground_finding(
            category="sql_injection",
            keywords=["sql", "select", "query", "username"],
            snippet="",
        )
        assert isinstance(result, GroundingResult)
        data = result.model_dump()
        for field in (
            "grounded",
            "rule_id",
            "title",
            "category",
            "cwe",
            "source",
            "evidence",
            "why_it_applies",
            "remediation",
            "verification",
            "confidence",
        ):
            assert field in data, f"Field '{field}' missing from GroundingResult"

    def test_source_has_required_sub_fields(self):
        result = ground_finding(
            category="sql_injection",
            keywords=["sql", "select", "query"],
            snippet="",
        )
        assert isinstance(result, GroundingResult)
        source = result.model_dump()["source"]
        for key in ("name", "title", "url", "type"):
            assert key in source, f"Source is missing field: '{key}'"

    def test_confidence_in_valid_range(self):
        result = ground_finding(
            category="secrets",
            keywords=["password", "hardcoded"],
            snippet="",
        )
        assert isinstance(result, GroundingResult)
        assert 0.0 <= result.confidence <= 1.0

    def test_grounded_true_for_result(self):
        result = ground_finding(
            category="xss",
            keywords=["innerHTML", "script", "user_input"],
            snippet="",
        )
        assert isinstance(result, GroundingResult)
        assert result.grounded is True

    def test_grounded_false_for_failure(self):
        result = ground_finding(category="", keywords=[], snippet="")
        assert isinstance(result, GroundingFailure)
        assert result.grounded is False

    def test_failure_has_reason_field(self):
        result = ground_finding(category="", keywords=[], snippet="")
        assert isinstance(result, GroundingFailure)
        assert result.reason
        assert len(result.reason) > 5

    def test_result_is_json_serialisable(self):
        result = ground_finding(
            category="command_injection",
            keywords=["os.system", "shell", "user_input"],
            snippet="",
        )
        data = result.model_dump()
        # model_dump output must be trivially serialisable
        out = json.dumps(data)
        parsed = json.loads(out)
        assert parsed["grounded"] is True

    def test_failure_is_json_serialisable(self):
        result = ground_finding(category="", keywords=[], snippet="")
        out = json.dumps(result.model_dump())
        parsed = json.loads(out)
        assert parsed["grounded"] is False


# ---------------------------------------------------------------------------
# 5. Keyword-only matching (category bypass)
# ---------------------------------------------------------------------------


class TestKeywordOnlyMatching:
    def test_keyword_match_without_category(self):
        """Strong keyword signal alone should produce a match."""
        result = ground_finding(
            category="",  # no category provided
            keywords=["password", "hardcoded", "db_password", "secret", "api_key"],
            snippet="",
        )
        assert isinstance(result, GroundingResult)
        assert result.grounded is True

    def test_alias_category_resolves_correctly(self):
        """Category aliases must map to the same rule as the canonical category."""
        result_canonical = ground_finding(
            category="sql_injection",
            keywords=["sql", "query", "select"],
            snippet="",
        )
        result_alias = ground_finding(
            category="sqli",
            keywords=["sql", "query", "select"],
            snippet="",
        )
        assert isinstance(result_canonical, GroundingResult)
        assert isinstance(result_alias, GroundingResult)
        assert result_canonical.rule_id == result_alias.rule_id


# ---------------------------------------------------------------------------
# 6. HTTP endpoint tests (uses FastAPI TestClient)
# ---------------------------------------------------------------------------


class TestHTTPEndpoint:
    @pytest.fixture(scope="class")
    @classmethod
    def client(cls):
        from fastapi.testclient import TestClient
        from app.main import app

        return TestClient(app)

    def test_health_check(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    def test_ground_endpoint_returns_200(self, client):
        payload = {
            "category": "secrets",
            "keywords": ["password", "hardcoded", "db_password"],
            "snippet": "DB_PASSWORD = 'admin123'",
        }
        resp = client.post("/ground", json=payload)
        assert resp.status_code == 200

    def test_ground_endpoint_sql_injection(self, client):
        payload = {
            "category": "sql_injection",
            "keywords": ["username", "query", "select", "concatenation"],
            "snippet": 'query = "SELECT * FROM users WHERE name=\'" + username + "\'"',
        }
        resp = client.post("/ground", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["grounded"] is True
        assert data["rule_id"] == "SEC-002"

    def test_ground_endpoint_no_match_returns_grounded_false(self, client):
        payload = {
            "category": "completely_unknown",
            "keywords": [],
            "snippet": "",
        }
        resp = client.post("/ground", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["grounded"] is False
        assert "reason" in data

    def test_ground_endpoint_invalid_payload_returns_422(self, client):
        """Missing required 'category' field should return 422."""
        resp = client.post("/ground", json={"keywords": ["foo"]})
        assert resp.status_code == 422

    def test_ground_endpoint_response_has_source_url(self, client):
        payload = {
            "category": "xss",
            "keywords": ["innerHTML", "script", "user_input", "unsanitized"],
            "snippet": "",
        }
        resp = client.post("/ground", json=payload)
        data = resp.json()
        if data["grounded"]:
            assert data["source"]["url"].startswith("http")

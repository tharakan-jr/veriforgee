import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from app.services.llm.base import LLMProvider
from app.services.review_service import ReviewService
from app.models.review import SeverityEnum, ReviewResponse, Finding


class FailingLLMProvider(LLMProvider):
    """Mock provider that always raises an exception."""
    async def generate(self, prompt: str, system_prompt: str) -> str:
        raise RuntimeError("LLM API Connection Timeout")


class RawStringLLMProvider(LLMProvider):
    """Mock provider returning raw non-JSON text."""
    def __init__(self, raw_content: str):
        self.raw_content = raw_content

    async def generate(self, prompt: str, system_prompt: str) -> str:
        return self.raw_content


# Test 1: Valid review output
def test_valid_review_output(client: TestClient):
    payload = {
        "artefact": "api_key = 'sk-1234567890qwertyuiop'\nprint('Connecting')",
        "language": "python",
        "context": "Authentication script"
    }
    response = client.post("/api/v1/review", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "summary" in data
    assert isinstance(data["findings"], list)
    assert len(data["findings"]) > 0

    finding = data["findings"][0]
    assert "id" in finding
    assert finding["id"].startswith("finding-")
    assert finding["severity"] in [s.value for s in SeverityEnum]
    assert "title" in finding
    assert "category" in finding
    assert "description" in finding
    assert "location" in finding
    assert "why_it_matters" in finding
    assert "recommendation" in finding
    assert "verification_question" in finding


# Test 2: Invalid/malformed LLM output handling
@pytest.mark.asyncio
async def test_invalid_llm_json_recovery():
    malformed_provider = RawStringLLMProvider("Sorry, I cannot analyze this snippet as JSON!")
    service = ReviewService(provider=malformed_provider)

    response: ReviewResponse = await service.review_artefact("def hello(): pass")
    assert response.status == "success"
    assert len(response.findings) == 1
    assert response.findings[0].id == "finding-001"
    assert "non-JSON" in response.findings[0].description or "anomaly" in response.findings[0].description


# Test 3: Empty artefact validation
def test_empty_artefact_validation(client: TestClient):
    # Empty string (Pydantic schema validation returns 422 Unprocessable Entity)
    response_empty = client.post("/api/v1/review", json={"artefact": ""})
    assert response_empty.status_code in [400, 422]

    # Whitespace only
    response_spaces = client.post("/api/v1/review", json={"artefact": "   \n\t  "})
    assert response_spaces.status_code in [400, 422]



# Test 4: Very large artefact handling
def test_very_large_artefact_handling(client: TestClient):
    large_artefact = "x = 1\n" * 20000  # ~120KB string exceeding default limit
    payload = {
        "artefact": large_artefact,
        "language": "python"
    }
    response = client.post("/api/v1/review", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["findings"]) > 0


# Test 5: Severity validation
@pytest.mark.asyncio
async def test_severity_validation():
    # LLM output containing unknown severity string like "super_critical"
    raw_json = """
    {
      "summary": "Custom review",
      "findings": [
        {
          "severity": "super_critical",
          "title": "Invalid Severity Test",
          "description": "Testing severity fallback",
          "why_it_matters": "Invalid enums should normalize to info",
          "recommendation": "Use valid severity",
          "verification_question": "What is the severity?"
        }
      ]
    }
    """
    provider = RawStringLLMProvider(raw_json)
    service = ReviewService(provider=provider)

    response = await service.review_artefact("code snippet")
    assert len(response.findings) == 1
    assert response.findings[0].severity == SeverityEnum.INFO


# Test 6: Missing fields handling
@pytest.mark.asyncio
async def test_missing_fields_handling():
    # LLM output missing why_it_matters and verification_question
    raw_json = """
    {
      "summary": "Incomplete json fields",
      "findings": [
        {
          "severity": "high",
          "title": "Missing fields item",
          "description": "Description only"
        }
      ]
    }
    """
    provider = RawStringLLMProvider(raw_json)
    service = ReviewService(provider=provider)

    response = await service.review_artefact("code snippet")
    assert len(response.findings) == 1
    finding = response.findings[0]
    assert finding.title == "Missing fields item"
    assert finding.why_it_matters != ""
    assert finding.verification_question != ""
    assert finding.recommendation != ""


# Test 7: LLM/provider failure fallback
@pytest.mark.asyncio
async def test_llm_provider_failure():
    failing_provider = FailingLLMProvider()
    service = ReviewService(provider=failing_provider)

    response = await service.review_artefact("code snippet")
    assert response.status == "success"
    assert len(response.findings) == 1
    assert "LLM API Connection Timeout" in response.findings[0].description

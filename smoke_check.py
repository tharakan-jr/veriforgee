"""End-to-end smoke check for VeriForge grounding layer."""

import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
errors = []

# /health
r = client.get("/health")
if r.status_code != 200 or r.json().get("status") != "ok":
    errors.append(f"FAIL /health: {r.status_code} {r.text}")
else:
    print("PASS  /health")

# grounded=True, SEC-001
r = client.post(
    "/ground",
    json={
        "category": "secrets",
        "keywords": ["password", "hardcoded", "db_password"],
        "snippet": "DB_PASSWORD='admin123'",
    },
)
d = r.json()
if r.status_code != 200 or not d.get("grounded") or d.get("rule_id") != "SEC-001":
    errors.append(f"FAIL  /ground(SEC-001): {d}")
else:
    required = (
        "evidence",
        "why_it_applies",
        "remediation",
        "verification",
        "confidence",
    )
    missing = [f for f in required if not d.get(f)]
    if missing:
        errors.append(f"FAIL  missing fields: {missing}")
    elif not d["source"]["url"].startswith("http"):
        errors.append("FAIL  source url invalid")
    else:
        print(
            f"PASS  POST /ground  grounded=True  rule_id={d['rule_id']}  cwe={d['cwe']}  confidence={d['confidence']}"
        )

# grounded=False
r = client.post(
    "/ground", json={"category": "xyz_unknown_cat", "keywords": [], "snippet": ""}
)
d = r.json()
if r.status_code != 200 or d.get("grounded") is not False or "reason" not in d:
    errors.append(f"FAIL  /ground(no-match): {d}")
else:
    print("PASS  POST /ground  grounded=False  reason present")

# 422 on bad payload
r = client.post("/ground", json={"keywords": ["foo"]})
if r.status_code != 422:
    errors.append(f"FAIL  expected 422, got {r.status_code}")
else:
    print("PASS  POST /ground  422 on missing 'category'")

# All 20 rules must be reachable
with open("app/grounding/knowledge_base.json", encoding="utf-8") as f:
    kb = json.load(f)

missed = []
for rule in kb:
    r = client.post(
        "/ground",
        json={
            "category": rule["category"],
            "keywords": rule["keywords"][:6],
            "snippet": rule.get("example", ""),
        },
    )
    d = r.json()
    if not d.get("grounded") or d.get("rule_id") != rule["id"]:
        missed.append(rule["id"])

if missed:
    errors.append(f"FAIL  rules not matched via HTTP: {missed}")
else:
    print(f"PASS  all {len(kb)}/20 rules reachable via POST /ground")

# Summary
print()
if errors:
    print("FAILURES:")
    for e in errors:
        print(" ", e)
    raise SystemExit(1)
else:
    print("ALL SMOKE CHECKS PASSED")

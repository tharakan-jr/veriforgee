# 2-minute demo

## Demo input 1 — hardcoded secret

```python
DB_PASSWORD = "admin123"
```

Expected output:

- Critical
- Explain why source-controlled secrets are dangerous.
- Show evidence.
- Suggest an environment variable.
- Ask the user to verify the fix.

## Demo input 2 — SQL injection

```python
query = "SELECT * FROM users WHERE name='" + username + "'"
```

Expected output:

- High/Critical depending on context.
- Explain the attack in plain language.
- Recommend parameterized queries.
- Give a verification check.

## Demo story

1. “AI made generation easy.”
2. Paste bad AI-generated code.
3. Click **Review**.
4. Show the plain-English finding.
5. Expand authoritative evidence.
6. Apply the fix.
7. Pass the understanding check.
8. Show project health / comprehension metric.

Closing line:

> We are not only making AI better at generating artefacts; we are helping humans understand and take ownership of what AI generates.

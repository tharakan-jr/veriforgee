# Dataset & Grounding Notes

The VeriForge grounding layer uses a small, curated knowledge base of 20 high-confidence rules.
Each rule is sourced from a primary, publicly accessible authoritative document.
No citations are fabricated. Every URL was verified live before inclusion.

## Source Provenance Table

| Rule ID | Title | Source Name | URL | Licence | Category |
|---------|-------|-------------|-----|---------|----------|
| SEC-001 | Hardcoded Credentials | OWASP Top 10:2025 A07 | https://owasp.org/Top10/2025/A07_2025-Authentication_Failures/ | CC BY-SA 4.0 | secrets |
| SEC-002 | SQL Injection | OWASP Cheat Sheet — SQL Injection Prevention | https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html | CC BY-SA 4.0 | sql_injection |
| SEC-003 | Command Injection | OWASP Cheat Sheet — OS Command Injection Defense | https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html | CC BY-SA 4.0 | command_injection |
| SEC-004 | Cross-Site Scripting | OWASP Cheat Sheet — XSS Prevention | https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html | CC BY-SA 4.0 | xss |
| SEC-005 | Path Traversal | OWASP Cheat Sheet — Path Traversal | https://cheatsheetseries.owasp.org/cheatsheets/Path_Traversal_Cheat_Sheet.html | CC BY-SA 4.0 | path_traversal |
| SEC-006 | Missing Authentication | OWASP Cheat Sheet — Authentication | https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html | CC BY-SA 4.0 | missing_authentication |
| SEC-007 | Broken Authorization | OWASP Cheat Sheet — Authorization | https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html | CC BY-SA 4.0 | broken_authorization |
| SEC-008 | Insecure Password Storage | OWASP Cheat Sheet — Password Storage | https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html | CC BY-SA 4.0 | insecure_password_storage |
| SEC-009 | Sensitive Information Exposure | OWASP Cheat Sheet — Logging | https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html | CC BY-SA 4.0 | sensitive_information_exposure |
| SEC-010 | Security Misconfiguration | OWASP Top 10:2025 A02 | https://owasp.org/Top10/2025/A02_2025-Security_Misconfiguration/ | CC BY-SA 4.0 | security_misconfiguration |
| SEC-011 | Insecure Cryptography | OWASP Cheat Sheet — Cryptographic Storage | https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html | CC BY-SA 4.0 | insecure_cryptography |
| SEC-012 | Weak Session Management | OWASP Cheat Sheet — Session Management | https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html | CC BY-SA 4.0 | weak_session_management |
| SEC-013 | SSRF | OWASP Cheat Sheet — SSRF Prevention | https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html | CC BY-SA 4.0 | ssrf |
| SEC-014 | CSRF | OWASP Cheat Sheet — CSRF Prevention | https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html | CC BY-SA 4.0 | csrf |
| SEC-015 | Insecure Deserialization | OWASP Cheat Sheet — Deserialization | https://cheatsheetseries.owasp.org/cheatsheets/Deserialization_Cheat_Sheet.html | CC BY-SA 4.0 | insecure_deserialization |
| SEC-016 | Dangerous File Upload | OWASP Cheat Sheet — File Upload | https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html | CC BY-SA 4.0 | dangerous_file_upload |
| SEC-017 | Missing Rate Limiting | OWASP Cheat Sheet — Authentication (Automated Attacks) | https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html#protect-against-automated-attacks | CC BY-SA 4.0 | missing_rate_limiting |
| SEC-018 | Debug/Verbose Error Exposure | OWASP Top 10:2025 A02 | https://owasp.org/Top10/2025/A02_2025-Security_Misconfiguration/ | CC BY-SA 4.0 | debug_error_exposure |
| SEC-019 | Supply-Chain / Dependency Risk | OWASP Top 10:2025 A03 | https://owasp.org/Top10/2025/A03_2025-Software_Supply_Chain_Failures/ | CC BY-SA 4.0 | supply_chain |
| SEC-020 | Insecure Randomness | OWASP Cheat Sheet — Cryptographic Storage | https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html | CC BY-SA 4.0 | insecure_randomness |

## Dataset Tracking Fields

For each source above:

- **Source name**: documented in table
- **URL / identifier**: documented in table and in `knowledge_base.json`
- **Licence / usage terms**: OWASP content is licensed under Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)
- **Retrieval date**: 2026-09-03
- **Rule / finding categories covered**: all 20 listed above
- **How it is used**: read at startup by `app/grounding/grounder.py`; evidence statements are factual summaries of source content, not verbatim quotations presented as such

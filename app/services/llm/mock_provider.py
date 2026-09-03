import json
import re
import ast
from typing import List, Dict, Any
from app.services.llm.base import LLMProvider


class MockLLMProvider(LLMProvider):
    """
    Mock LLM provider that analyzes inputs using deterministic heuristics
    and returns valid JSON payload conforming to the Finding schema structure.
    Used for unit testing, offline development, and zero-dependency default operation.
    """

    async def generate_remediation(self, code: str, finding_title: str, language: str = "python") -> str:
        """Generate a deterministic, changed remediation for supported findings."""
        title = finding_title.lower()

        if "credential" in title or "secret" in title or "password" in title:
            credential_pattern = re.compile(
                r"(?im)^(\s*)(api_key|secret|password|token)\s*=\s*([\"'])[^\"']+\3\s*$"
            )

            def replace_credential(match: re.Match[str]) -> str:
                variable_name = match.group(2)
                return f'{match.group(1)}{variable_name} = os.environ["{variable_name.upper()}"]'

            fixed_code = credential_pattern.sub(replace_credential, code)
            if fixed_code != code:
                if not re.search(r"(?m)^\s*import\s+os\b", fixed_code):
                    fixed_code = f"import os\n\n{fixed_code}"
                return fixed_code

        if "unsafe code execution" in title or "eval" in title or "exec" in title:
            fixed_code = re.sub(r"\beval\s*\(([^\n()]*)\)", r"parse_explicit_operation(\1)", code)
            fixed_code = re.sub(
                r"\bexec\s*\([^\n()]*\)",
                'raise ValueError("Arbitrary code execution is not allowed")',
                fixed_code,
            )
            if fixed_code != code:
                return fixed_code

        if "bare exception" in title or "except" in title:
            fixed_code = re.sub(r"(?m)^(\s*)except\s*:", r"\1except Exception as exc:", code)
            fixed_code = re.sub(
                r"(?m)^(\s*)except Exception as exc:\n\1    pass\s*$",
                r'\1except Exception as exc:\n\1    print(f"Operation failed: {exc}")',
                fixed_code,
            )
            if fixed_code != code:
                return fixed_code

        if "sql injection" in title or "sql_injection" in title:
            query_assignment = re.compile(
                r"(?m)^(?P<indent>\s*)(?P<name>[A-Za-z_]\w*)\s*=\s*(?P<expression>.+)$"
            )
            string_token = r'''(?:'[\s\S]*?(?<!\\)'|"[\s\S]*?(?<!\\)")'''

            for match in query_assignment.finditer(code):
                expression = match.group("expression").strip()
                if not re.search(r"(?i)\b(select|insert|update|delete)\b", expression):
                    continue
                if "+" not in expression:
                    continue

                terms = re.split(r"\s*\+\s*", expression)
                if len(terms) < 2:
                    continue

                sql_parts: List[str] = []
                parameters: List[str] = []
                valid_expression = True
                parameter_boundary = False
                for term in terms:
                    term = term.strip()
                    if re.fullmatch(string_token, term, re.DOTALL):
                        try:
                            literal_value = str(ast.literal_eval(term))
                            if parameter_boundary and literal_value[:1] in {"'", '"'}:
                                literal_value = literal_value[1:]
                            sql_parts.append(literal_value)
                            parameter_boundary = False
                        except (SyntaxError, ValueError):
                            valid_expression = False
                            break
                    elif re.fullmatch(r"[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*", term):
                        if sql_parts and sql_parts[-1][-1:] in {"'", '"'}:
                            sql_parts[-1] = sql_parts[-1][:-1]
                        sql_parts.append("?")
                        parameters.append(term)
                        parameter_boundary = True
                    else:
                        valid_expression = False
                        break

                if not valid_expression or not parameters:
                    continue

                query_name = match.group("name")
                execute_pattern = re.compile(
                    rf"(?P<prefix>\.execute\(\s*{re.escape(query_name)})(?P<suffix>\s*\))"
                )
                execute_match = execute_pattern.search(code, match.end())
                if not execute_match:
                    continue

                fixed_query = "".join(sql_parts)
                parameter_tuple = f"({', '.join(parameters)}{',' if len(parameters) == 1 else ''})"
                replacement_query = f'{match.group("indent")}{query_name} = {json.dumps(fixed_query)}'
                fixed_code = (
                    code[:match.start()]
                    + replacement_query
                    + code[match.end():]
                )
                adjusted_execute_start = execute_match.start() + len(replacement_query) - (match.end() - match.start())
                adjusted_execute_end = execute_match.end() + len(replacement_query) - (match.end() - match.start())
                execute_text = fixed_code[adjusted_execute_start:adjusted_execute_end]
                fixed_code = (
                    fixed_code[:adjusted_execute_start]
                    + execute_text[:-1]
                    + f", {parameter_tuple})"
                    + fixed_code[adjusted_execute_end:]
                )
                if fixed_code != code:
                    return fixed_code

            return code

        raise ValueError(f"No deterministic remediation available for finding: {finding_title}")

    async def generate(self, prompt: str, system_prompt: str) -> str:
        code_match = re.search(r"<untrusted_user_code_to_review>\n(.*?)\n</untrusted_user_code_to_review>", prompt, re.DOTALL)
        code = code_match.group(1) if code_match else prompt
        lines = code.splitlines()
        findings: List[Dict[str, Any]] = []

        # Check 1: Hardcoded credentials or secrets
        cred_line = 1
        cred_found = False
        for idx, line in enumerate(lines, start=1):
            if re.search(r'(?i)(api_key|secret|password|token)\s*=\s*["\'][^"\']+["\']', line):
                cred_line = idx
                cred_found = True
                break
        if not cred_found and re.search(r'(?i)(api_key|secret|password|token)\s*=\s*["\'][^"\']+["\']', code):
            cred_found = True

        if cred_found:
            findings.append({
                "severity": "critical",
                "title": "Hardcoded credential",
                "category": "security",
                "description": "A credential or secret appears to be stored directly in source code.",
                "location": f"line {cred_line}",
                "why_it_matters": "Anyone who gains access to the source repository may obtain the secret credential.",
                "recommendation": "Move the credential into an environment variable or appropriate secret manager.",
                "verification_question": "Why is storing a credential directly in source code risky?"
            })

        # Check 2: Unsafe execution (eval/exec)
        eval_line = 1
        eval_found = False
        for idx, line in enumerate(lines, start=1):
            if re.search(r'\b(eval|exec)\s*\(', line):
                eval_line = idx
                eval_found = True
                break
        if not eval_found and re.search(r'\b(eval|exec)\s*\(', code):
            eval_found = True

        if eval_found:
            findings.append({
                "severity": "high",
                "title": "Unsafe code execution",
                "category": "security",
                "description": "Direct use of dynamic execution functions like eval() or exec().",
                "location": f"line {eval_line}",
                "why_it_matters": "Executing dynamic code string input can allow arbitrary remote code execution.",
                "recommendation": "Replace dynamic execution with safe parsing or predefined logic dispatchers.",
                "verification_question": "What security risk does calling eval() on untrusted input introduce?"
            })

        # Check 3: Bare exception handling (except:)
        except_line = 1
        except_found = False
        for idx, line in enumerate(lines, start=1):
            if re.search(r'except\s*:', line):
                except_line = idx
                except_found = True
                break
        if not except_found and re.search(r'except\s*:', code):
            except_found = True

        if except_found:
            findings.append({
                "severity": "medium",
                "title": "Bare exception handling",
                "category": "maintainability",
                "description": "Catching all exceptions blindly without specifying the exception type.",
                "location": f"line {except_line}",
                "why_it_matters": "Bare exception blocks mask unexpected errors like SystemExit, KeyboardInterrupt, or typos.",
                "recommendation": "Specify the concrete exception type (e.g., except ValueError:).",
                "verification_question": "Why is catching generic exceptions without filtering problematic during debugging?"
            })

        # Check 4: SQL query construction through string concatenation
        sql_line = 1
        sql_injection_found = False
        for idx, line in enumerate(lines, start=1):
            if re.search(r"(?i)\b(select|insert|update|delete)\b.*\+", line):
                sql_line = idx
                sql_injection_found = True
                break

        if sql_injection_found:
            findings.append({
                "severity": "high",
                "title": "SQL injection",
                "category": "sql_injection",
                "description": "Untrusted input is concatenated directly into a SQL query.",
                "location": f"line {sql_line}",
                "why_it_matters": "An attacker may alter the query and read, change, or delete database data.",
                "recommendation": "Use parameterized queries with bound values instead of string concatenation.",
                "verification_question": "Why do parameterized queries prevent user input from changing SQL structure?"
            })


        # Fallback check if code seems clean or simple
        if not findings:
            findings.append({
                "severity": "info",
                "title": "Code structure looks clear",
                "category": "general",
                "description": "No critical vulnerabilities or obvious code smells were detected in this snippet.",
                "location": "global",
                "why_it_matters": "Clean code is easier to maintain and lowers potential defect rates.",
                "recommendation": "Ensure automated test coverage exists for all edge cases.",
                "verification_question": "What is the primary benefit of maintaining unit test coverage for clean code?"
            })

        response_payload = {
            "summary": f"Identified {len(findings)} potential finding(s).",
            "findings": findings
        }

        return json.dumps(response_payload)

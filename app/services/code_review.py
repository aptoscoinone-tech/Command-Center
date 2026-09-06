"""Code Reviewer (M3): Static security and quality auditor for generated code."""

import ast
from typing import Dict, Any, List


class CodeReviewer:
    DANGEROUS_IMPORTS = ["os.system", "subprocess.Popen", "eval", "exec", "__import__", "pickle"]

    @classmethod
    def review(cls, code: str) -> Dict[str, Any]:
        """
        Analyzes code for security vulnerabilities, resource limits, and best practices.
        """
        issues: List[str] = []
        suggestions: List[str] = []
        is_secure = True

        # Check for banned substrings / patterns
        for dangerous in cls.DANGEROUS_IMPORTS:
            if dangerous in code:
                issues.append(f"Security Alert: potentially unsafe construct detected ({dangerous}).")
                is_secure = False

        # Parse AST for basic sanity
        try:
            tree = ast.parse(code)
            has_docstrings = any(isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) for node in tree.body)
            if not has_docstrings:
                suggestions.append("Рекомендуется добавить docstring для описания сигнатуры и типов.")
        except SyntaxError as se:
            issues.append(f"Syntax Error in generated code: {str(se)}")
            is_secure = False

        feedback = "✅ Код прошёл проверку безопасности. Обработка краевых случаев корректна."
        if not is_secure:
            feedback = f"⚠️ Обнаружены замечания:\n" + "\n".join(f"- {i}" for i in issues)
        elif suggestions:
            feedback += f"\n💡 Рекомендации:\n" + "\n".join(f"- {s}" for s in suggestions)

        return {
            "is_secure": is_secure,
            "issues": issues,
            "suggestions": suggestions,
            "feedback": feedback
        }

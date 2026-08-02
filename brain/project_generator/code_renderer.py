from typing import Any


class CodeRenderer:
    def render(self, template_content: str, variables: dict[str, Any]) -> str:
        content = template_content
        # Deterministic simple replacement
        for key, value in variables.items():
            placeholder = f"{{{{{key}}}}}"
            content = content.replace(placeholder, str(value))
        return content

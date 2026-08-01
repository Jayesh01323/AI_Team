from typing import Dict, Any

class CodeRenderer:
    def render(self, template_content: str, variables: Dict[str, Any]) -> str:
        content = template_content
        # Deterministic simple replacement
        for key, value in variables.items():
            placeholder = f"{{{{{key}}}}}"
            content = content.replace(placeholder, str(value))
        return content

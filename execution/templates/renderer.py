import re
from pathlib import Path

from core.exceptions import TemplateRenderError
from execution.repository.filesystem import FileSystem

# Matches ${braced} variable placeholders only — NOT bare $name references
# so that template files can safely contain patterns like *$py.class.
_BRACED_VAR = re.compile(r"\$\{(\w+)\}")

# Pattern to detect unresolved ${variable} placeholders in rendered output
_UNRESOLVED_PATTERN = re.compile(r"\$\{[a-zA-Z_][a-zA-Z0-9_]*\}")


class TemplateRenderer:
    def __init__(self, fs: FileSystem):
        self.fs = fs

    def render_to_string(self, template_content: str, variables: dict) -> str:
        """Renders using ``${braced}`` variable substitution only.

        Bare ``$name`` references (without braces) are left untouched so
        that template files can safely contain patterns like ``*$py.class``.

        Raises:
            TemplateRenderError: If a required ``${variable}`` is missing
                or unresolved placeholders remain after substitution.
        """

        def repl(match):
            var_name = match.group(1)
            if var_name not in variables:
                raise KeyError(var_name)
            return str(variables[var_name])

        try:
            rendered = re.sub(r"\$\{([a-zA-Z_][a-zA-Z0-9_]*)\}", repl, template_content)
        except KeyError as e:
            raise TemplateRenderError(
                f"Template rendering failed — missing variable: '{e.args[0]}'"
            ) from e

        # Belt-and-suspenders: catch any unresolved ${...} placeholders
        unresolved = _UNRESOLVED_PATTERN.findall(rendered)
        if unresolved:
            raise TemplateRenderError(
                f"Template rendering left unresolved placeholders: {unresolved}"
            )

        return rendered

    def render_to_file(
        self,
        template_path: Path,
        dest_rel_path: str,
        variables: dict,
        overwrite: bool = True,
    ) -> Path:
        content = template_path.read_text(encoding="utf-8")
        rendered = self.render_to_string(content, variables)
        return self.fs.write_file(dest_rel_path, rendered, overwrite=overwrite)

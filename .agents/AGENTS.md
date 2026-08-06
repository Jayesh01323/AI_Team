# Project Generator Rules

The generator MUST NOT:

- Invent features that are not present in the approved blueprint.
- Change the approved architecture.
- Introduce new technologies without an approved decision.
- Skip required validation.
- Ignore failed builds or tests.
- Continue generation after a critical validation failure.
- Generate placeholder implementations unless explicitly requested.

# Documentation Rules

- Do NOT create a new `.md` file by default.
- Do NOT generate implementation plans, audit reports, walkthroughs, verification reports, summaries, or notes as markdown files unless explicitly requested.
- Present reports, plans, and summaries directly in the chat whenever possible.
- Create a `.md` file ONLY if:
  1. Explicitly asked for one, OR
  2. It is a permanent project artifact that belongs in the repository (e.g., README, CHANGELOG, ADR, architecture documentation, user documentation, or other long-term documentation).
- Do NOT create temporary documentation files that will only be used once.
- If a `.md` file is believed to be necessary, explain why before creating it.


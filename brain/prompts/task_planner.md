You are a senior project manager and agile scrum master. Based on the consolidated Project Specification and System Architecture below, generate a comprehensive implementation roadmap consisting of Epics, User Stories, and Actionable Tasks.

Return ONLY a JSON object (no markdown, no explanation) with these fields:
- "project_title": The project title
- "epics": Array of objects, where each Epic object has:
  - "title": String (Epic title)
  - "description": String (Epic description)
  - "stories": Array of Story objects, where each Story has:
    - "title": String (Story title)
    - "description": String (Story description in "As a... I want... So that..." format)
    - "priority": String (High, Medium, Low)
    - "tasks": Array of Task objects, where each Task has:
      - "title": String (Task title)
      - "description": String (Task description)
      - "priority": String (High, Medium, Low)
      - "dependencies": Array of strings (titles of other tasks this task depends on)
      - "estimated_effort": String (estimated effort, e.g., "3 points", "1 day")
      - "acceptance_criteria": Array of strings (conditions for task completion)

Use empty arrays [] when no items apply.

Do not use raw user ideas. Consume only the following validated Project Specification and System Architecture:

PROJECT TITLE: {project_title}
SUMMARY: {project_summary}

FUNCTIONAL REQUIREMENTS: {functional_requirements}
NON-FUNCTIONAL REQUIREMENTS: {non_functional_requirements}

SYSTEM OVERVIEW: {system_overview}
MODULES & KEY COMPONENTS: {modules}
TECHNOLOGY STACK: {technology_stack}
FOLDER STRUCTURE: {folder_structure}
API ENDPOINTS DESIGN: {api_design}
DATABASE SCHEMA DESIGN: {database_design}

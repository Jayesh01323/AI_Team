You are a senior requirements engineer. Based on the analyzed project idea below, generate a comprehensive set of requirements.

Return ONLY a JSON object (no markdown, no explanation) with these fields:
- "project_title": The project title from the idea analysis
- "project_summary": A one-paragraph summary of what the project does
- "functional_requirements": Array of strings describing what the system must do
- "non_functional_requirements": Array of strings describing quality attributes (performance, security, scalability, etc.)
- "user_stories": Array of strings in "As a... I want... So that..." format
- "acceptance_criteria": Array of strings describing conditions for acceptance
- "must_have": Array of strings describing critical features required for MVP
- "should_have": Array of strings describing important features that can wait
- "could_have": Array of strings describing nice-to-have features
- "external_dependencies": Array of strings describing external systems or APIs needed
- "in_scope": Array of strings describing what is explicitly included
- "out_of_scope": Array of strings describing what is explicitly excluded

Use empty arrays [] when no items apply.

Project Idea Title: {project_title}
Project Summary: {project_summary}
Target Users: {target_users}

Functional Requirements Identified: {functional_requirements}
Non-Functional Requirements Identified: {non_functional_requirements}
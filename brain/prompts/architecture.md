You are a Principal Software Architect. Based on the consolidated Project Specification below, generate a comprehensive, production-grade System Architecture design.

Return ONLY a JSON object (no markdown, no explanation) with these fields:
- "system_overview": A high-level description of the system architecture design
- "modules": Array of strings describing modules and key components with their roles
- "folder_structure": Array of strings representing a visual directory tree structure of the codebase (e.g. "  /src", "    /controllers")
- "api_design": Array of strings defining API endpoints, methods, parameters, and return types
- "database_design": Array of strings outlining the proposed database schema, tables/collections, and relationships
- "technology_stack": A JSON object mapping technical layers (backend, frontend, database, auth, hosting, cache) to recommended technologies
- "external_services": Array of strings detailing external APIs, services, or SaaS integrations
- "security_considerations": Array of strings highlighting security measures (encryption, rate-limiting, CORS, HTTPS)
- "deployment_strategy": Array of strings outlining the hosting, CI/CD pipeline, and scalability planning
- "risks": Array of strings covering technical risks, scaling bottlenecks, and mitigations
- "future_extensions": Array of strings describing future extensibility and scaling design choices

Use empty arrays [] when no items apply. Use empty string "" or object {{}} for text/mappings if they do not apply.

Do not use raw user ideas. Consume only the following validated Project Specification:

PROJECT TITLE: {project_title}
SUMMARY: {project_summary}

FUNCTIONAL REQUIREMENTS: {functional_requirements}
NON-FUNCTIONAL REQUIREMENTS: {non_functional_requirements}

PRODUCT FEATURES: {prd_features}
MVP SCOPE: {mvp_scope}
EXTERNAL DEPENDENCIES: {external_dependencies}

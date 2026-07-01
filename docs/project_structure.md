# Project Structure

This document details the file and folder layout of the AI Multi-Agent Research Writer workspace, outlining where backend components, frontend files, tests, and configuration assets reside.

---

## Workspace Root Layout

The root folder contains orchestration configs, dependencies, containerization definitions, and root documentation files:

*   **[Dockerfile](file:///C:/Users/Shivangi/Desktop/Multi-Agent%20Research%20writer/Dockerfile)**: Docker instructions defining the build env, installing system and Python requirements, and running the FastAPI backend.
*   **[docker-compose.yml](file:///C:/Users/Shivangi/Desktop/Multi-Agent%20Research%20writer/docker-compose.yml)**: Multi-container configuration for backend (FastAPI) and frontend (Streamlit) services, linking network communication and database volumes.
*   **[pyproject.toml](file:///C:/Users/Shivangi/Desktop/Multi-Agent%20Research%20writer/pyproject.toml)**: Project configuration defining tool preferences for Ruff (formatter/linter) and Pytest (test suite options).
*   **[requirements.txt](file:///C:/Users/Shivangi/Desktop/Multi-Agent%20Research%20writer/requirements.txt)**: Python package list specifying required dependencies.
*   **[README.md](file:///C:/Users/Shivangi/Desktop/Multi-Agent%20Research%20writer/README.md)**: Main landing documentation for the project.
*   **[docs/](file:///C:/Users/Shivangi/Desktop/Multi-Agent%20Research%20writer/docs)**: Documentation directory housing detailed implementation references.

---

## Backend Directory `backend/`

The [backend](file:///C:/Users/Shivangi/Desktop/Multi-Agent%20Research%20writer/backend) codebase follows clean software design principles:

*   **[main.py](file:///C:/Users/Shivangi/Desktop/Multi-Agent%20Research%20writer/backend/main.py)**: The FastAPI server entry point. Configures CORS, sets up middlewares, configures the base routes, and mounts the asynchronous lifespan startup check handler.
*   **`api/`**: Exposes HTTP routing paths and schemas.
    *   **[routes.py](file:///C:/Users/Shivangi/Desktop/Multi-Agent%20Research%20writer/backend/api/routes.py)**: Defines root router, health checks, and research request/response execution routes.
*   **`core/`**: Core configuration settings and logging setups.
    *   **[config.py](file:///C:/Users/Shivangi/Desktop/Multi-Agent%20Research%20writer/backend/core/config.py)**: Manages Pydantic configuration settings, validation of ports/URLs, and default environment fallbacks.
    *   **[logger.py](file:///C:/Users/Shivangi/Desktop/Multi-Agent%20Research%20writer/backend/core/logger.py)**: Configures a semi-structured standard logging utility outputting format logs to stdout.
    *   **[startup_validation.py](file:///C:/Users/Shivangi/Desktop/Multi-Agent%20Research%20writer/backend/core/startup_validation.py)**: Checks write permissions and Ollama connectivity at application start.
*   **`agents/`**: Core LangGraph agent constructors.
    *   **[planner_agent.py](file:///C:/Users/Shivangi/Desktop/Multi-Agent%20Research%20writer/backend/agents/planner_agent.py)**: Drafts structured outline sections.
    *   **[research_agent.py](file:///C:/Users/Shivangi/Desktop/Multi-Agent%20Research%20writer/backend/agents/research_agent.py)**: Orchestrates retrieval flows from Search and Memory.
    *   **[writer_agent.py](file:///C:/Users/Shivangi/Desktop/Multi-Agent%20Research%20writer/backend/agents/writer_agent.py)**: Generates the draft chapters.
    *   **[reviewer_agent.py](file:///C:/Users/Shivangi/Desktop/Multi-Agent%20Research%20writer/backend/agents/reviewer_agent.py)**: Examines sections and returns feedback comments.
    *   **[editor_agent.py](file:///C:/Users/Shivangi/Desktop/Multi-Agent%20Research%20writer/backend/agents/editor_agent.py)**: Applies suggestions and cleans formatting.
*   **`workflows/`**: LangGraph workflow assembly.
    *   **[research_workflow.py](file:///C:/Users/Shivangi/Desktop/Multi-Agent%20Research%20writer/backend/workflows/research_workflow.py)**: Chains all agents together in a graph layout.
*   **`models/`**: Client structures and state wrappers.
    *   **[ollama_client.py](file:///C:/Users/Shivangi/Desktop/Multi-Agent%20Research%20writer/backend/models/ollama_client.py)**: Low-level client managing API request loops, retries, exponential backoffs, and stream generation to the Ollama server.
*   **`memory/`**: RAG storage logic.
    *   **[memory_service.py](file:///C:/Users/Shivangi/Desktop/Multi-Agent%20Research%20writer/backend/memory/memory_service.py)**: Wraps ChromaDB PersistentClient, handles embeddings mapping, document storage, and vector searching.
*   **`search/`**: Web search integration.
    *   **[search_service.py](file:///C:/Users/Shivangi/Desktop/Multi-Agent%20Research%20writer/backend/search/search_service.py)**: Wraps DuckDuckGo search API to pull live snippets.
*   **`utils/`**: Utility code.
    *   **[export_service.py](file:///C:/Users/Shivangi/Desktop/Multi-Agent%20Research%20writer/backend/utils/export_service.py)**: Handles converting raw Markdown to PDF using ReportLab and DOCX using python-docx.

---

## Frontend Directory `frontend/`

The Streamlit code resides in:

*   **[app.py](file:///C:/Users/Shivangi/Desktop/Multi-Agent%20Research%20writer/frontend/app.py)**: Renders the sidebar inputs, connection status checks, dynamic research logs, and markdown output downloads.

---

## Tests Directory `tests/`

The test suite provides comprehensive test coverage:

*   **[conftest.py](file:///C:/Users/Shivangi/Desktop/Multi-Agent%20Research%20writer/tests/conftest.py)**: Set up global session-level mocks for Ollama, AI Service, and network sockets to ensure fast, offline execution.
*   **[test_api.py](file:///C:/Users/Shivangi/Desktop/Multi-Agent%20Research%20writer/tests/test_api.py)**: Validates api routes.
*   **[test_production.py](file:///C:/Users/Shivangi/Desktop/Multi-Agent%20Research%20writer/tests/test_production.py)**: Asserts production validation rules (config validation, startup error checks, compose file formatting).
*   **[test_optimization.py](file:///C:/Users/Shivangi/Desktop/Multi-Agent%20Research%20writer/tests/test_optimization.py)**: Asserts Phase 14B optimizations (lazy connection client check, cached startup validation, singleton status checks).
*   **Individual Agent Tests**: (`test_planner_agent.py`, `test_research_agent.py`, etc.) assert unit-level agent behaviors.

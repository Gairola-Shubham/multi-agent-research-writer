# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.2.0] - 2026-07-01

### Added
*   New system optimization tests inside [test_optimization.py](file:///C:/Users/Shivangi/Desktop/Multi-Agent%20Research%20writer/tests/test_optimization.py).
*   Detailed project documentation in `docs/`:
    *   [architecture.md](file:///C:/Users/Shivangi/Desktop/Multi-Agent%20Research%20writer/docs/architecture.md)
    *   [project_structure.md](file:///C:/Users/Shivangi/Desktop/Multi-Agent%20Research%20writer/docs/project_structure.md)
    *   [api_reference.md](file:///C:/Users/Shivangi/Desktop/Multi-Agent%20Research%20writer/docs/api_reference.md)
    *   [setup.md](file:///C:/Users/Shivangi%20Research%20writer/docs/setup.md)
    *   [screenshots.md](file:///C:/Users/Shivangi/Desktop/Multi-Agent%20Research%20writer/docs/screenshots.md)
    *   [release_checklist.md](file:///C:/Users/Shivangi/Desktop/Multi-Agent%20Research%20writer/docs/release_checklist.md)
*   GitHub Actions CI workflow definition inside `.github/workflows/ci.yml`.
*   Standard open-source files: `LICENSE` (MIT), `CONTRIBUTING.md`, and `CHANGELOG.md`.

### Changed
*   **Lazy Initialization**: Modified `OllamaClient` in [ollama_client.py](file:///C:/Users/Shivangi/Desktop/Multi-Agent%20Research%20writer/backend/models/ollama_client.py) to run model checks and connection checks lazily, preventing application import blockages.
*   **Startup Verification Guard**: Added an execution guard in [startup_validation.py](file:///C:/Users/Shivangi/Desktop/Multi-Agent%20Research%20writer/backend/core/startup_validation.py) to prevent duplicate verification runs on reloads/test executions.
*   **Healthcheck Optimizations**: Refactored the `/health` route in [routes.py](file:///C:/Users/Shivangi/Desktop/Multi-Agent%20Research%20writer/backend/api/routes.py) to reuse singleton service instances from the global LangGraph workflow object, eliminating redundant connections.
*   **Resilience & Exception Logs**: Updated exception catching across healthchecks to output standard warning logs, preserving error details for maintenance.

---

## [0.1.0] - 2026-07-01

### Added
*   Initial release of the AI Multi-Agent Research Writer.
*   Multi-agent research coordination workflow implemented in LangGraph.
*   Specialized agents: `PlannerAgent`, `ResearchAgent`, `WriterAgent`, `ReviewerAgent`, and `EditorAgent`.
*   ChromaDB (RAG) persistent vector storage.
*   DuckDuckGo search scraper tool integration.
*   FastAPI backend routing with asynchronous endpoints.
*   Streamlit user dashboard UI.
*   PDF and Word document exporter engines.
*   Docker and Docker Compose setup configurations.

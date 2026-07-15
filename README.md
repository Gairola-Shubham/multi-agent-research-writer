# AI Multi-Agent Research Writer

An autonomous, multi-agent AI research and report generation platform designed to conduct extensive web research, analyze scientific and domain data, structure a comprehensive report, and output a publication-ready PDF.

Powered by **Python 3.12, FastAPI, Streamlit, Ollama, LangGraph, ChromaDB, and DuckDuckGo Search**, this tool simulates a collaborative team of professional researchers, writers, and editors to produce high-fidelity academic or industry research reports locally and with zero API costs.

For detailed architecture details, see [docs/architecture.md](file:///C:/Users/Shivangi/Desktop/Multi-Agent%20Research%20writer/docs/architecture.md).

---

## Features

- **Multi-Agent Research Pipeline**: Designed using LangGraph to orchestrate a team of specialized agents:
  - **Research Lead**: Plans and coordinates research tracks.
  - **Web Researcher**: Employs DuckDuckGo search to retrieve, filter, and extract high-signal info.
  - **Domain Analyst**: Structures and synthesizes information, populating a vector database (ChromaDB) for retrieval.
  - **Writer & Editor**: Drafts academic-grade text and refines it for style, flow, and coherence.
  - **Publisher**: Combines chapters/sections and compiles formatted files.
- **Local-First Execution**: Fully integrated with Ollama for offline LLM inference, ensuring data privacy.
- **FastAPI Backend**: Robust asynchronous API service to trigger research tasks, track progress, and serve health check logs.
- **Streamlit Frontend**: An interactive user interface allowing users to prompt research, view real-time logs, and download reports.
- **Persistent Knowledge Graph**: ChromaDB integration for RAG (Retrieval-Augmented Generation) ensuring factual consistency across long reports.
- **Dynamic File Compilation**: Auto-generates structured PDF and Microsoft Word DOCX formats of the generated research.

---

## Technology Stack

*   **Core Logic**: Python 3.12
*   **Web API Framework**: FastAPI
*   **User Interface**: Streamlit
*   **Agent Workflow Engine**: LangGraph
*   **Local LLM Service**: Ollama (optimized for phi3:latest model)
*   **Vector Database (RAG)**: ChromaDB
*   **Web Scraping / Crawling**: DuckDuckGo Search API (`duckduckgo-search`)
*   **Document Generation Utilities**: ReportLab (PDF), python-docx (DOCX)
*   **Testing Suite**: Pytest (fully mocked for offline testing)

---

## Project Structure

A clean separation of concerns is maintained across frontend, backend, test suite, and configurations. For a complete directory reference, see [docs/project_structure.md](file:///C:/Users/Shivangi/Desktop/Multi-Agent%20Research%20writer/docs/project_structure.md).

*   `backend/` - API endpoints, settings, agents, memory, search services, and document utilities.
*   `frontend/` - Streamlit UI application setup.
*   `tests/` - Unit, integration, production validation, and system optimization test files.
*   `docs/` - Architectural flowcharts, setup tutorials, and API reference sheets.

---

## Installation & Setup

For a step-by-step setup walkthrough, please refer to [docs/setup.md](file:///C:/Users/Shivangi/Desktop/Multi-Agent%20Research%20writer/docs/setup.md).

### 1. Prerequisites
Ensure you have installed Python 3.12, Git, and Ollama.

### 2. Virtual Environment and Dependencies
```bash
python -m venv .venv
# Activate: On Windows: .venv\Scripts\activate | On macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Environment Variables
Copy `.env.example` to `.env` and verify configurations:
```bash
cp .env.example .env
```

### 4. Ollama Setup
Pull the default model:
```bash
ollama pull phi3:latest
```

---

## How to Run

### Running Locally

1.  **Start the FastAPI Backend**:
    ```bash
    uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
    ```
2.  **Start the Streamlit Frontend**:
    ```bash
    streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0
    ```

### Running with Docker

Run the multi-container configuration using Docker Compose:
```bash
docker-compose up --build
```
Access the application at [http://localhost:8501](http://localhost:8501) and API docs at [http://localhost:8000/docs](http://localhost:8000/docs).

---

## Usage Guide

1.  Open the Streamlit UI at `http://localhost:8501`.
2.  Enter your **Research Topic** (e.g., *Impact of quantum computing on modern cryptography*).
3.  Specify a custom **Style Guide** (e.g., *IEEE format* or *Chicago manual of style*).
4.  Choose your **Research Depth** (Standard, Detailed, or Brief).
5.  Click **Start Research Pipeline**. The UI will stream execution logs from each agent node in real-time.
6.  Once finalized, read the compiled report in the UI or download the **PDF** and **Word (DOCX)** document exports.

---

## Screenshots

Placeholder UI representations can be reviewed in [docs/screenshots.md](file:///C:/Users/Shivangi/Desktop/Multi-Agent%20Research%20writer/docs/screenshots.md).

---

## Architecture Overview

Detailed descriptions of individual system components and pipeline layouts can be reviewed in [docs/architecture.md](file:///C:/Users/Shivangi/Desktop/Multi-Agent%20Research%20writer/docs/architecture.md).

### LangGraph Workflow Overview
Chains sequential processing nodes:
1.  `PlannerNode` -> 2. `ResearchNode` -> 3. `WriterNode` -> 4. `ReviewerNode` -> 5. `EditorNode`.

### Agent Descriptions
*   [PlannerAgent](file:///C:/Users/Shivangi/Desktop/Multi-Agent%20Research%20writer/backend/agents/planner_agent.py): Uses the LLM to structure outline sections based on depth.
*   [ResearchAgent](file:///C:/Users/Shivangi/Desktop/Multi-Agent%20Research%20writer/backend/agents/research_agent.py): Runs web search queries and vector database lookups to aggregate raw data.
*   [WriterAgent](file:///C:/Users/Shivangi/Desktop/Multi-Agent%20Research%20writer/backend/agents/writer_agent.py): Synthesizes aggregated findings into cohesive Markdown chapters.
*   [ReviewerAgent](file:///C:/Users/Shivangi/Desktop/Multi-Agent%20Research%20writer/backend/agents/reviewer_agent.py): Audits spelling, grammar, readability, and style guide compliance.
*   [EditorAgent](file:///C:/Users/Shivangi/Desktop/Multi-Agent%20Research%20writer/backend/agents/editor_agent.py): Polishes formatting and resolves reviewer feedback before compilation.

---

## API Overview

The backend API details are fully covered in [docs/api_reference.md](file:///C:/Users/Shivangi/Desktop/Multi-Agent%20Research%20writer/docs/api_reference.md).

*   `GET /`: Status check page.
*   `GET /health`: Comprehensive component health diagnostic reporting.
*   `POST /research`: Submits research tasks and returns final markdown.

---

## Core Services Integration

### Search Integration
Uses [SearchService](file:///C:/Users/Shivangi/Desktop/Multi-Agent%20Research%20writer/backend/search/search_service.py) to run queries on DuckDuckGo, filtering out irrelevant snippets and passing high-signal title/URL/content structures to the researcher agent.

### ChromaDB (RAG) Integration
Uses [MemoryService](file:///C:/Users/Shivangi/Desktop/Multi-Agent%20Research%20writer/backend/memory/memory_service.py) to store section outputs and retrieve historical summaries, preventing text duplication and keeping information factually correct across sections.

### Export Functionality
Uses [ExportService](file:///C:/Users/Shivangi/Desktop/Multi-Agent%20Research%20writer/backend/utils/export_service.py) to compile generated Markdown dynamically to clean PDF formats (via ReportLab flowables) and structured Word DOCX files (via python-docx elements).

---

## Testing Instructions

The codebase includes integration, production readiness, and component optimization test suites:

Run the entire test suite locally:
```bash
python -m pytest
```

The test suite requires no active connections to Ollama, ChromaDB, or the internet, as all external calls are mocked in [conftest.py](file:///C:/Users/Shivangi/Desktop/Multi-Agent%20Research%20writer/tests/conftest.py).

---

## Troubleshooting

*   **Ollama Connection Failure**: Ensure the Ollama app is running locally. Check `ollama serve` output and double check that port `11434` is not blocked.
*   **Docker Container Connection Issues**: If the Docker backend cannot reach the host's Ollama instance, ensure `OLLAMA_BASE_URL` in `.env` is set to `http://host.docker.internal:11434` instead of `http://localhost:11434`.
*   **Write Permission Failures**: If startup checks crash indicating ChromaDB paths or temp directories are not writable, run with elevated shell privileges or adjust folder access configurations.

---

## Future Improvements

1.  **Multi-source knowledge retrieval**: Add ArXiv, Google Scholar, PubMed, and custom file PDF uploads.
2.  **Custom model providers**: Add support for cloud endpoints (OpenAI, Anthropic, Gemini).
3.  **Human-in-the-loop validation**: Add options for users to modify the generated outline or review notes before final document draft synthesis.
4.  **Collab spaces**: Support multi-user workspaces and joint research sessions.

---

## License

Distributed under the MIT License. See [LICENSE](file:///C:/Users/Shivangi/Desktop/Multi-Agent%20Research%20writer/LICENSE) for more information.

---

## Author

Created by Gairola Shubham and contributors.
For issues or feature requests, submit a ticket on the GitHub Repository.

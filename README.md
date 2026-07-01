# AI Multi-Agent Research Writer

An autonomous, multi-agent AI research and report generation platform designed to conduct extensive web research, analyze scientific and domain data, structure a comprehensive report, and output a publication-ready PDF.

Powered by **Python 3.12, FastAPI, Streamlit, Ollama, LangGraph, ChromaDB, and DuckDuckGo Search**, this tool simulates a collaborative team of professional researchers, writers, and editors to produce high-fidelity academic or industry research reports.

---

## Features

- **Multi-Agent Research Pipeline**: Designed using LangGraph to orchestrate a team of specialized agents:
  - **Research Lead**: Plans and coordinates research tracks.
  - **Web Researcher**: Employs DuckDuckGo search to retrieve, filter, and extract high-signal info.
  - **Domain Analyst**: Structures and synthesizes information, populating a vector database (ChromaDB) for retrieval.
  - **Writer & Editor**: Drafts academic-grade text and refines it for style, flow, and coherence.
  - **Publisher**: Combines chapters/sections and compiles a beautiful PDF report using ReportLab.
- **Local-First Execution**: Fully integrated with Ollama for offline LLM inference, ensuring data privacy and zero API costs.
- **FastAPI Backend**: Robust asynchronous API service to trigger research tasks, track progress, and serve generated files.
- **Streamlit Frontend**: A polished, interactive user interface allowing users to prompt research, view real-time agent coordination, and download compiled PDFs.
- **Persistent Knowledge Graph**: ChromaDB integration for RAG (Retrieval-Augmented Generation) ensuring factual consistency across long reports.

---

## Folder Structure

The project maintains a clean separation of concerns across frontend, backend, test suite, and configuration:

```text
multi-agent-research-writer/
│
├── backend/
│   ├── api/          # FastAPI routes, schemas, and API entry points
│   ├── core/         # Core application configuration, security, and settings
│   ├── agents/       # LangGraph agents definition and workflows
│   ├── models/       # Pydantic models & state definitions
│   ├── memory/       # ChromaDB interactions and vector storage wrappers
│   ├── search/       # DuckDuckGo search integrations and web scraping utilities
│   ├── prompts/      # System prompts and instruction templates for agents
│   └── utils/        # Utility helpers (PDF generation, file handling, logging)
│
├── frontend/         # Streamlit UI pages, components, and static assets
│
├── tests/            # Pytest test suites (unit, integration, and workflow tests)
│
├── docs/             # API documentation, architectural designs, and guides
│
├── requirements.txt  # Python package dependencies
├── README.md         # Project overview and run instructions
├── .env.example      # Configuration environment variables template
├── Dockerfile        # Backend containerization config
├── docker-compose.yml# Multi-container orchestration (FastAPI & Streamlit)
├── .gitignore        # Files and directories ignored by Git
└── pyproject.toml    # Tooling and package settings (Ruff, Pytest, etc.)
```

---

## Installation

### Prerequisites

- **Python 3.12** or higher
- **Docker** and **Docker Compose** (optional, but highly recommended)
- **Ollama** installed on your local machine or an accessible host

### Local Setup

1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd multi-agent-research-writer
   ```

2. **Create a Virtual Environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Environment Variables**:
   Copy the example environment file and customize as needed:
   ```bash
   cp .env.example .env
   ```

---

## Ollama Installation & Setup

This project uses Ollama to run high-performance models locally.

### 1. Install Ollama

- **macOS / Linux**:
  Run the official installation script:
  ```bash
  curl -fsSL https://ollama.com/install.sh | sh
  ```
- **Windows**:
  Download the installer from the [Ollama website](https://ollama.com/download/windows).

### 2. Run Ollama Service

Ensure the Ollama service is running. Typically, it starts automatically on Windows and macOS. On Linux, run:
```bash
ollama serve
```

### 3. Pull the Qwen2.5:7b Model

The research pipeline is optimized for the **Qwen 2.5 (7B)** model due to its strong instruction-following capabilities, rich vocabulary, and excellent reasoning in multi-agent workflows.

Pull the model by executing:
```bash
ollama pull qwen2.5:7b
```

To verify the model is pulled and available:
```bash
ollama list
```

---

## How to Run the Application

You can run the application either directly in your local environment or using Docker.

### Option A: Local Development (Recommended for quick testing)

1. **Start the FastAPI Backend**:
   Ensure your virtual environment is active:
   ```bash
   uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Start the Streamlit Frontend**:
   In a separate terminal tab/window:
   ```bash
   streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0
   ```

3. **Access the Application**:
   - Backend API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
   - Streamlit Frontend: [http://localhost:8501](http://localhost:8501)

### Option B: Docker Compose (Recommended for isolated execution)

Docker Compose automatically orchestrates both the backend API and the frontend UI. It leverages the host's Ollama instance.

1. **Build and Run Containers**:
   ```bash
   docker-compose up --build
   ```

2. **Access the Application**:
   - Backend API: [http://localhost:8000/docs](http://localhost:8000/docs)
   - Streamlit Frontend: [http://localhost:8501](http://localhost:8501)

---

## Future Improvements

- **Advanced PDF Templating**: Integrate custom styling engines and interactive HTML/Markdown-to-PDF converters.
- **Multi-Source Knowledge Retrieval**: Add integration with PubMed, arXiv, and Google Scholar to complement DuckDuckGo.
- **Custom Agent Fine-Tuning**: Support for user-provided models or proprietary endpoints (OpenAI, Anthropic).
- **Human-in-the-Loop Reviews**: Pause workflows at key junctions (e.g., draft approval) to allow direct user modifications before final publishing.
- **Collaborative Research Rooms**: Support multi-user projects where teams can prompt research tracks together.

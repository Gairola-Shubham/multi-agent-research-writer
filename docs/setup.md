# Setup and Installation Guide

This guide walks you through setting up the AI Multi-Agent Research Writer locally, configuring Ollama, downloading required models, and running the application using Docker.

---

## Prerequisites

Before starting, ensure you have installed:
*   **Python 3.12** or higher.
*   **Git** command line interface.
*   **Docker Desktop** (optional, recommended for isolated setup).
*   **Ollama** installed on your host system.

---

## 1. Local Setup

### Step A: Clone the Repository
Clone the codebase to your local directory:
```bash
git clone <repository-url>
cd multi-agent-research-writer
```

### Step B: Virtual Environment & Packages
Initialize a Python virtual environment and install the package requirements:
```bash
python -m venv .venv

# On Windows (PowerShell/CMD):
.venv\Scripts\activate

# On macOS/Linux:
source .venv/bin/activate

# Install dependencies:
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 2. Environment Variables Setup

Copy the environment template file:
```bash
cp .env.example .env
```

Open the newly created `.env` file and verify or adjust the settings:
*   `BACKEND_HOST`: Set to `0.0.0.0` or `127.0.0.1`.
*   `BACKEND_PORT`: Host port mapping for backend FastAPI (Default: `8000`).
*   `FRONTEND_PORT`: Host port mapping for Streamlit (Default: `8501`).
*   `OLLAMA_BASE_URL`: Base connection endpoint for Ollama (e.g., `http://localhost:11434` or `http://host.docker.internal:11434` when inside Docker).
*   `LLM_MODEL`: Local model name to target (Default: `phi3:latest`).
*   `CHROMA_DB_PATH`: Folder path for ChromaDB storage (Default: `./data/chroma`).

---

## 3. Ollama Installation & Setup

This system is configured to run LLMs locally to avoid cloud subscription fees and maintain full data privacy.

### Step A: Install Ollama
*   **macOS / Linux**:
    ```bash
    curl -fsSL https://ollama.com/install.sh | sh
    ```
*   **Windows**: Download and execute the installation setup file from the [Ollama Download Page](https://ollama.com/download/windows).

### Step B: Download the LLM Model
Ensure the Ollama background service is running, and pull the **Phi-3 (latest)** model:
```bash
ollama pull phi3:latest
```

Verify that the model is loaded:
```bash
ollama list
```

---

## 4. Run Locally

With the environment set up and Ollama configured, launch the services:

### Step A: Start the FastAPI Backend
Ensure your virtual environment is active, then run:
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```
API Documentation will be live at [http://localhost:8000/docs](http://localhost:8000/docs).

### Step B: Start the Streamlit Frontend
Open a new terminal tab/window, activate your virtual environment, and execute:
```bash
streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0
```
Open [http://localhost:8501](http://localhost:8501) in your browser to access the frontend dashboard.

---

## 5. Run with Docker Compose

Using Docker Compose automatically mounts volume folders and links the frontend UI to the backend service.

### Step A: Start Container Build
```bash
docker-compose up --build
```

### Step B: Verify Setup
*   FastAPI backend is exposed at `http://localhost:8000/docs`.
*   Streamlit frontend dashboard is exposed at `http://localhost:8501`.
*   **Note**: Ensure your local Ollama port (`11434`) is reachable from Docker. On Windows/macOS, use the default `host.docker.internal:11434` URL path inside `.env`.

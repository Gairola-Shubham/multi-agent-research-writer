# Release Checklist

This checklist contains all steps necessary to package, verify, and launch a new release of the AI Multi-Agent Research Writer system.

---

## 1. Code Integration & Verification

- [ ] Ensure all feature branches are merged cleanly into `main`.
- [ ] Run the Python formatter and linter locally to check syntax consistency:
  ```bash
  ruff format .
  ruff check .
  ```
- [ ] Run the complete test suite to ensure that zero regression bugs exist:
  ```bash
  python -m pytest
  ```
  *(Verify that all 90 tests pass successfully)*.

---

## 2. Setup & Installation Verification

- [ ] **Cloning**: Verify that the project can be cloned successfully into a clean directory:
  ```bash
  git clone <repository-url> clean-test-dir
  cd clean-test-dir
  ```
- [ ] **Installation**: Verify package installation completes without dependency resolution errors:
  ```bash
  python -m venv .venv
  source .venv/bin/activate  # On Windows: .venv\Scripts\activate
  pip install --upgrade pip
  pip install -r requirements.txt
  ```
- [ ] **Environment Setup**: Copy and check variable settings:
  ```bash
  cp .env.example .env
  ```
  Ensure keys (`BACKEND_PORT`, `FRONTEND_PORT`, `OLLAMA_BASE_URL`, `LLM_MODEL`, `CHROMA_DB_PATH`) are present and loaded correctly.

---

## 3. Local Execution Verification

- [ ] **Model Download**: Verify that Ollama starts and the targeted model is available:
  ```bash
  ollama pull qwen2.5:7b
  ollama list
  ```
- [ ] **Running Backend**: Start the FastAPI server and check the interactive documentation page:
  ```bash
  uvicorn backend.main:app --host 0.0.0.0 --port 8000
  ```
  - Access [http://localhost:8000/docs](http://localhost:8000/docs).
  - Verify that the `/health` endpoint responds with a status code of `200 OK`.
- [ ] **Running Frontend**: Start the Streamlit application:
  ```bash
  streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0
  ```
  - Open [http://localhost:8501](http://localhost:8501).
  - Check the sidebar to verify backend status is shown as "Connected".

---

## 4. Docker Deployment Verification

- [ ] **Running Docker**: Spin up the containers using Docker Compose:
  ```bash
  docker-compose up --build
  ```
- [ ] Verify that both services build, link, and report status as healthy.
- [ ] Verify that Streamlit and FastAPI endpoints are accessible on the configured host ports.

---

## 5. End-to-End Pipeline Verification

- [ ] Run a test research query from the Streamlit UI dashboard.
- [ ] Monitor the step-by-step progress logging panels.
- [ ] **Exporting Reports**:
  - Download the generated report in **PDF** format and verify the formatting is correct.
  - Download the generated report in **Word (DOCX)** format and verify the tables and headers are correct.

---

## 6. Release Finalization

- [ ] Bump version numbers in [pyproject.toml](file:///C:/Users/Shivangi/Desktop/Multi-Agent%20Research%20writer/pyproject.toml).
- [ ] Update [CHANGELOG.md](file:///C:/Users/Shivangi/Desktop/Multi-Agent%20Research%20writer/CHANGELOG.md) with details for the new version.
- [ ] Push changes, tag the commit, and release the new tag on GitHub:
  ```bash
  git tag -a v0.2.0 -m "Release version 0.2.0"
  git push origin v0.2.0
  ```

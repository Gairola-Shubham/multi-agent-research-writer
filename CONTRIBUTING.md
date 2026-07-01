# Contributing to AI Multi-Agent Research Writer

Thank you for your interest in contributing to the AI Multi-Agent Research Writer project! We welcome and appreciate contributions of all sizes: bug reports, documentation updates, code cleanups, performance optimizations, and new features.

---

## Code of Conduct

Please be respectful and considerate of other contributors. We aim to foster a welcoming, inclusive, and collaborative open-source community.

---

## How to Contribute

### 1. Reporting Bugs
*   Search the GitHub Issue Tracker to verify that the bug hasn't already been reported.
*   If not, open a new issue. Include:
    *   A clear, descriptive title.
    *   Steps to reproduce the bug.
    *   Expected vs. actual behavior.
    *   Environment details (OS version, Python version, Ollama model version).

### 2. Suggesting Enhancements
*   Submit an issue describing the proposed enhancement.
*   Explain the problem it solves and why it would benefit other users.

### 3. Submitting Pull Requests
*   **Fork** the repository and create your branch from `main`:
    ```bash
    git checkout -b feature/your-feature-name
    ```
*   **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
*   **Write clean code**:
    *   Follow Python PEP 8 styling conventions.
    *   Format your code using `ruff format` and lint using `ruff check`.
*   **Write tests**:
    *   Add unit/integration tests under `tests/` for any new logic.
    *   Ensure all tests execute locally and pass.
*   **Run existing tests**:
    ```bash
    python -m pytest
    ```
*   **Commit messages**:
    *   Write concise, descriptive commit messages.
*   **Submit a PR**:
    *   Describe your changes clearly in the PR description.
    *   Reference any related issue numbers.

---

## Development Guidelines

*   **Mocking Policy**: Do not write tests that require a live Ollama connection, a populated ChromaDB disk directory, or outgoing Internet requests. All external resources should be mocked in [conftest.py](file:///C:/Users/Shivangi/Desktop/Multi-Agent%20Research%20writer/tests/conftest.py) or locally in the test files.
*   **Type Hinting**: Provide proper type annotations for all new function parameters and return types.
*   **Docstrings**: Follow Google Style Python Docstrings conventions.

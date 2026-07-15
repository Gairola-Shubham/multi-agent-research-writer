# API Reference

This document outlines the API endpoints, request/response payload schemas, and error responses exposed by the FastAPI backend service.

---

## 1. Get Service Root

Returns basic status details indicating that the FastAPI server is running.

*   **URL**: `/`
*   **Method**: `GET`
*   **Response Headers**: `Content-Type: application/json`
*   **Status Code**: `200 OK`

### Response Payload Example
```json
{
  "status": "running",
  "application": "AI Multi-Agent Research Writer"
}
```

---

## 2. Get Service Health

Performs structural checks across backend service components (Ollama connection, ChromaDB persistence, workflow graph validation, Search connectivity, and Memory Collection readiness).

*   **URL**: `/health`
*   **Method**: `GET`
*   **Response Headers**: `Content-Type: application/json`
*   **Status Code**: `200 OK`

### Response Payload Example (Healthy)
```json
{
  "status": "healthy",
  "ollama": "healthy",
  "chromadb": "healthy",
  "search": "healthy",
  "memory": "healthy",
  "workflow": "healthy",
  "version": "0.2.0"
}
```

### Response Payload Example (Degraded)
```json
{
  "status": "unhealthy",
  "ollama": "unhealthy",
  "chromadb": "healthy",
  "search": "healthy",
  "memory": "unhealthy",
  "workflow": "healthy",
  "version": "0.2.0"
}
```

---

## 3. Post Research Task

Submits a research topic and parameters to run the LangGraph multi-agent compilation workflow. Returns a fully synthesized academic research markdown document.

*   **URL**: `/research`
*   **Method**: `POST`
*   **Request Headers**: `Content-Type: application/json`
*   **Status Code**: `200 OK`

### Request Schema ([ResearchRequest](file:///C:/Users/Shivangi/Desktop/Multi-Agent%20Research%20writer/backend/schemas/request_models.py))
```json
{
  "topic": "String (Required) - Topic to research",
  "style": "String (Optional) - Formatting or stylistic guidelines (Default: 'standard')",
  "depth": "String (Optional) - Research depth level (Default: 'detailed')"
}
```

### Response Schema ([ResearchResponse](file:///C:/Users/Shivangi/Desktop/Multi-Agent%20Research%20writer/backend/schemas/response_models.py))
```json
{
  "topic": "String - The processed topic",
  "title": "String - Generated research title",
  "final_markdown": "String - Complete structured Markdown document contents",
  "review": "Object - Log statements and scores from the ReviewerAgent",
  "changes_applied": "String - Description of editing changes made"
}
```

### Request Example
```json
{
  "topic": "Impact of quantum computing on modern cryptography",
  "style": "IEEE academic style",
  "depth": "detailed"
}
```

### Response Example
```json
{
  "topic": "Impact of quantum computing on modern cryptography",
  "title": "Quantum Computing and the Future of Cryptography",
  "final_markdown": "# Quantum Computing and Cryptography\n\n## Abstract...\n\n## Section 1: Shor's Algorithm...",
  "review": {
    "score": 9.2,
    "comments": "High quality writeup. Tone is academic."
  },
  "changes_applied": "Formatted titles to IEEE headers, adjusted capitalization."
}
```

---

## Error Responses

The API uses standardized HTTP status codes and payloads to indicate issues:

### 422 Unprocessable Entity
Returned when request parameters (e.g., empty topic strings) fail validation.
```json
{
  "detail": "Failed to generate structured research: Input plan is missing 'topic'"
}
```

### 503 Service Unavailable
Returned when the backend is unable to connect to the Ollama server.
```json
{
  "detail": "Ollama offline: Cannot connect to Ollama server at http://localhost:11434."
}
```

### 504 Gateway Timeout
Returned when the Ollama server connection or response generation times out.
```json
{
  "detail": "Request timeout: Request to Ollama timed out after 3 attempts."
}
```

### 500 Internal Server Error
Returned for unhandled exceptions or execution failures.
```json
{
  "detail": "Internal server error: ChromaDB persistent client failed to load database."
}
```

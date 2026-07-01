# Application Screenshots

This document contains visual representations and layout placeholders for key interface components of the AI Multi-Agent Research Writer system.

---

## 1. Homepage Dashboard

Renders the main Streamlit configuration dashboard, showing settings inputs, Ollama model statuses, and the research submission pane.

```text
+-----------------------------------------------------------------------------------+
|  [Logo] AI Multi-Agent Research Writer                       [Ollama Status: OK]  |
+-----------------------------------------------------------------------------------+
|  Topic to Research:                                                               |
|  [ Impact of Quantum Computing on Modern Cryptography                         ]   |
|                                                                                   |
|  Styling / Guidelines:                      Depth:                                |
|  [ IEEE Academic Style        ]             ( ) Standard  (*) Detailed  ( ) Brief |
|                                                                                   |
|  [ START RESEARCH PIPELINE ]                                                      |
+-----------------------------------------------------------------------------------+
|  Pipeline Logs & Live Activity:                                                   |
|  [i] [PlannerNode] - Drafting research outline for sections...                    |
|  [i] [ResearchNode] - Fetching DuckDuckGo web results for Shor's Algorithm...     |
|  [i] [ResearchNode] - Persistent ChromaDB lookup returned 3 matches.              |
+-----------------------------------------------------------------------------------+
```

---

## 2. Generated Report Output

Shows the final refined Markdown report rendered inside Streamlit, displaying structure headers, key takeaway lists, and generated references.

```text
+-----------------------------------------------------------------------------------+
|  Research Topic: Impact of Quantum Computing on Modern Cryptography               |
+-----------------------------------------------------------------------------------+
|  # Quantum Computing and the Future of Cryptography                               |
|                                                                                   |
|  ## Abstract                                                                      |
|  This paper explores the security vulnerabilities introduced in public-key        |
|  cryptosystems due to scale-level developments in quantum computing...            |
|                                                                                   |
|  ## Section 1: Shor's Algorithm and Asymmetric Cryptography                      |
|  Asymmetric encryption schemes relying on integer factorization (RSA) and        |
|  discrete logarithms (ECC) are mathematically vulnerable to quantum attacks...    |
|                                                                                   |
|  ### Key Takeaway Points:                                                         |
|  * Shor's algorithm solves prime factorization in polynomial time.               |
|  * Symmetric keys (AES-256) remain largely secure using Grover's algorithm.        |
+-----------------------------------------------------------------------------------+
```

---

## 3. Reviewer Agent Comments

Exhibits the ReviewerAgent feedback panel, detailing quality metrics, style guide compliance percentages, and improvement comments.

```text
+-----------------------------------------------------------------------------------+
|  [+] Agent Review & Quality Feedback Logs                                          |
+-----------------------------------------------------------------------------------+
|  * Reviewer Rating: 9.2 / 10.0                                                    |
|  * Style Compliance: 95% (IEEE format requirements met)                           |
|                                                                                   |
|  Review Comments:                                                                 |
|  "The draft maintains high technical accuracy. Structural transitions between     |
|  Section 1 and Section 2 are clean. Ensure capitalization in references table     |
|  matches standard citation formatting rules."                                     |
+-----------------------------------------------------------------------------------+
```

---

## 4. Document Export Options

Renders download links to export final compiled documents to PDF and DOCX file types.

```text
+-----------------------------------------------------------------------------------+
|  [ Download Report as PDF ]               [ Download Report as Word (DOCX) ]      |
+-----------------------------------------------------------------------------------+
|  Files are compiled and structured on demand. PDF uses custom ReportLab layouts    |
|  including header/footer structures and numbered pages. DOCX creates standard     |
|  Word formatting for academic edits.                                              |
+-----------------------------------------------------------------------------------+
```

---

## 5. Health Diagnostic Endpoint Check

Visual representation of raw JSON output returned by the FastAPI server `/health` route.

```json
{
  "status": "healthy",
  "ollama": "healthy",
  "chromadb": "healthy",
  "search": "healthy",
  "memory": "healthy",
  "workflow": "healthy",
  "version": "0.1.0"
}
```

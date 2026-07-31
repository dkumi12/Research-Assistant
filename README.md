# 🔬 Autonomous AI Research Assistant

An enterprise-ready, agentic research service built with **LangGraph**, **FastAPI**, and **OpenRouter**. The assistant executes iterative web searches, dynamically grades source evidence, refines search queries on the fly, and synthesizes cited research reports.

---

## 🏗 System Architecture

The core research pipeline is structured as a stateful graph utilizing **LangGraph**. Instead of relying on a single linear prompt, the system cycles through a feedback loop to guarantee evidence depth before generating a final response.

```text
                  +-------------------+
                  |      [START]      |
                  +---------+---------+
                            |
                            v
                  +-------------------+
                  |    create_plan    |
                  +---------+---------+
                            |
                            v
                  +-------------------+
                  |     research      |<--------------------+
                  +---------+---------+                     |
                            |                               |
                            v                               |
                  +-------------------+                     |
                  |  grade_evidence   |                     |
                  +---------+---------+                     |
                            |                               |
                            v                               |
                 /---------------------\                    |
                /  route_after_grade    \                   |
               /   (Sufficient / Max?)   \                  |
              +---------------------------+                 |
             /                             \                |
     (YES)  /                               \  (NO)         |
           v                                 v              |
+-------------------+               +-------------------+   |
|   write_report    |               |  Refine Queries   +---+
+---------+---------+               +-------------------+
          |
          v
  +---------------+
  |    [END]      |
  +---------------+

```

---

## ✨ Key Features

* **Agentic Search & Loop:** Dynamically evaluates search results against the original research query and loops back for additional web searches if evidence is insufficient.
* **Self-Correction & Query Refinement:** Automatically generates improved search queries based on missing information identified during the grading phase.
* **Asynchronous Non-Blocking Execution:** Uses `asyncio.to_thread` to wrap synchronous graph execution within FastAPI, keeping the event loop responsive to cancellation signals (`Ctrl + C`).
* **Resilient API Strategy:** Configured with strict request timeouts, fallbacks for empty search results, and custom header definitions for OpenRouter model routing.
* **Automated Testing Suite:** Includes `pytest` integration and route validation tests with mocked graph invocations for CI/CD environments.

---

## 🧰 Tech Stack

* **Framework:** FastAPI, Uvicorn
* **Orchestration & AI:** LangGraph, LangChain
* **LLM Provider:** OpenRouter (`google/gemma-2-9b-it`, `openai/gpt-4o-mini`, or `mistralai/mistral-nemo`)
* **Web Search:** Tavily API
* **Validation & Serialization:** Pydantic v2
* **Testing:** Pytest, HTTPX, FastAPI `TestClient`

---

## 📁 Directory Structure

```text
.
├── src/
│   ├── api.py          # FastAPI application & endpoints
│   ├── graph.py        # LangGraph state definition & nodes
│   ├── schemas.py      # Pydantic request/response models
│   └── tools.py        # LLM initialization, web search, & prompts
├── tests/
│   ├── test_api.py     # Integration tests with mocked graph calls
│   └── test_routes.py  # HTTP route & schema validation tests
├── .env                # Environment variables (Git-ignored)
├── requirements.txt    # Project dependencies
└── README.md           # Project documentation

```

---

## 🚀 Getting Started

### 1. Prerequisites

* Python `3.10+`
* An [OpenRouter API Key](https://openrouter.ai/)
* A [Tavily Search API Key](https://tavily.com/)

### 2. Installation

Clone the repository and set up a virtual environment:

```bash
git clone https://github.com/YOUR_USERNAME/AI-Research-Assistant.git
cd AI-Research-Assistant

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

```

### 3. Environment Configuration

Create a `.env` file in the root directory:

```env
OPENROUTER_API_KEY=sk-or-v1-YOUR_OPENROUTER_KEY
TAVILY_API_KEY=tvly-YOUR_TAVILY_KEY
OPENROUTER_MODEL_ID=google/gemma-2-9b-it
MAX_SEARCH_ROUNDS=2

```

---

## 🏃 Running the Application

Start the local development server with Uvicorn:

```bash
uvicorn src.api:app --reload

```

The server will spin up at `[http://127.0.0.1:8000](http://127.0.0.1:8000)`. You can access the interactive Swagger API documentation at:
👉 **`[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)`**

---

## 📡 API Usage

### Execute Research Request

**Endpoint:** `POST /api/research`

**Payload:**

```json
{
  "question": "What are the benefits and risks of the Turkish Get-Up for scoliosis patients?",
  "depth": "comprehensive"
}

```

**Response Example:**

```json
{
  "question": "What are the benefits and risks of the Turkish Get-Up for scoliosis patients?",
  "report": "# Research Report: Kettlebell Turkish Get-Up (TGU) for Scoliosis Patients\n\n### 1. Biomechanical Analysis...\n",
  "search_rounds": 2,
  "evidence_score": 85,
  "sources": [
    {
      "title": "The Turkish Get-Up - Biomechanics Education",
      "url": "https://biomechanicseducation.com/...",
      "content": "Sample extracted evidence..."
    }
  ]
}

```

---

## 🧪 Running Tests

The repository includes unit and integration tests using `pytest`. The integration tests mock external API calls to avoid burning LLM credits during test runs.

To execute the test suite:

```bash
pytest

```
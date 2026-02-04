# Cosmetic-Assistant

An AI-powered Chatbot Assistant for cosmetic product recommendations, built with a Multi-Agent architecture.

## 🚀 Getting Started

### Prerequisites

- Docker & Docker Compose
- Nvidia NIM API Key (or OpenAI compatible key)
- Google Gemini API Key

### 1. Setup & Run

Start the backend services using Docker Compose:

```bash
docker compose up --build
```

This will start:

- `cosmetics_db`: PostgreSQL database with `pgvector` extension.
- `cosmetics_backend`: The FastAPI application server.

### 2. Initialize Embeddings

Once the containers are running, you need to generate embeddings for the product catalog. Run the following command in a new terminal:

```bash
docker exec -it cosmetics_backend python scripts/run_embedding.py
```

This script fetches products from the database, generates embeddings using Google Gemini, and stores them in the `pgvector` column for semantic search.

## 🧪 Demo & Testing

You can verify the system's "Orchestrator" capabilities (Memory & Ambiguity Handling) using the CLI demo runner.

### Run Demo Scenarios

To run a specific test scenario, execute the `run_demo_cli.py` script inside the container:

**Scenario 1: Long Conversation (Memory Trigger)**
_Simulates a long chat history to trigger auto-summarization._

```bash
docker exec -it cosmetics_backend python scripts/run_demo_cli.py --file tests/data/long_conversation.jsonl
```

**Scenario 2: Ambiguous Query (Query Understanding)**
_Tests the agent's ability to rewrite ambiguous queries (e.g., "that one") or ask clarifying questions._

```bash
docker exec -it cosmetics_backend python scripts/run_demo_cli.py --file tests/data/ambiguous_query.jsonl
```

**Scenario 3: Mixed Scenario (Context Switching)**
_Tests handling of topic changes and follow-up questions._

```bash
docker exec -it cosmetics_backend python scripts/run_demo_cli.py --file tests/data/mixed_scenario.jsonl
```

### View Results Offline

If you prefer not to run the commands, you can view the pre-recorded output logs in the `data/demo/` directory:

- `data/demo/long_conservation.md`: Demonstrates memory summarization after 10+ turns.
- `data/demo/ambigious_query.md`: Shows the system asking clarifying questions.
- `data/demo/mixed_scenario.md`: Shows handling of context switching.

> **Tip:** when viewing these `.md` files in VS Code, press `Ctrl+Shift+V` to open the Markdown Preview for a better reading experience.

## ⚠️ Limitations & Current Status

### Demo Coverage

- **Backend CLI Demo (`run_demo_cli.py`)**:
  - ✅ **Agents**: Orchestrator, Search, Expert, Consultant (4/5).
  - ✅ **Features**: Full Memory (Summarization) & Ambiguity Handling.
  - ⚠️ **Missing**: `SalesAgent` is not included in this CLI demo due to complex state management requirements.

- **Frontend (Streamlit) Demo**:
  - ✅ **Agents**: Full suite including `SalesAgent` (5/5).
  - ⚠️ **Missing**: Does **not** yet utilize the new `MemoryManager` (Summarization/Context) logic implemented in the backend CLI.

  **Screenshots:**

  ![Frontend Demo 1](data/demo/Screenshot%202026-02-04%20122505.png)
  ![Frontend Demo 2](data/demo/Screenshot%202026-02-04%20122512.png)
  ![Frontend Demo 3](data/demo/Screenshot%202026-02-04%20122520.png)
  ![Frontend Demo 4](data/demo/Screenshot%202026-02-04%20122526.png)
  ![Frontend Demo 5](data/demo/Screenshot%202026-02-04%20122539.png)

### Other Notes

- **Order History**: The "Long Conversation" scenario demonstrates the _intent_ to purchase, but the final confirmation and persistent order history storage are not yet implemented.

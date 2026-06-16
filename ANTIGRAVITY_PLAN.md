## 1. System Topology & Component Map

The system utilizes a 3-tier architecture to ingest, store, and query graph-relational data representing human relationships. FalkorDB (a high-performance, Redis-compatible graph database) acts as the primary data store. 

```
┌────────────────────────────────────────────────────────┐
│                      Client UI                         │
│             (Streamlit Web Application)                │
└───────────┬───────────────────────────────▲────────────┘
            │                               │
            │ 1. Submit Person Data         │ 4. Render Results
            ▼                               │
┌───────────────────────────────────────────┴────────────┐
│                  Python Backend Engine                 │
│         (FalkorDB Client & Agent Interface)            │
└───────────┬───────────────────────────────▲────────────┘
            │                               │
            │ 2. Cypher Queries             │ 3. Schema & Data
            ▼                               │
┌──────────────────────────────┐ ┌──────────┴────────────┐
│          FalkorDB            │ │   Google GenAI Agent  │
│      (Docker Instance)       │ │  (NL to Cypher Tool)  │
└──────────────────────────────┘ └───────────────────────┘
```

### Component Breakdown
*   **Data Tier (FalkorDB)**: Runs via Docker. It stores entities as Nodes (`Person`) and their connections as directed Edges (`RELATES_TO`).
*   **Application Tier (Python / Streamlit)**: 
    *   **Data Ingestion UI**: A graphical form allowing users to input two people, their properties (Name, Location), the relationship type (e.g., Friend, Enemy, Boss), and an emotional sentiment score (e.g., Hate to Love).
    *   **Agent Interface**: Integrates with the Google Agent ADK to interpret English queries, convert them to Cypher queries, execute them on FalkorDB, and return natural language responses.
*   **AI Agent Tier (Google Agent ADK)**: Leverages structured system instructions and function-calling (tools) to interact with FalkorDB safely.

---

## 2. Technical Specifications

### Tech Stack & Dependencies
*   **Runtime**: Python 3.11+
*   **Database**: FalkorDB (Docker image: `falkordb/falkordb:latest`)
*   **Libraries**:
    *   `falkordb==1.0.1` (Python client for FalkorDB)
    *   `google-genai==2.8.0` (Google GenAI SDK)
    *   `google-adk==2.2.0` (Google ADK)
    *   `streamlit==1.32.0` (UI framework)
    *   `pydantic==2.13.0` (Data validation)

### Database Schema (Graph Model)

#### Nodes
*   **Label**: `Person`
*   **Properties**:
    *   `name`: `String` (Unique identifier/Key)
    *   `location`: `String`

#### Edges (Relationships)
*   **Type**: `RELATES_TO`
*   **Properties**:
    *   `type`: `String` (e.g., "friend", "husband", "enemy", "boss")
    *   `sentiment`: `String` (e.g., "love", "like", "neutral", "dislike", "hate")

---

## 3. Antigravity Step-by-Step Task List

- [ ] **Task 1: Infrastructure and Environment Configuration**
  - **Context:** Spin up the FalkorDB instance and configure the Python virtual environment.
  - **Files to Create/Modify:** 
    *   `docker-compose.yml`
    *   `requirements.txt`
    *   `.env`
  - **Verification Criteria:** Run `docker compose up -d` and verify FalkorDB is listening on port `6379` using a TCP ping or `redis-cli ping`.

- [ ] **Task 2: Database Connection and Ingestion Module**
  - **Context:** Implement the core Python interface to interact with FalkorDB using the official client library. Define methods to upsert nodes and create relationships.
  - **Files to Create/Modify:**
    *   `src/database.py`
  - **Verification Criteria:** Run a test script `pytest tests/test_database.py` to insert two test nodes with a relationship and retrieve them via Cypher query.

- [ ] **Task 3: Streamlit Data Ingestion UI**
  - **Context:** Build a user-friendly UI to capture the two-person tuple, properties, relationship type, and emotional value, then persist them to FalkorDB.
  - **Files to Create/Modify:**
    *   `src/app.py`
  - **Verification Criteria:** Start the UI via `streamlit run src/app.py`. Ensure submitting a form successfully writes data to the graph with no errors.

- [ ] **Task 4: Google GenAI Agent Integration**
  - **Context:** Build the English-to-Cypher translation agent using the Google GenAI SDK. The agent receives a natural language query, translates it to a valid FalkorDB Cypher query, runs it, and formats the output.
  - **Files to Create/Modify:**
    *   `src/agent.py`
  - **Verification Criteria:** Run `python src/agent.py --query "Who is enemies with Alice?"` and verify it returns a correct, coherent English answer based on the DB state.

- [ ] **Task 5: End-to-End System Integration**
  - **Context:** Embed the natural language querying agent directly into the Streamlit UI to allow users to both enter data and ask questions in one dashboard.
  - **Files to Create/Modify:**
    *   `src/app.py`
  - **Verification Criteria:** Open the updated Streamlit app, enter a relationship, ask a query in the chat box, and confirm the UI outputs the correct semantic answer."

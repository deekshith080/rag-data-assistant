# RAG Data Catalog Assistant

Enterprise-grade Natural Language to SQL system using RAG, LangChain, ChromaDB, Llama3, FastAPI, and Streamlit.

Ask questions about your data in plain English and get instant SQL results.

## Demo

```
User: "What is the total revenue per customer?"

System:
  1. Retrieves relevant schemas from ChromaDB (revenue, customers)
  2. Generates SQL using Llama3
  3. Executes SQL on database
  4. Returns results as table

Result:
  Acme Corp    -> $8,500
  CloudFirst   -> $5,000
  Enterprise Co -> $5,000
```

## Architecture

```
User Question
      |
      v
ChromaDB Vector Store
(finds relevant table schemas using nomic-embed-text embeddings)
      |
      v
Llama3 LLM
(generates SQL using retrieved schemas as context)
      |
      v
SQLite Database
(executes SQL, returns results)
      |
      v
FastAPI REST API -> Streamlit Chat Interface
```

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| LLM | Llama3 (via Ollama) | SQL generation |
| Embeddings | nomic-embed-text | Schema vectorization |
| Vector DB | ChromaDB | Schema retrieval |
| Orchestration | LangChain | RAG pipeline |
| Database | SQLite | Query execution |
| API | FastAPI | REST backend |
| UI | Streamlit | Chat interface |
| Runtime | Ollama | Local LLM serving |

## Why RAG for SQL Generation

Without RAG, an LLM cannot generate accurate SQL because it does not know your schema.
RAG solves this by retrieving relevant table schemas at query time and providing them as context.

```
Without RAG: LLM guesses column names -> wrong SQL -> errors
With RAG:    LLM sees actual schema -> correct SQL -> results
```

## Database Schema

| Table | Description |
|-------|-------------|
| customers | Company accounts with industry and account manager |
| subscriptions | Plan details with pricing and status |
| revenue | Monthly revenue records per customer |
| events | User activity logs and feature usage |
| support_tickets | Customer support history and priority |

## Quick Start

### Prerequisites
- Python 3.10+
- Ollama installed (https://ollama.com)

### Setup

```bash
# Clone
git clone https://github.com/deekshith080/rag-data-assistant.git
cd rag-data-assistant

# Install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Pull Ollama models
ollama pull llama3
ollama pull nomic-embed-text

# Create database
python3 src/database/schema_extractor.py

# Index schemas into ChromaDB
python3 src/embeddings/vector_store.py

# Start everything
bash start.sh
```

### Access

```
FastAPI docs -> http://localhost:8001/docs
Streamlit UI -> http://localhost:8502
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /health | Health check |
| POST | /query | Natural language to SQL |

### Example Request

```bash
curl -X POST http://localhost:8001/query \
  -H "Content-Type: application/json" \
  -d '{"question": "show me total revenue per customer"}'
```

### Example Response

```json
{
  "question": "show me total revenue per customer",
  "sql": "SELECT c.company_name, SUM(r.amount) FROM revenue r JOIN customers c...",
  "tables_used": ["revenue", "customers"],
  "success": true,
  "rows": [{"company_name": "Acme Corp", "total_revenue": 8500}],
  "row_count": 8
}
```

## Real World Use Cases

This pattern solves a real problem at every data-driven company:

- Analysts spend hours writing SQL for simple questions
- New engineers waste days learning which tables to use
- Data teams get flooded with "what table has X?" questions

This system lets anyone query data in plain English without knowing SQL or schema details.

## Author

Deekshith - Data and ML Engineer
GitHub: https://github.com/deekshith080
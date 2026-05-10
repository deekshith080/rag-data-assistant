"""
FastAPI backend for the RAG Data Assistant.
Exposes one endpoint: POST /query
Takes a natural language question, returns SQL + results.
"""

import sys
sys.path.insert(0, ".")
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.rag.sql_generator import SQLGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

generator = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global generator
    logger.info("Loading SQLGenerator...")
    generator = SQLGenerator()
    logger.info("API ready.")
    yield
    logger.info("API shutting down.")

app = FastAPI(
    title="RAG Data Assistant API",
    description="Natural language to SQL using RAG + Llama3.",
    version="1.0.0",
    lifespan=lifespan,
)

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    question: str
    sql: str
    tables_used: list
    success: bool
    columns: list
    rows: list
    row_count: int
    error: str = ""

@app.get("/health")
def health():
    return {"status": "healthy", "model": "llama3", "embeddings": "nomic-embed-text"}

@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):
    """
    Takes a natural language question.
    Returns SQL query + results from the database.
    """
    if not generator:
        raise HTTPException(status_code=503, detail="Model not loaded yet.")
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    try:
        result = generator.generate_and_execute(request.question)
        return QueryResponse(**result)
    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
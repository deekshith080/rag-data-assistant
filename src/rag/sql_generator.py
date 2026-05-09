"""
src/rag/sql_generator.py
Generates SQL from natural language using RAG + Llama3.
1. Retrieves relevant schemas from ChromaDB
2. Builds prompt with schemas + question
3. Sends to Llama3 for SQL generation
4. Executes SQL on database
5. Returns results
"""

import sys
sys.path.insert(0, ".")
import sqlite3
import re
import ollama
from src.embeddings.vector_store import VectorStore

DB_PATH = "data/company.db"
LLAMA_MODEL = "llama3"

SQL_PROMPT_TEMPLATE = """You are an expert SQL developer.
Given the following table schemas, write a SQLite SQL query to answer the question.

SCHEMAS:
{schemas}

QUESTION: {question}

Rules:
- Write only the SQL query, nothing else
- Use only the tables and columns shown in the schemas
- Always use proper SQLite syntax
- End the query with a semicolon
- If joining tables, use explicit JOIN syntax

SQL:"""


class SQLGenerator:
    """
    Generates and executes SQL from natural language questions.
    Uses RAG to find relevant schemas, Llama3 to generate SQL.
    """

    def __init__(self):
        self.vector_store = VectorStore()
        self.vector_store.index_schemas()
        print("SQLGenerator ready.")

    def _build_prompt(self, question: str, schemas: list) -> str:
        """Build prompt with schemas and question for Llama3."""
        schema_text = chr(10).join([s["schema_text"] for s in schemas])
        return SQL_PROMPT_TEMPLATE.format(
            schemas=schema_text,
            question=question,
        )

    def _extract_sql(self, response: str) -> str:
        """Extract clean SQL from Llama3 response."""
        # Remove markdown code blocks if present
        response = re.sub(r"```sql", "", response)
        response = re.sub(r"```", "", response)
        # Get everything up to and including semicolon
        match = re.search(r"(SELECT.*?;)", response, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return response.strip()

    def _execute_sql(self, sql: str) -> dict:
        """Execute SQL on SQLite database and return results."""
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            results = [dict(row) for row in rows]
            conn.close()
            return {"success": True, "columns": columns, "rows": results, "row_count": len(results)}
        except Exception as e:
            return {"success": False, "error": str(e), "columns": [], "rows": [], "row_count": 0}

    def generate_and_execute(self, question: str) -> dict:
        """
        Full pipeline: question -> schemas -> SQL -> results
        """
        print(f"Question: {question}")

        # Step 1: Retrieve relevant schemas
        print("Retrieving relevant schemas...")
        schemas = self.vector_store.retrieve_relevant_schemas(question, n_results=3)
        tables_used = [s["table_name"] for s in schemas]

        # Step 2: Build prompt
        prompt = self._build_prompt(question, schemas)

        # Step 3: Generate SQL with Llama3
        print("Generating SQL with Llama3...")
        response = ollama.chat(
            model=LLAMA_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        raw_sql = response["message"]["content"]

        # Step 4: Extract clean SQL
        sql = self._extract_sql(raw_sql)
        print(f"Generated SQL: {sql}")

        # Step 5: Execute SQL
        print("Executing SQL...")
        result = self._execute_sql(sql)

        return {
            "question": question,
            "sql": sql,
            "tables_used": tables_used,
            "success": result["success"],
            "columns": result["columns"],
            "rows": result["rows"],
            "row_count": result["row_count"],
            "error": result.get("error", None),
        }


if __name__ == "__main__":
    generator = SQLGenerator()

    questions = [
        "Show me all customers and their subscription plans",
        "What is the total revenue per customer?",
        "Which customers have open support tickets?",
    ]

    for question in questions:
        print(chr(10) + "=" * 60)
        result = generator.generate_and_execute(question)
        print("Tables used: " + str(result["tables_used"]))
        if result["success"]:
            print("Rows returned: " + str(result["row_count"]))
            for row in result["rows"][:3]:
                print(f"  {row}")
        else:
            print("Error: " + str(result["error"]))
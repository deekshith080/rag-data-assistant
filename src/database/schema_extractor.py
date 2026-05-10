"""
Extracts table schemas from SQLite and converts to text for ChromaDB.
"""

import sqlite3

TABLE_DESCRIPTIONS = {
    "customers": "Stores customer account information including company name, industry, country, and account manager.",
    "subscriptions": "Stores subscription plans per customer including plan name, monthly price, start date, end date, and status.",
    "revenue": "Stores monthly revenue records per customer including amount and revenue type such as subscription or expansion.",
    "events": "Stores user activity events including logins, feature usage, session duration, and timestamps.",
    "support_tickets": "Stores customer support tickets including priority, category, creation date, resolution date, and status.",
}

class SchemaExtractor:
    def __init__(self, db_path="data/company.db"):
        self.db_path = db_path

    def get_tables(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        return tables

    def get_columns(self, table_name):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        conn.close()
        return [{"name": col[1], "type": col[2]} for col in columns]

    def get_sample_values(self, table_name, column_name, limit=5):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"SELECT DISTINCT {column_name} FROM {table_name} WHERE {column_name} IS NOT NULL LIMIT {limit}")
        values = [str(row[0]) for row in cursor.fetchall()]
        conn.close()
        return values

    def get_row_count(self, table_name):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def extract_schema_text(self, table_name):
        columns = self.get_columns(table_name)
        row_count = self.get_row_count(table_name)
        lines = []
        lines.append(f"Table: {table_name}")
        lines.append(f"Row count: {row_count}")
        lines.append("Columns:")
        for col in columns:
            sample_vals = self.get_sample_values(table_name, col["name"])
            sample_str = ", ".join(sample_vals) if sample_vals else "N/A"
            lines.append(f'  - {col["name"]} ({col["type"]}): sample values: {sample_str}')
        description = TABLE_DESCRIPTIONS.get(table_name, "No description available.")
        lines.append(f"Description: {description}")
        return chr(10).join(lines)

    def extract_all_schemas(self):
        tables = self.get_tables()
        schemas = []
        for table in tables:
            schema_text = self.extract_schema_text(table)
            schemas.append({"table_name": table, "schema_text": schema_text})
            print(f"Extracted schema for: {table}")
        return schemas

if __name__ == "__main__":
    extractor = SchemaExtractor()
    schemas = extractor.extract_all_schemas()
    print("=" * 50)
    print("Sample schema output:")
    print("=" * 50)
    print(schemas[0]["schema_text"])
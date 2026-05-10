#!/bin/bash
# start.sh — starts the RAG Data Assistant
cd ~/Downloads/rag-data-assistant
source venv/bin/activate
echo "Starting FastAPI on port 8001..."
python3 -m uvicorn src.api.app:app --port 8001 &
sleep 5
echo "Starting Streamlit on port 8502..."
streamlit run streamlit_app.py --server.port 8502 &
echo ""
echo "All services started!"
echo "FastAPI   -> http://localhost:8001/docs"
echo "Streamlit -> http://localhost:8502"
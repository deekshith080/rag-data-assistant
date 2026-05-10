#!/bin/bash
# stop.sh — stops all services
pkill -f uvicorn
pkill -f streamlit
echo "All services stopped."
#!/bin/bash
cd backend

# Try different Python commands
if command -v python3 &> /dev/null; then
    echo "Starting Flask development server with python3..."
    python3 app.py
elif command -v python &> /dev/null; then
    echo "Starting Flask development server with python..."
    python app.py
else
    echo "Python not found. Available commands:"
    which python || which python3 || echo "No Python found"
    exit 1
fi

#!/bin/bash
cd backend

# Try gunicorn first
if command -v gunicorn &> /dev/null; then
    echo "Starting with gunicorn..."
    gunicorn app:app --bind 0.0.0.0:$PORT
else
    echo "Gunicorn not found, trying Flask development server..."
    python app.py
fi

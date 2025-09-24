#!/bin/bash
cd backend

# Use Flask development server (more reliable than gunicorn)
echo "Starting Flask development server..."
python app.py

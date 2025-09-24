#!/bin/bash

echo "=== Railway Environment Debug Info ==="
echo "Current directory: $(pwd)"
echo "Files in current directory: $(ls -la)"
echo "Available Python commands:"
which python || echo "python not found"
which python3 || echo "python3 not found"
which python3.9 || echo "python3.9 not found"
which python3.10 || echo "python3.10 not found"
which python3.11 || echo "python3.11 not found"
echo "PATH: $PATH"
echo "=== End Debug Info ==="

# Railway runs this script from the root directory (/app), so we need to cd to backend
cd backend

# Try different Python commands in order of preference
PYTHON_CMD=""

if command -v python3.11 &> /dev/null; then
    PYTHON_CMD="python3.11"
    echo "Using python3.11"
elif command -v python3.10 &> /dev/null; then
    PYTHON_CMD="python3.10"
    echo "Using python3.10"
elif command -v python3.9 &> /dev/null; then
    PYTHON_CMD="python3.9"
    echo "Using python3.9"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    echo "Using python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    echo "Using python"
else
    echo "ERROR: No Python found!"
    echo "Available commands:"
    (which python || which python3 || which python3.9 || which python3.10 || which python3.11) | head -5
    exit 1
fi

echo "Starting Flask development server with $PYTHON_CMD..."
$PYTHON_CMD app.py

#!/bin/bash
# Setup script for local development

echo "🔧 Setting up MyRecipeFinder for local development..."
echo "=" * 60

# Check if we're in the right directory
if [ ! -f "backend/app.py" ]; then
    echo "❌ Please run this from the MyRecipeFinder root directory"
    exit 1
fi

echo "✅ Found backend files"

# Check Python
python --version
if [ $? -ne 0 ]; then
    echo "❌ Python not found. Please install Python 3.8+"
    exit 1
fi

echo "✅ Python found"

# Setup backend
echo ""
echo "📦 Setting up backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python -m venv .venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/Scripts/activate  # Windows
# source .venv/bin/activate  # macOS/Linux

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating backend/.env file..."
    cat > .env << 'EOF'
FLASK_ENV=development
PORT=4000
FRONTEND_ORIGIN=http://localhost:5173

# Add your API keys here:
COHERE_API_KEY=your_cohere_key_here
TAVILY_API_KEY=your_tavily_key_here

# Database (SQLite for local development)
DATABASE_URL=sqlite:///./app.db
EOF
    echo "⚠️  Please edit backend/.env and add your API keys!"
fi

echo "✅ Backend setup complete"
cd ..

# Setup frontend
echo ""
echo "📦 Setting up frontend..."
cd frontend

# Check Node.js
node --version
if [ $? -ne 0 ]; then
    echo "❌ Node.js not found. Please install Node.js 16+"
    exit 1
fi

echo "✅ Node.js found"

# Install dependencies
if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install
fi

echo "✅ Frontend setup complete"
cd ..

echo ""
echo "🚀 Ready to run!"
echo ""
echo "Terminal 1 - Backend:"
echo "  cd backend"
echo "  source .venv/Scripts/activate  # Windows"
echo "  python app.py"
echo ""
echo "Terminal 2 - Frontend:"
echo "  cd frontend"
echo "  npm run dev"
echo ""
echo "🌐 Frontend will be at: http://localhost:5173"
echo "🔗 Backend API will be at: http://localhost:4000"
echo ""
echo "⚠️  Remember to add your API keys to backend/.env!"

#!/usr/bin/env python3
"""
Local Development Setup for MyRecipeFinder
Run this to set up and test your local environment
"""

import os
import sys
import subprocess
import time

def check_requirements():
    """Check if all requirements are met"""
    print("🔍 Checking requirements...")

    # Check Python
    try:
        result = subprocess.run([sys.executable, "--version"], capture_output=True, text=True)
        print(f"✅ Python: {result.stdout.strip()}")
    except:
        print("❌ Python not found")
        return False

    # Check Node.js
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        print(f"✅ Node.js: {result.stdout.strip()}")
    except:
        print("❌ Node.js not found")
        return False

    return True

def setup_backend():
    """Setup backend environment"""
    print("\n📦 Setting up backend...")

    backend_dir = os.path.join(os.getcwd(), "backend")

    # Create .env if missing
    env_file = os.path.join(backend_dir, ".env")
    if not os.path.exists(env_file):
        print("Creating backend/.env...")
        with open(env_file, "w") as f:
            f.write("""FLASK_ENV=development
PORT=4000
FRONTEND_ORIGIN=http://localhost:5173

# Add your API keys here:
COHERE_API_KEY=your_cohere_key_here
TAVILY_API_KEY=your_tavily_key_here

# Database (SQLite for local development)
DATABASE_URL=sqlite:///./app.db
""")
        print("⚠️  Please edit backend/.env and add your API keys!")

    # Create virtual environment if needed
    venv_path = os.path.join(backend_dir, ".venv")
    if not os.path.exists(venv_path):
        print("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", ".venv"], cwd=backend_dir)

    # Install dependencies
    print("Installing Python dependencies...")
    subprocess.run([os.path.join(venv_path, "Scripts", "python"), "-m", "pip", "install", "-r", "requirements.txt"],
                   cwd=backend_dir, check=True)

    print("✅ Backend setup complete")

def setup_frontend():
    """Setup frontend environment"""
    print("\n📦 Setting up frontend...")

    frontend_dir = os.path.join(os.getcwd(), "frontend")

    # Install dependencies
    if not os.path.exists(os.path.join(frontend_dir, "node_modules")):
        print("Installing Node.js dependencies...")
        subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)

    print("✅ Frontend setup complete")

def test_backend():
    """Test backend connectivity"""
    print("\n🧪 Testing backend...")

    try:
        import requests
        response = requests.get("http://localhost:4000/health", timeout=5)
        print(f"✅ Backend health check: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ Backend not responding: {e}")
        return False

def main():
    print("🚀 MyRecipeFinder Local Development Setup")
    print("=" * 50)

    if not check_requirements():
        print("\n❌ Requirements not met. Please install Python 3.8+ and Node.js 16+")
        sys.exit(1)

    setup_backend()
    setup_frontend()

    print("\n" + "=" * 50)
    print("✅ Setup complete!")
    print("\n📋 Next steps:")
    print("1. Add your API keys to backend/.env")
    print("2. Terminal 1 - Run backend:")
    print("   cd backend && .venv\\Scripts\\activate && python app.py")
    print("3. Terminal 2 - Run frontend:")
    print("   cd frontend && npm run dev")
    print("\n🌐 Frontend: http://localhost:5173")
    print("🔗 Backend API: http://localhost:4000")

    # Test backend if it's already running
    if test_backend():
        print("\n✅ Backend is running! You can start the frontend now.")
    else:
        print("\n⚠️  Backend not running yet. Start it in a new terminal.")

if __name__ == "__main__":
    main()

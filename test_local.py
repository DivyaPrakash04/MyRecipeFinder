import os
import requests
import json

def test_local_setup():
    """Test the local MyRecipeFinder setup"""

    print("🧪 Testing Local MyRecipeFinder Setup")
    print("=" * 40)

    # Test backend
    print("1. Testing Backend (http://localhost:4000)")
    try:
        response = requests.get("http://localhost:4000/health", timeout=5)
        print(f"   ✅ Health: {response.status_code}")
    except:
        print("   ❌ Backend not running - start with: python app.py")
        return False

    # Test session creation
    try:
        response = requests.post("http://localhost:4000/api/sessions", timeout=5)
        if response.status_code == 200:
            session_id = response.json()["session_id"]
            print(f"   ✅ Session: {response.status_code} (ID: {session_id[:8]}...)")
        else:
            print(f"   ❌ Session: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Session test failed: {e}")
        return False

    # Test chat (without API keys)
    try:
        response = requests.post("http://localhost:4000/api/chat",
                                json={"session_id": session_id, "message": "test", "use_graph": False},
                                timeout=10)
        if response.status_code == 400:
            print("   ✅ Chat: Expected error (no API keys) - this is normal")
        elif response.status_code == 200:
            print("   ✅ Chat: Working with API keys!")
        else:
            print(f"   ⚠️  Chat: {response.status_code}")
    except:
        print("   ❌ Chat test failed")

    # Test frontend
    print("\n2. Testing Frontend (http://localhost:5173)")
    try:
        response = requests.get("http://localhost:5173", timeout=5)
        print(f"   ✅ Frontend: {response.status_code}")
    except:
        print("   ❌ Frontend not running - start with: npm run dev")

    print("\n" + "=" * 40)
    print("📋 Status Summary:")
    print("✅ Backend should be running on port 4000")
    print("✅ Frontend should be running on port 5173")
    print("⚠️  Make sure to add API keys to backend/.env")
    print("🔧 If issues persist, check the console for errors")

if __name__ == "__main__":
    test_local_setup()

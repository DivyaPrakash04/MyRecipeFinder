import os
import sys
import requests

# Test backend connectivity
BACKEND_URL = os.getenv('VITE_API_BASE_URL', 'http://localhost:4000')

def test_backend():
    print(f"🔍 Testing backend at: {BACKEND_URL}")
    print("=" * 50)

    try:
        # Test health endpoint
        response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        print(f"✅ Health check: {response.status_code}")
        print(f"   Response: {response.json()}")
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to backend at {BACKEND_URL}")
        print("   Make sure your backend server is running!")
        return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

    try:
        # Test chat session creation
        response = requests.post(f"{BACKEND_URL}/api/sessions", timeout=10)
        if response.status_code == 200:
            session_id = response.json().get('session_id')
            print(f"✅ Session creation: {response.status_code}")
            print(f"   Session ID: {session_id}")

            # Test chat message
            chat_response = requests.post(f"{BACKEND_URL}/api/chat", json={
                "session_id": session_id,
                "message": "test message",
                "use_graph": False
            }, timeout=30)

            print(f"✅ Chat test: {chat_response.status_code}")
            if chat_response.status_code == 400:
                print("   Expected error (missing API keys) - this is normal if API keys aren't set")
            elif chat_response.status_code == 200:
                print(f"   Success! Response: {chat_response.json()}")
            else:
                print(f"   Unexpected status: {chat_response.status_code}")
                print(f"   Error: {chat_response.text}")
        else:
            print(f"❌ Session creation failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Chat test failed: {e}")

    print("\n" + "=" * 50)
    print("📋 Next Steps:")
    print("1. Make sure your backend is running (python app.py)")
    print("2. Check your .env file for API keys:")
    print("   - COHERE_API_KEY or CO_API_KEY")
    print("   - TAVILY_API_KEY")
    print("3. If using production, verify your Railway/Render deployment")

if __name__ == "__main__":
    test_backend()

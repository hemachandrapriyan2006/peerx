"""
PeerX Live Gemini Test Script
Tests backend environment, Gemini API key loading, and Mentor agent response.
"""

import os
import sys
import logging

# Ensure backend root directory is on Python search path regardless of CWD
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if os.path.exists(os.path.join(CURRENT_DIR, "services")):
    BACKEND_DIR = CURRENT_DIR
elif os.path.exists(os.path.join(CURRENT_DIR, "..", "services")):
    BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
elif os.path.exists(os.path.join(CURRENT_DIR, "backend", "services")):
    BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "backend"))
else:
    BACKEND_DIR = CURRENT_DIR

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_test():
    print("==================================================")
    print("Testing PeerX Live Gemini Integration")
    print("==================================================")

    # 1. Check Configuration & API Key
    from config import settings
    has_key = bool(settings.GEMINI_API_KEY)
    print(f"Gemini API key loaded: {'YES' if has_key else 'NO'}")
    print(f"Gemini Model configured: {settings.GEMINI_MODEL}")

    # 2. Test ai_service
    from services.ai_service import is_mock_mode
    print(f"Mock Mode active: {is_mock_mode()}")

    # 3. Test Mentor Agent
    from agents.mentor import mentor_agent
    test_topic = "Python Functions"
    test_subject = "Python"

    print(f"Mentor topic: {test_topic}")
    print("Gemini request started...")

    try:
        result = mentor_agent.explain(topic=test_topic, subject=test_subject, difficulty=2)
        print(f"Gemini response received: YES")
        
        explanation = result.get("explanation", "")
        print(f"Response length: {len(explanation)}")
        print(f"Result keys: {list(result.keys())}")
        print("\n--- Sample Mentor Output ---")
        print(explanation[:300] + "..." if len(explanation) > 300 else explanation)
        print("----------------------------\n")
        
        if len(explanation) > 0 and "Python" in explanation:
            print("SUCCESS: Live Gemini Mentor test passed!")
            return True
        else:
            print("WARNING: Explanation received but empty or missing expected topic keywords.")
            return False

    except Exception as e:
        print(f"Gemini response received: NO")
        print(f"Error calling Mentor Agent: {e}")
        return False

if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1)

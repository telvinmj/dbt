import os
import sys
import uvicorn
import time
from dotenv import load_dotenv

# Add the parent directory to sys.path so Python can find the backend module
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Load environment variables
load_dotenv()

# Check for Gemini API key
gemini_api_key = os.environ.get("GEMINI_API_KEY")
if not gemini_api_key:
    print("\n⚠️  WARNING: GEMINI_API_KEY environment variable not found!")
    print("AI description generation will be disabled.")
    print("To enable AI descriptions, set your Gemini API key:")
    print("  export GEMINI_API_KEY='your-api-key'\n")
    print("You can get a Gemini API key from: https://makersuite.google.com/app/apikey\n")
    time.sleep(2)  # Give user time to read the message

if __name__ == "__main__":
    # Run the app
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    
    print(f"Starting backend server at http://{host}:{port}")
    uvicorn.run("backend.main:app", host=host, port=port, reload=True)

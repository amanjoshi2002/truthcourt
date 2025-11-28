import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure the two different Gemini instances
GEMINI_KEY_1 = os.getenv('GEMINI_KEY_1')
GEMINI_KEY_2 = os.getenv('GEMINI_KEY_2')

# Configure Google Custom Search API (for web search)
GOOGLE_SEARCH_API = "https://www.googleapis.com/customsearch/v1"
SEARCH_ENGINE_ID = os.getenv('SEARCH_ENGINE_ID')

# Configure debate rounds
ROUNDS = int(os.getenv('ROUNDS', 3))  # Default to 3 rounds if not set
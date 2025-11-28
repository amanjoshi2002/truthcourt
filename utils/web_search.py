import requests
from typing import List, Dict
from config import GOOGLE_SEARCH_API, SEARCH_ENGINE_ID
import os

def perform_web_search(query: str, num_results: int = 3) -> List[Dict]:
    """Perform a web search and return relevant results"""
    try:
        params = {
            'q': query,
            'key': os.getenv('GOOGLE_SEARCH_API_KEY'),
            'cx': SEARCH_ENGINE_ID,
            'num': num_results
        }
        response = requests.get(GOOGLE_SEARCH_API, params=params)
        results = response.json().get('items', [])
        return [{'title': r['title'], 'snippet': r['snippet'], 'link': r['link']} for r in results]
    except Exception as e:
        print(f"Search error: {e}")
        return []
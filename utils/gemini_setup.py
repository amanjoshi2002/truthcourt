import google.generativeai as genai
import time
import random
from functools import wraps

def retry_with_exponential_backoff(max_retries=3, base_delay=1):
    """Decorator to retry API calls with exponential backoff"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if "429" in str(e) or "Resource exhausted" in str(e):
                        if attempt < max_retries - 1:
                            # Exponential backoff with jitter
                            delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                            print(f"Rate limit hit. Retrying in {delay:.2f}s... (attempt {attempt + 1}/{max_retries})")
                            time.sleep(delay)
                        else:
                            print(f"Max retries reached. Error: {e}")
                            raise
                    else:
                        raise
        return wrapper
    return decorator

class RetryGenerativeModel:
    """Wrapper around GenerativeModel with retry logic"""
    def __init__(self, model: genai.GenerativeModel):
        self.model = model
    
    @retry_with_exponential_backoff(max_retries=3, base_delay=2)
    def generate_content(self, prompt: str, **kwargs):
        """Generate content with retry logic"""
        return self.model.generate_content(prompt, **kwargs)

def setup_gemini(api_key: str) -> RetryGenerativeModel:
    """Initialize a Gemini model instance with retry logic"""
    genai.configure(api_key=api_key)
    
    # Configure the model with generation config
    generation_config = {
        "temperature": 0.7,
        "top_p": 1,
        "top_k": 1,
        "max_output_tokens": 2048,
    }
    
    # Create the model with specific configuration
    model = genai.GenerativeModel(
        model_name='gemini-2.0-flash-exp',  # Using experimental for free tier
        generation_config=generation_config
    )
    
    # Wrap with retry logic
    return RetryGenerativeModel(model)
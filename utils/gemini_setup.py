import google.generativeai as genai

def setup_gemini(api_key: str) -> genai.GenerativeModel:
    """Initialize a Gemini model instance"""
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
        model_name='gemini-2.0-flash',  # Using the stable release version
        generation_config=generation_config
    )
    
    return model
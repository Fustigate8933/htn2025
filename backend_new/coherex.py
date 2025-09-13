import os
from dotenv import load_dotenv
import cohere

# Load .env
load_dotenv()

COHERE_API_KEY = os.getenv("COHERE_API_KEY")

if not COHERE_API_KEY:
    raise ValueError("COHERE_API_KEY not found in .env")

# Initialize Cohere client
co = cohere.Client(COHERE_API_KEY)

def generate_speech(user_input, style="humorous", max_tokens=800):
    try:
        # Updated Cohere API call
        response = co.chat(
            model="command",  # Use current recommended model
            message=f"Write a {style} speech about: {user_input}",
            max_tokens=max_tokens
        )
        
        # Get the text response
        speech_text = response.text
        return speech_text

    except cohere.CohereError as e:
        print(f"[Cohere Error] {e}")
        return None
    except Exception as e:
        print(f"[General Error] {e}")
        return None
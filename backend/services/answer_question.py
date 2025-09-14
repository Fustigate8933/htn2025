from pptx import Presentation
from PyPDF2 import PdfReader
from generate_speech import generate_speech
from google.cloud import storage
import io
import time
import json
from cloudfare_audio_to_text import cloudfare_audio_to_text
from file_to_speech import PPTProcessor
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

def answer_prompt(ppt_text, question):
    """
    Build the prompt to send to cohere API based on the extracted text
    """
    prompt = (
        f"You are answering a live audience question during a presentation."
        "Use the PowerPoint slide content provided as your reference. Respond in a short, clear, and conversational way—like you're speaking directly to the audience."
        "Focus only on the key idea from the slide that answers the question."
        "If explanation is needed, use simple everyday language and a quick example."
        "Do not give long background or summaries."
        f"Slide content:\n{ppt_text['text']}\n\n"
        f"Audience question:\n{question}\n\n"
    )
    return prompt

def generate_answer(style="humorous", max_tokens=50):
    ppt_processor = PPTProcessor()
    PAGE_NUM = 1
    ppt_path = "/Users/hanyunguo/Downloads/New Folder With Items/test.pptx"
    audio_path = "/Users/hanyunguo/Downloads/New Folder With Items/question.mp3"
    ppt_text = ppt_processor.extract_ppt_text(ppt_path)
    transcript = cloudfare_audio_to_text(audio_path)
    question = json.loads(transcript.body).get("speech-to-text", "")
    prompt = answer_prompt(ppt_text[PAGE_NUM], question)
    print(f"Generated answer for speech {PAGE_NUM}:\n{prompt}\n")

    try:
        # Updated Cohere API call
        response = co.chat(
            model="command",  # Use current recommended model
            message=prompt,
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
    
    return generate_speech

if __name__ == "__main__":
    print(generate_answer())
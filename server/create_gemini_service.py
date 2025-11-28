#!/usr/bin/env python3
"""Script to create the complete gemini_service.py file with all language support"""

content = '''import os
from dotenv import load_dotenv
import google.generativeai as genai
from google.cloud import texttospeech
import base64
import traceback

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

class GeminiService:
    def __init__(self):
        # Use full path for credentials
        creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if creds_path and not os.path.isabs(creds_path):
            creds_path = os.path.join(os.path.dirname(__file__), creds_path)
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = creds_path
            print(f"Credentials path: {creds_path}")
            
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        try:
            self.tts_client = texttospeech.TextToSpeechClient()
            print("TTS Client initialized successfully")
        except Exception as e:
            print(f"TTS Client init error: {e}")
            traceback.print_exc()
            self.tts_client = None
        
    def generate_question(self, difficulty="Medium", language="English", job_role="Telesales", question_number=1, total_questions=5):
        """Generate interview question using Gemini"""
        try:
            # Determine if this should be difficult or normal based on question number
            actual_difficulty = "Difficult" if question_number <= 3 else "Normal"
            
            # Base prompt
            base_prompt = f"""You are conducting a job interview for a {job_role} position at matrimony.com.
            
Generate interview question #{question_number} of {total_questions}.
Difficulty level: {actual_difficulty}

Job Role: {job_role} at matrimony.com (matchmaking/matrimonial services company)

Question Requirements:
- For DIFFICULT questions: Ask about handling objections, complex sales scenarios, persuasion techniques, or challenging customer situations
- For NORMAL questions: Ask about basic sales skills, customer service, communication, or motivation
- Keep questions practical and relevant to telesales in the matrimonial industry
- Questions should be answerable in 30-60 seconds
- Make it conversational and realistic"""

            # Language-specific instructions
            lang_lower = language.lower()
            
            if lang_lower == "tamil":
                prompt = base_prompt + """

TAMIL LANGUAGE STYLE REQUIREMENTS:
- Use simple everyday spoken Tamil
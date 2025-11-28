import os
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
    
    def generate_greeting(self, candidate_name, job_title, language="English"):
        """Generate personalized greeting for interview start"""
        greetings = {
            "english": f"Hello {candidate_name}! Congratulations on being selected for the {job_title} position at matrimony.com. I'm excited to conduct your interview today. Let's begin with a few questions to understand your qualifications better.",
            "tamil": f"வணக்கம் {candidate_name}! matrimony.com-ல் {job_title} position-க்கு நீங்க select ஆகிட்டீங்க, வாழ்த்துக்கள்! இன்னைக்கு உங்க interview-ஐ நடத்த போறேன். உங்க qualification-ஐ நல்லா புரிஞ்சுக்க சில questions கேக்கலாம்.",
            "hindi": f"नमस्ते {candidate_name}! matrimony.com में {job_title} position के लिए आपका selection हुआ है, बधाई हो! आज मैं आपका interview लूंगा। चलिए कुछ questions से शुरू करते हैं।",
            "telugu": f"నమస్కారం {candidate_name}! matrimony.com లో {job_title} position కి మీరు select అయ్యారు, అభినందనలు! ఈరోజు మీ interview నేను conduct చేస్తాను. మీ qualifications గురించి కొన్ని questions అడుగుదాం.",
            "kannada": f"ನಮಸ್ಕಾರ {candidate_name}! matrimony.com ನಲ್ಲಿ {job_title} position ಗೆ ನೀವು select ಆಗಿದ್ದೀರಿ, ಅಭಿನಂದನೆಗಳು! ಇಂದು ನಾನು ನಿಮ್ಮ interview ಅನ್ನು conduct ಮಾಡುತ್ತೇನೆ. ನಿಮ್ಮ qualifications ಬಗ್ಗೆ ಕೆಲವು questions ಕೇಳೋಣ."
        }
        
        return greetings.get(language.lower(), greetings["english"])

        
    def generate_question(self, difficulty="Medium", language="English", job_role="Telesales", question_number=1, total_questions=5, question_type="technical"):
        """Generate interview question using Gemini - supports English, Tamil, Hindi, Telugu, Kannada"""
        try:
            # Determine difficulty based on question number
            actual_difficulty = "Difficult" if question_number <= 3 else "Normal"
            
            # Question type specific prompts
            type_prompts = {
                "resume": "Ask about their past experience, skills, education, or work history mentioned in their resume",
                "technical": "Ask about technical skills, job-specific knowledge, problem-solving abilities, or industry expertise",
                "hr": "Ask about their motivation, career goals, cultural fit, work style, or behavioral aspects"
            }
            
            type_instruction = type_prompts.get(question_type.lower(), type_prompts["technical"])
            
            # Base prompt for all languages
            base_prompt = f"""You are conducting a job interview for a {job_role} position at matrimony.com.
            
Generate interview question #{question_number} of {total_questions}.
Question Type: {question_type.upper()}
Difficulty level: {actual_difficulty}

Job Role: {job_role} at matrimony.com (matchmaking/matrimonial services company)

Question Requirements:
- {type_instruction}
- For DIFFICULT questions: Ask about handling objections, complex scenarios, or challenging situations
- For NORMAL questions: Ask about basic skills, experience, or motivation
- Keep questions practical and relevant to {job_role} in the matrimonial industry
- Questions should be answerable in 30-60 seconds
- Make it conversational and realistic"""

            # Add language-specific instructions
            lang_lower = language.lower()
            
            if lang_lower == "tamil":
                prompt = base_prompt + """

TAMIL LANGUAGE STYLE REQUIREMENTS:
- Use simple everyday spoken Tamil (NOT too pure Tamil, NOT formal, NOT slang)
- Prefer natural forms like "உங்களுக்கு", "உங்க", "கொஞ்சம்", "சரி", "பாருங்க"
- Avoid formal words like "உங்களிடம்", "இத்தகவல்", "எனினும்", "ஆயினும்"
- You may mix common Tanglish terms (experience, shift, performance, confirm, role, customer, service, etc.)
- Sound like a friendly, professional HR interviewer (no district slang or buddy tone)
- Absolutely NO filler sounds or hesitation
- Keep sentences short, clear, steady
- Use polite pronouns ("நீங்கள்", "தயவு செய்து") without sounding stiff

Generate ONLY the Tamil question text, no additional formatting or labels."""
            
            elif lang_lower == "hindi":
                prompt = base_prompt + """

HINDI LANGUAGE STYLE REQUIREMENTS:
- Use simple conversational Hindi (NOT overly formal, NOT pure Sanskrit-heavy Hindi)
- Mix common English terms naturally (experience, customer, service, sales, target, etc.)
- Sound like a friendly, professional HR interviewer
- Use polite forms: "आप", "आपका", "कृपया"
- Avoid overly formal words like "आपसे निवेदन है", "सादर"
- Keep sentences clear and natural
- NO filler sounds or hesitation

Generate ONLY the Hindi question text, no additional formatting or labels."""
            
            elif lang_lower == "telugu":
                prompt = base_prompt + """

TELUGU LANGUAGE STYLE REQUIREMENTS:
- Use simple conversational Telugu (NOT overly formal or literary Telugu)
- Mix common English terms naturally (experience, customer, service, sales, etc.)
- Sound like a friendly, professional HR interviewer
- Use polite forms: "మీరు", "మీ", "దయచేసి"
- Keep sentences clear and natural
- NO filler sounds or hesitation

Generate ONLY the Telugu question text, no additional formatting or labels."""
            
            elif lang_lower == "kannada":
                prompt = base_prompt + """

KANNADA LANGUAGE STYLE REQUIREMENTS:
- Use simple conversational Kannada (NOT overly formal or literary Kannada)
- Mix common English terms naturally (experience, customer, service, sales, etc.)
- Sound like a friendly, professional HR interviewer
- Use polite forms: "ನೀವು", "ನಿಮ್ಮ", "ದಯವಿಟ್ಟು"
- Keep sentences clear and natural
- NO filler sounds or hesitation

Generate ONLY the Kannada question text, no additional formatting or labels."""
            
            else:  # English
                prompt = base_prompt + """

Language: English
Generate ONLY the question text, no additional formatting or labels."""

            # Generate with optimized settings
            generation_config = {
                'temperature': 0.7,
                'max_output_tokens': 150,
                'top_p': 0.9,
                'top_k': 40
            }
            
            response = self.model.generate_content(prompt, generation_config=generation_config)
            question_text = response.text.strip().replace('"', '').replace("'", "").strip()
            
            print(f"✅ Generated {actual_difficulty} question #{question_number} in {language}: {question_text[:100]}...")
            
            return question_text
            
        except Exception as e:
            print(f"❌ Error generating question: {e}")
            traceback.print_exc()
            
            # Fallback questions by language
            fallback_questions = {
                "tamil": {
                    1: "உங்களுக்கு telesales-la என்ன மாதிரியான experience இருக்கு?",
                    2: "ஒரு customer உங்க service-ஐ நம்பலைன்னா, நீங்க எப்படி handle பண்ணுவீங்க?",
                    3: "premium membership வாங்க தயங்கற customer-ஐ நீங்க எப்படி convince பண்ணுவீங்க?",
                    4: "matrimony industry-la telesales job ஏன் பண்ண விரும்புறீங்க?",
                    5: "நிறைய rejection வந்தாலும் எப்படி motivated-ஆ இருப்பீங்க?"
                },
                "hindi": {
                    1: "आपको telesales में किस तरह का experience है?",
                    2: "अगर कोई customer आपकी service पर भरोसा नहीं करता, तो आप कैसे handle करेंगे?",
                    3: "जो customer premium membership लेने में हिचकिचा रहा है, उसे आप कैसे convince करेंगे?",
                    4: "आप matrimony industry में telesales job क्यों करना चाहते हैं?",
                    5: "बहुत सारे rejection के बाद भी आप कैसे motivated रहेंगे?"
                },
                "telugu": {
                    1: "మీకు telesales లో ఎలాంటి experience ఉంది?",
                    2: "ఒక customer మీ service ని నమ్మకపోతే, మీరు ఎలా handle చేస్తారు?",
                    3: "premium membership కొనడానికి망설ిస్తున్న customer ని మీరు ఎలా convince చేస్తారు?",
                    4: "మీరు matrimony industry లో telesales job ఎందుకు చేయాలనుకుంటున్నారు?",
                    5: "చాలా rejection లు వచ్చినా మీరు ఎలా motivated గా ఉంటారు?"
                },
                "kannada": {
                    1: "ನಿಮಗೆ telesales ನಲ್ಲಿ ಯಾವ ರೀತಿಯ experience ಇದೆ?",
                    2: "ಒಬ್ಬ customer ನಿಮ್ಮ service ಅನ್ನು ನಂಬದಿದ್ದರೆ, ನೀವು ಹೇಗೆ handle ಮಾಡುತ್ತೀರಿ?",
                    3: "premium membership ತೆಗೆದುಕೊಳ್ಳಲು망설ುತ್ತಿರುವ customer ಅನ್ನು ನೀವು ಹೇಗೆ convince ಮಾಡುತ್ತೀರಿ?",
                    4: "ನೀವು matrimony industry ನಲ್ಲಿ telesales job ಏಕೆ ಮಾಡಲು ಬಯಸುತ್ತೀರಿ?",
                    5: "ಬಹಳಷ್ಟು rejection ಗಳು ಬಂದರೂ ನೀವು ಹೇಗೆ motivated ಆಗಿ ಇರುತ್ತೀರಿ?"
                },
                "english": {
                    1: "What kind of experience do you have in telesales?",
                    2: "How would you handle a customer who doesn't trust your service?",
                    3: "How would you convince a customer who is hesitant to buy premium membership?",
                    4: "Why do you want to work in telesales in the matrimony industry?",
                    5: "How do you stay motivated despite facing many rejections?"
                }
            }
            
            lang_fallback = fallback_questions.get(lang_lower, fallback_questions["english"])
            return lang_fallback.get(question_number, "Tell me about your experience.")

    
    def text_to_speech(self, text, language='english'):
        """Convert text to speech using Google Cloud TTS with Chirp 3 HD model"""
        if not self.tts_client:
            print("⚠️ TTS client not available - skipping audio generation")
            return None
            
        try:
            # Map language to voice codes
            voice_map = {
                'tamil': 'ta-IN',
                'hindi': 'hi-IN',
                'english': 'en-US',
                'telugu': 'te-IN',
                'kannada': 'kn-IN'
            }
            
            lang_code = voice_map.get(language.lower(), 'en-US')
            print(f"🔊 Generating TTS for language: {lang_code} using Chirp 3 HD")
            
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            # Chirp 3 HD voice names by language
            chirp_voices = {
                'en-US': 'en-US-Chirp3-HD-Aoede',
                'ta-IN': 'ta-IN-Chirp3-HD-Aoede',
                'hi-IN': 'hi-IN-Chirp3-HD-Aoede',
                'te-IN': 'te-IN-Chirp3-HD-Aoede',
                'kn-IN': 'kn-IN-Chirp3-HD-Aoede'
            }
            
            voice_name = chirp_voices.get(lang_code, 'en-US-Chirp3-HD-Aoede')
            
            voice = texttospeech.VoiceSelectionParams(
                language_code=lang_code,
                name=voice_name
            )
            
            # Audio config for high quality
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=1.0,
                pitch=0.0,
                effects_profile_id=['headphone-class-device'],
                sample_rate_hertz=24000
            )
            
            # Generate speech
            response = self.tts_client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            
            # Return base64 encoded audio
            audio_base64 = base64.b64encode(response.audio_content).decode('utf-8')
            print(f"✅ Chirp 3 HD TTS generated successfully for {lang_code}")
            return audio_base64
            
        except Exception as e:
            print(f"❌ TTS Error: {e}")
            traceback.print_exc()
            
            # Fallback to standard voices
            try:
                print("⚠️ Falling back to standard TTS voices...")
                
                synthesis_input = texttospeech.SynthesisInput(text=text)
                
                voice = texttospeech.VoiceSelectionParams(
                    language_code=lang_code,
                    ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
                )
                
                audio_config = texttospeech.AudioConfig(
                    audio_encoding=texttospeech.AudioEncoding.MP3,
                    speaking_rate=1.0,
                    pitch=0.0
                )
                
                response = self.tts_client.synthesize_speech(
                    input=synthesis_input,
                    voice=voice,
                    audio_config=audio_config
                )
                
                audio_base64 = base64.b64encode(response.audio_content).decode('utf-8')
                print(f"✅ Fallback TTS generated successfully")
                return audio_base64
                
            except Exception as fallback_error:
                print(f"❌ Fallback TTS Error: {fallback_error}")
                traceback.print_exc()
                return None

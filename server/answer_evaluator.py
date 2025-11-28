"""
Answer Evaluator Service
Uses AI to evaluate candidate answers and generate scores and feedback
"""

import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))


class AnswerEvaluator:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    def evaluate_answer(self, question: str, answer_text: str, job_role: str = "Telesales") -> dict:
        """
        Evaluate a candidate's answer to an interview question
        
        Args:
            question: The interview question asked
            answer_text: The candidate's answer (from transcript)
            job_role: The job role being interviewed for
            
        Returns:
            dict: {
                'score': float (0-5),
                'verdict': str,
                'strengths': list[str],
                'weaknesses': list[str]
            }
        """
        try:
            prompt = f"""You are an expert HR interviewer evaluating a candidate's answer for a {job_role} position.

Question Asked:
{question}

Candidate's Answer:
{answer_text}

Evaluate this answer on a scale of 0-5 based on:
1. Relevance to the question (25%)
2. Clarity and communication (25%)
3. Depth and detail (25%)
4. Practical experience/examples (25%)

Scoring Guide:
- 5.0: Excellent - Clear, detailed, relevant, with good examples
- 4.0: Good - Mostly clear and relevant, some details
- 3.0: Average - Basic answer, lacks depth or clarity
- 2.0: Below Average - Vague, off-topic, or incomplete
- 1.0: Poor - Barely addresses the question
- 0.0: No answer or completely irrelevant

Return ONLY valid JSON with this exact structure:
{{
  "score": 4.5,
  "verdict": "Brief explanation of the score (2-3 sentences)",
  "strengths": ["Strength 1", "Strength 2"],
  "weaknesses": ["Weakness 1", "Weakness 2"]
}}

Return ONLY the JSON, no additional text."""

            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Clean up response
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            # Parse JSON
            result = json.loads(response_text)
            
            # Validate score
            score = float(result.get('score', 0))
            score = max(0.0, min(5.0, score))
            result['score'] = score
            
            # Ensure required fields
            if 'verdict' not in result:
                result['verdict'] = "Unable to generate verdict"
            if 'strengths' not in result or not isinstance(result['strengths'], list):
                result['strengths'] = []
            if 'weaknesses' not in result or not isinstance(result['weaknesses'], list):
                result['weaknesses'] = []
            
            print(f"Answer evaluated: Score {score}/5")
            return result
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Response text: {response_text}")
            return {
                'score': 0.0,
                'verdict': "Unable to evaluate answer due to processing error",
                'strengths': [],
                'weaknesses': []
            }
        except Exception as e:
            print(f"Error evaluating answer: {e}")
            import traceback
            traceback.print_exc()
            return {
                'score': 0.0,
                'verdict': f"Error: {str(e)}",
                'strengths': [],
                'weaknesses': []
            }
    
    def extract_topics_from_answers(self, answers_data: list) -> dict:
        """
        Extract topics/skills from questions and map them to scores
        
        Args:
            answers_data: List of dicts with {question, answer, score, verdict}
            
        Returns:
            dict: {
                'topics': [{'topic': str, 'score': float, 'max': float}],
                'topic_analysis': str
            }
        """
        try:
            # Prepare questions summary
            questions_summary = "\n".join([
                f"Q{idx+1} (Score: {ans.get('score', 0)}/5): {ans.get('question', 'N/A')}"
                for idx, ans in enumerate(answers_data)
            ])
            
            prompt = f"""Analyze these interview questions and extract the key topics/skills being evaluated.

Questions and Scores:
{questions_summary}

Extract 5-7 main topics/skills that these questions are testing. For each topic, calculate an average score based on the questions that relate to it.

Return ONLY valid JSON with this exact structure:
{{
  "topics": [
    {{"topic": "PROBLEM SOLVING", "score": 4.5, "max": 5}},
    {{"topic": "COMMUNICATION SKILLS", "score": 3.0, "max": 5}},
    {{"topic": "TECHNICAL KNOWLEDGE", "score": 4.0, "max": 5}}
  ]
}}

Rules:
- Topic names should be in UPPERCASE
- Score should be the average of related questions
- Max is always 5
- Return 5-7 topics minimum

Return ONLY the JSON, no additional text."""

            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Clean up response
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            result = json.loads(response_text)
            
            print(f"Extracted {len(result.get('topics', []))} topics from questions")
            return result
            
        except Exception as e:
            print(f"Error extracting topics: {e}")
            import traceback
            traceback.print_exc()
            # Return default topics based on scores
            return {
                'topics': [
                    {'topic': f'QUESTION {idx+1}', 'score': ans.get('score', 0), 'max': 5}
                    for idx, ans in enumerate(answers_data)
                ]
            }
    
    def generate_overall_feedback(self, answers_data: list) -> dict:
        """
        Generate overall interview feedback based on all answers
        
        Args:
            answers_data: List of dicts with {question, answer, score, verdict}
            
        Returns:
            dict: {
                'overall_feedback': str,
                'detailed_feedback': str,
                'overall_score': float,
                'overall_score_percent': float
            }
        """
        try:
            # Calculate overall score
            total_score = sum(a.get('score', 0) for a in answers_data)
            max_score = len(answers_data) * 5.0
            overall_score = total_score
            overall_score_percent = (total_score / max_score * 100) if max_score > 0 else 0
            
            # Extract topics first
            topics_result = self.extract_topics_from_answers(answers_data)
            
            # Prepare summary for AI
            summary = f"Interview Summary:\n"
            summary += f"Total Questions: {len(answers_data)}\n"
            summary += f"Overall Score: {overall_score:.1f}/{max_score:.1f} ({overall_score_percent:.1f}%)\n\n"
            
            for idx, ans in enumerate(answers_data, 1):
                summary += f"Q{idx}: {ans.get('question', 'N/A')}\n"
                summary += f"Answer: {ans.get('answer_text', 'N/A')[:200]}...\n"
                summary += f"Score: {ans.get('score', 0)}/5\n"
                summary += f"Verdict: {ans.get('verdict', 'N/A')}\n\n"
            
            # Add topic breakdown
            summary += "\nTopic-wise Performance:\n"
            for topic in topics_result.get('topics', []):
                summary += f"- {topic['topic']}: {topic['score']}/{topic['max']}\n"
            
            prompt = f"""You are an expert HR interviewer providing final feedback for a candidate.

{summary}

Generate comprehensive feedback with:
1. Overall Assessment (4-5 sentences summarizing the candidate's overall performance, highlighting key strengths and areas for improvement)
2. Detailed Feedback (6-8 sentences with:
   - Specific observations about their strongest topics
   - Areas where they struggled
   - Communication quality
   - Confidence level
   - Specific recommendations for improvement
   - Overall suitability for the role)

Return ONLY valid JSON with this exact structure:
{{
  "overall_feedback": "Overall assessment here...",
  "detailed_feedback": "Detailed feedback here...",
  "key_strengths": ["Strength 1", "Strength 2", "Strength 3"],
  "areas_for_improvement": ["Area 1", "Area 2"],
  "confidence_level": "High/Medium/Low",
  "communication_quality": "Excellent/Good/Average/Poor",
  "suitability_score": 75
}}

Return ONLY the JSON, no additional text."""

            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Clean up response
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            # Parse JSON
            result = json.loads(response_text)
            
            result['overall_score'] = overall_score
            result['overall_score_percent'] = overall_score_percent
            result['topics'] = topics_result.get('topics', [])
            
            print(f"Overall feedback generated: {overall_score_percent:.1f}%")
            return result
            
        except Exception as e:
            print(f"Error generating overall feedback: {e}")
            import traceback
            traceback.print_exc()
            return {
                'overall_feedback': "Unable to generate overall feedback",
                'detailed_feedback': "Unable to generate detailed feedback",
                'overall_score': overall_score if 'overall_score' in locals() else 0.0,
                'overall_score_percent': overall_score_percent if 'overall_score_percent' in locals() else 0.0
            }


# Test function
if __name__ == "__main__":
    evaluator = AnswerEvaluator()
    
    # Test evaluation
    question = "How would you handle a customer who is skeptical about online matrimonial services?"
    answer = "I would first listen to their concerns carefully, then explain the benefits of our service with real success stories. I would also offer them a free trial to experience the platform."
    
    result = evaluator.evaluate_answer(question, answer)
    print(json.dumps(result, indent=2))

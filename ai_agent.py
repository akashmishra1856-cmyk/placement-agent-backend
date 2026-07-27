import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)


def analyze_gap(student_skills: str, required_skills: str, cgpa: float, min_cgpa: float, quiz_score, interview_status):
    prompt = f"""
You are a placement readiness advisor for a college student.

Student's current skills: {student_skills}
Company's required skills: {required_skills}
Student's CGPA: {cgpa} (required: {min_cgpa})
Quiz score: {quiz_score}
Interview status: {interview_status}

Give the student a short, friendly, encouraging improvement plan (3-4 bullet points max) 
to become placement-ready. Be specific and practical.
"""

    response = client.models.generate_content(
        model="gemini-flash-latest",
        contents=prompt
    )

    return response.text

def generate_interview_question(role: str, student_skills: str, conversation_history: str):
    prompt = f"""
You are a friendly placement interviewer conducting a mock interview.

Role being interviewed for: {role}
Candidate's skills: {student_skills}
Conversation so far: {conversation_history if conversation_history else "This is the first question."}

Ask ONE relevant interview question for this role. Keep it natural and conversational.
Return ONLY the question, nothing else.
"""

    response = client.models.generate_content(
        model="gemini-flash-latest",
        contents=prompt
    )

    return response.text.strip()


def generate_interview_feedback(conversation_history: str):
    prompt = f"""
You are reviewing a completed mock placement interview.

Full conversation:
{conversation_history}

Give a short feedback summary (2-3 sentences) covering the candidate's communication skills 
and technical depth. Be honest but encouraging.
"""

    response = client.models.generate_content(
        model="gemini-flash-latest",
        contents=prompt
    )

    return response.text.strip()

def grade_quiz_answer(question_text: str, student_answer: str):
    prompt = f"""
You are grading a placement-readiness quiz answer.

Question: {question_text}
Student's Answer: {student_answer}

Score this answer from 0 to 10 based on correctness and clarity.
Return ONLY the number, nothing else. No explanation, no words, just the digit(s).
"""

    response = client.models.generate_content(
        model="gemini-flash-latest",
        contents=prompt
    )

    result_text = response.text.strip()

    # Sirf number nikaalne ki koshish karo, agar AI ne extra text de diya
    try:
        score = int(''.join(filter(str.isdigit, result_text))[:2] or 0)
        score = min(score, 10)  # kabhi bhi 10 se zyada na ho
    except:
        score = 0

    return score
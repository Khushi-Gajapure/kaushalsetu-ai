import json
import os

from openai import OpenAI


def generate_quiz_questions(text, number_of_questions=5):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    prompt = f"""
You are an educational quiz generator for the KaushalSetu AI platform.

Generate {number_of_questions} multiple-choice questions from the
learning material below.

IMPORTANT:
- Use ONLY information supported by the supplied learning material.
- Do not invent facts.
- Each question must have exactly four options.
- correct_answer must be one of: A, B, C, D.
- Include a short explanation.
- difficulty must be Beginner, Medium, or Hard.
- competency should describe the skill/topic tested.

Return ONLY valid JSON in this format:

{{
    "questions": [
        {{
            "question": "Question text",
            "option_a": "Option A",
            "option_b": "Option B",
            "option_c": "Option C",
            "option_d": "Option D",
            "correct_answer": "A",
            "explanation": "Why this answer is correct.",
            "difficulty": "Medium",
            "competency": "Operating Systems"
        }}
    ]
}}

LEARNING MATERIAL:
{text}
"""

    response = client.responses.create(
        model="gpt-5.6-luna",
        input=prompt,
    )

    result = response.output_text

    return json.loads(result)
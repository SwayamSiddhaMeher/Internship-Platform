import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("AI_API_KEY")
)


def generate_mcqs_with_ai(skill, number_of_questions, difficulty):

    prompt = f"""
You are an educational assessment generator.

Generate {number_of_questions} multiple-choice questions
for the skill: {skill}

Difficulty: {difficulty}

Requirements:

1. Generate exactly {number_of_questions} questions.
2. Each question must have exactly 4 options.
3. Options must be A, B, C and D.
4. Each question must have exactly one correct answer.
5. The questions must test actual knowledge of {skill}.
6. Do not repeat questions.
7. The correct answer must be one of A, B, C or D.
8. Difficulty must be Easy, Medium, or Hard.
9. Return ONLY valid JSON.
10. Do not include markdown.
11. Do not include explanations.

Return the result in exactly this format:

[
    {{
        "question": "Question text",
        "option_a": "Option A",
        "option_b": "Option B",
        "option_c": "Option C",
        "option_d": "Option D",
        "correct_answer": "B",
        "difficulty": "Easy"
    }}
]
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You generate valid educational MCQs in JSON format."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.7
    )

    content = response.choices[0].message.content

    try:
        questions = json.loads(content)
    except json.JSONDecodeError:
        raise Exception("AI returned invalid JSON.")

    # Validate that AI returned a list
    if not isinstance(questions, list):
        raise Exception("AI response must be a list of questions.")

    # Validate number of questions
    if len(questions) != number_of_questions:
        raise Exception(
            f"AI returned {len(questions)} questions instead of "
            f"{number_of_questions}."
        )

    required_fields = [
        "question",
        "option_a",
        "option_b",
        "option_c",
        "option_d",
        "correct_answer",
        "difficulty"
    ]

    valid_difficulties = ["Easy", "Medium", "Hard"]
    valid_answers = ["A", "B", "C", "D"]

    seen_questions = set()

    for question in questions:

        # Check required fields
        for field in required_fields:
            if field not in question:
                raise Exception(
                    f"Missing field '{field}' in AI response."
                )

        # Check duplicate questions
        question_text = question["question"].strip().lower()

        if question_text in seen_questions:
            raise Exception("AI generated duplicate questions.")

        seen_questions.add(question_text)

        # Check correct answer
        if question["correct_answer"] not in valid_answers:
            raise Exception(
                "Correct answer must be A, B, C or D."
            )

        # Check difficulty
        if question["difficulty"] not in valid_difficulties:
            raise Exception(
                "Difficulty must be Easy, Medium or Hard."
            )

        # Check options
        options = [
            question["option_a"],
            question["option_b"],
            question["option_c"],
            question["option_d"]
        ]

        if any(not option or not option.strip() for option in options):
            raise Exception("All four options must contain text.")

    return questions
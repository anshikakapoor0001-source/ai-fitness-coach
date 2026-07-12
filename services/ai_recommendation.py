import os

from dotenv import load_dotenv
from google import genai


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY must be set before starting the application.")

client = genai.Client(api_key=api_key)


def generate_plan(name, age, height, weight, bmi, goal):
    """Generate a consistently structured, general-wellness fitness plan."""
    prompt = f"""
You are an expert AI Fitness Coach. Provide general wellness guidance only.
Do not diagnose medical conditions or make medical claims. Encourage the user to
consult a qualified professional for injuries, chronic conditions, or concerns.

Create a personalized fitness plan for this user:
Name: {name}
Age: {age}
Height: {height} cm
Weight: {weight} kg
BMI: {bmi}
Goal: {goal}

Return the response exactly with these Markdown headings:

## AI Recommendation
Write a short, supportive recommendation in 4–6 lines.

## Diet Plan
Breakfast:
Mid-Morning Snack:
Lunch:
Evening Snack:
Dinner:
Water Intake:

## Workout Plan
Monday:
Tuesday:
Wednesday:
Thursday:
Friday:
Saturday:
Sunday: Rest and recovery
"""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    text = (response.text or "").strip()
    if not text:
        raise RuntimeError("The AI coach returned an empty response.")
    return text

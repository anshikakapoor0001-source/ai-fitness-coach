import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def generate_plan(name, age, height, weight, bmi, goal):

    prompt = f"""
You are an expert fitness coach and certified dietitian.

Generate a personalized fitness plan for the following user.

Name: {name}
Age: {age}
Height: {height} cm
Weight: {weight} kg
BMI: {bmi}
Goal: {goal}

Provide:

1. BMI Analysis

2. Personalized Diet Plan
- Breakfast
- Lunch
- Snacks
- Dinner

3. Personalized Workout Plan
- Warm-up
- Main Workout
- Cool Down

4. Health Tips

Keep the response simple, beginner friendly and under 300 words.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text
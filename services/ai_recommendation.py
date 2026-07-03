import os
from urllib import response

from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def generate_plan(name, age, height, weight, bmi, goal):

   prompt = f"""
You are an expert AI Fitness Coach.

Generate a personalized fitness plan for the following user.

Name: {name}
Age: {age}
Height: {height} cm
Weight: {weight} kg
BMI: {bmi}
Goal: {goal}

Return the response EXACTLY in the following format.

## AI Recommendation
(Write a short motivational recommendation in 5-6 lines.)

## Diet Plan

Breakfast:
...

Mid-Morning Snack:
...

Lunch:
...

Evening Snack:
...

Dinner:
...

Water Intake:
...

## Workout Plan

Monday:
...

Tuesday:
...

Wednesday:
...

Thursday:
...

Friday:
...

Saturday:
...

Sunday:
Rest and Recovery
"""
   response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

   return response.text.strip()
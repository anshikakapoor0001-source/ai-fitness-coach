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

Format the entire response as clean GitHub-flavored Markdown.
- Do not wrap the response in a code block.
- Do not escape Markdown characters.
- Put a blank line after every heading.
- Put a blank line before every bullet list.
- Use real Markdown bullets with "- "; do not write dense label-only paragraphs.
- Keep the exact top-level headings shown below so the app can split the plan.

Create a personalized fitness plan for this user:
Name: {name}
Age: {age}
Height: {height} cm
Weight: {weight} kg
BMI: {bmi}
Goal: {goal}

Return the response exactly with these Markdown headings:

## AI Recommendation

- Write 4 to 6 concise bullet points.
- Make each bullet one practical sentence.
- Use **bold** for the most important habit or warning.

## Diet Plan

### Breakfast

- Give 1 practical meal idea.

### Mid-Morning Snack

- Give 1 practical snack idea.

### Lunch

- Give 1 balanced meal idea.

### Evening Snack

- Give 1 light snack idea.

### Dinner

- Give 1 balanced dinner idea.

### Water Intake

- Give a realistic hydration target.

## Workout Plan

### Monday

- Give the workout for Monday.

### Tuesday

- Give the workout for Tuesday.

### Wednesday

- Give the workout for Wednesday.

### Thursday

- Give the workout for Thursday.

### Friday

- Give the workout for Friday.

### Saturday

- Give the workout for Saturday.

### Sunday

- Rest and recovery.
"""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    text = (response.text or "").strip()
    if not text:
        raise RuntimeError("The AI coach returned an empty response.")
    return text

def get_diet_plan(goal, bmi_category):
    """Return a simple, general-purpose food plan when AI is unavailable."""
    if goal == "Weight Loss" and bmi_category in {"Overweight", "Obese"}:
        return [
            "- **Breakfast:** Oats with milk and an apple",
            "- **Lunch:** Brown rice, dal, and a large salad",
            "- **Snack:** A small handful of mixed nuts",
            "- **Dinner:** Chapati with vegetables and protein",
            "- **Hydration:** Aim for at least 3 litres of water",
        ]
    if goal == "Muscle Gain":
        return [
            "- **Breakfast:** Eggs or paneer, milk, and a banana",
            "- **Lunch:** Chicken or paneer, rice, and vegetables",
            "- **Snack:** Greek yogurt or a protein shake",
            "- **Dinner:** Dal, rice, vegetables, and paneer",
            "- **Hydration:** Aim for 3-4 litres of water",
        ]
    return [
        "- Build meals around vegetables, fruit, protein, and whole grains",
        "- Include a protein source with every main meal",
        "- Choose water regularly throughout the day",
        "- Keep treats enjoyable and occasional rather than forbidden",
    ]

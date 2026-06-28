def get_diet_plan(goal, bmi_category):

    if goal == "Weight Loss":

        if bmi_category == "Obese" or bmi_category == "Overweight":
            return [
                "🥣 Breakfast: Oats + Milk + Apple",
                "🍛 Lunch: Brown Rice + Dal + Salad",
                "🥜 Snack: Mixed Nuts",
                "🍲 Dinner: Chapati + Vegetables",
                "💧 Drink at least 3L of water"
            ]

        else:
            return [
                "🥣 Breakfast: Oats + Banana",
                "🍛 Lunch: Rice + Dal + Vegetables",
                "🍎 Snack: Fruit",
                "🍲 Dinner: Soup + Salad"
            ]

    elif goal == "Muscle Gain":

        return [
            "🥚 Breakfast: Eggs + Milk + Banana",
            "🍗 Lunch: Chicken/Paneer + Rice",
            "🥛 Snack: Protein Shake",
            "🍚 Dinner: Rice + Dal + Paneer",
            "💧 Drink 3–4L of water"
        ]

    else:

        return [
            "🍎 Eat a balanced diet",
            "🥗 Include fruits and vegetables",
            "🥛 Drink enough water",
            "🍚 Eat protein with every meal"
        ]
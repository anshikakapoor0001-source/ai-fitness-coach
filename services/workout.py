def get_workout_plan(goal):
    """Return a beginner-friendly routine when AI is unavailable."""
    if goal == "Weight Loss":
        return [
            "- **Brisk walk:** 30 minutes",
            "- **Jog or cycle:** 20 minutes, at a comfortable effort",
            "- **Jumping jacks:** 3 sets",
            "- **Bodyweight squats:** 3 sets",
            "- **Cool-down stretching:** 10 minutes",
        ]
    if goal == "Muscle Gain":
        return [
            "- **Warm-up walk:** 10 minutes",
            "- **Push-ups:** 3 sets of 8-12 reps",
            "- **Bodyweight squats:** 3 sets of 12-15 reps",
            "- **Lunges:** 3 sets of 8-12 reps per side",
            "- **Plank:** 3 sets of 30-45 seconds",
        ]
    return [
        "- **Walk:** 20 minutes",
        "- **Mobility or yoga:** 10 minutes",
        "- **Light cardio:** 20 minutes",
        "- **Full-body strength:** 3 days each week",
        "- **Rest or easy movement** on remaining days",
    ]

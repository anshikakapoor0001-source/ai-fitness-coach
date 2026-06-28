def get_workout_plan(goal):

    if goal == "Weight Loss":
        return [
            "🚶 30 minutes brisk walking",
            "🏃 20 minutes jogging",
            "🤸 3 sets of jumping jacks",
            "💪 3 sets of squats",
            "🧘 10 minutes stretching"
        ]

    elif goal == "Muscle Gain":
        return [
            "💪 Push-ups - 3 sets x 12 reps",
            "🏋️ Squats - 3 sets x 15 reps",
            "🦵 Lunges - 3 sets x 12 reps",
            "🏋️ Plank - 3 sets x 45 seconds",
            "🚶 10 minutes warm-up walk"
        ]

    else:
        return [
            "🚶 20 minutes walking",
            "🧘 Yoga",
            "🤸 Stretching",
            "🏃 Light cardio",
            "💪 Full body workout (3 days/week)"
        ]
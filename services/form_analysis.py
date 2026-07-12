EXERCISES = {
    "squat": {
        "name": "Squat", "landmarks": ("LEFT_HIP", "LEFT_KNEE", "LEFT_ANKLE"),
        "up_angle": 165, "down_angle": 100, "ready": "Ready! Start squatting",
        "up_feedback": "Go down with control", "down_feedback": "Good depth. Stand back up",
        "middle_feedback": "Try to lower a little further",
    },
    "pushup": {
        "name": "Push-up", "landmarks": ("LEFT_SHOULDER", "LEFT_ELBOW", "LEFT_WRIST"),
        "up_angle": 160, "down_angle": 90, "ready": "Ready! Begin your push-ups",
        "up_feedback": "Lower your chest with control", "down_feedback": "Good depth. Push back up",
        "middle_feedback": "Lower a little further while keeping your body straight",
    },
    "bicep_curl": {
        "name": "Bicep curl", "landmarks": ("LEFT_SHOULDER", "LEFT_ELBOW", "LEFT_WRIST"),
        "up_angle": 155, "down_angle": 45, "ready": "Ready! Start curling",
        "up_feedback": "Curl the weight upward", "down_feedback": "Great curl. Lower with control",
        "middle_feedback": "Bring your hand a little closer to your shoulder",
    },
    "lunge": {
        "name": "Lunge", "landmarks": ("LEFT_HIP", "LEFT_KNEE", "LEFT_ANKLE"),
        "up_angle": 165, "down_angle": 105, "ready": "Ready! Step into a lunge",
        "up_feedback": "Step forward and lower with control", "down_feedback": "Good depth. Drive back to standing",
        "middle_feedback": "Bend the front knee a little more",
    },
}


def exercise_choices():
    return [{"id": key, "name": value["name"]} for key, value in EXERCISES.items()]

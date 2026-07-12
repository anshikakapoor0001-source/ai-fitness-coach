import os

import cv2
import mediapipe as mp
import numpy as np


mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils


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


def calculate_angle(a, b, c):
    """Calculate the angle at point b for three normalized landmarks."""
    a, b, c = np.array(a), np.array(b), np.array(c)
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = abs(radians * 180.0 / np.pi)
    return 360 - angle if angle > 180 else angle


def exercise_choices():
    return [{"id": key, "name": value["name"]} for key, value in EXERCISES.items()]


def generate_frames(exercise_id="squat"):
    """Stream annotated frames and count repetitions for the chosen exercise."""
    exercise = EXERCISES.get(exercise_id, EXERCISES["squat"])
    backend = cv2.CAP_DSHOW if os.name == "nt" else cv2.CAP_ANY
    camera = cv2.VideoCapture(0, backend)
    if not camera.isOpened():
        raise RuntimeError("Could not open webcam. Check that it is connected and available.")

    counter, stage, feedback = 0, None, "Stand in view to begin"
    started, down_frames = False, 0
    landmark_names = exercise["landmarks"]

    try:
        with mp_pose.Pose(min_detection_confidence=0.6, min_tracking_confidence=0.6) as pose:
            while camera.isOpened():
                success, frame = camera.read()
                if not success:
                    break
                frame = cv2.flip(frame, 1)
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                rgb.flags.writeable = False
                results = pose.process(rgb)

                if results.pose_landmarks:
                    landmarks = results.pose_landmarks.landmark
                    try:
                        first, middle, last = (landmarks[getattr(mp_pose.PoseLandmark, name).value] for name in landmark_names)
                        angle = calculate_angle([first.x, first.y], [middle.x, middle.y], [last.x, last.y])
                        cv2.putText(frame, str(int(angle)), tuple(np.multiply([middle.x, middle.y], [640, 480]).astype(int)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)

                        if not started and angle > exercise["up_angle"]:
                            started, stage, feedback = True, "UP", exercise["ready"]
                        elif started and angle > exercise["up_angle"]:
                            if stage == "DOWN":
                                counter += 1
                                feedback = f"Rep {counter} complete!"
                            else:
                                feedback = exercise["up_feedback"]
                            stage, down_frames = "UP", 0
                        elif started and angle < exercise["down_angle"]:
                            down_frames += 1
                            if down_frames >= 5:
                                stage, feedback = "DOWN", exercise["down_feedback"]
                        elif started:
                            feedback = exercise["middle_feedback"]
                    except (IndexError, TypeError, ValueError):
                        feedback = "Move fully into the camera frame"

                    mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS, mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2), mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2))

                cv2.rectangle(frame, (0, 0), (410, 120), (0, 0, 0), -1)
                for text, position, size, color in ((exercise["name"], (10, 30), 0.7, (255, 255, 255)), (f"Reps: {counter}", (10, 65), 0.9, (0, 255, 0)), (feedback, (10, 100), 0.6, (0, 255, 255))):
                    cv2.putText(frame, text, position, cv2.FONT_HERSHEY_SIMPLEX, size, color, 2)
                encoded, buffer = cv2.imencode(".jpg", frame)
                if encoded:
                    yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n"
    finally:
        camera.release()

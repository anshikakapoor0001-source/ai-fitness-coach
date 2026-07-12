import os

import cv2
import mediapipe as mp
import numpy as np


mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils


def calculate_angle(a, b, c):
    """Calculate the angle at point b for three normalized landmarks."""
    a, b, c = np.array(a), np.array(b), np.array(c)
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(
        a[1] - b[1], a[0] - b[0]
    )
    angle = abs(radians * 180.0 / np.pi)
    return 360 - angle if angle > 180 else angle


def generate_frames():
    """Stream annotated frames while counting controlled squat repetitions."""
    backend = cv2.CAP_DSHOW if os.name == "nt" else cv2.CAP_ANY
    camera = cv2.VideoCapture(0, backend)
    if not camera.isOpened():
        raise RuntimeError("Could not open webcam. Check that it is connected and available.")

    counter, stage, feedback = 0, None, "Stand straight to begin"
    started, down_frames = False, 0

    try:
        with mp_pose.Pose(
            min_detection_confidence=0.6, min_tracking_confidence=0.6
        ) as pose:
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
                        hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
                        knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value]
                        ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]
                        angle = calculate_angle(
                            [hip.x, hip.y], [knee.x, knee.y], [ankle.x, ankle.y]
                        )

                        cv2.putText(
                            frame,
                            str(int(angle)),
                            tuple(np.multiply([knee.x, knee.y], [640, 480]).astype(int)),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7,
                            (255, 255, 255),
                            2,
                            cv2.LINE_AA,
                        )

                        if not started and angle > 165:
                            started, stage, feedback = True, "UP", "Ready! Start squatting"
                        elif started and angle > 165:
                            stage, down_frames, feedback = "UP", 0, "Go down"
                        elif started and angle < 100:
                            down_frames += 1
                            if down_frames >= 5 and stage == "UP":
                                stage, counter, feedback = "DOWN", counter + 1, "Good squat!"
                        elif started:
                            feedback = "Go lower"
                    except (IndexError, TypeError, ValueError):
                        feedback = "Move fully into the camera frame"

                    mp_drawing.draw_landmarks(
                        frame,
                        results.pose_landmarks,
                        mp_pose.POSE_CONNECTIONS,
                        mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),
                        mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2),
                    )

                cv2.rectangle(frame, (0, 0), (350, 120), (0, 0, 0), -1)
                for text, position, size, color in (
                    (f"Reps: {counter}", (10, 35), 1, (0, 255, 0)),
                    (f"Stage: {stage or 'READY'}", (10, 70), 0.8, (255, 255, 255)),
                    (feedback, (10, 105), 0.7, (0, 255, 255)),
                ):
                    cv2.putText(frame, text, position, cv2.FONT_HERSHEY_SIMPLEX, size, color, 2)

                encoded, buffer = cv2.imencode(".jpg", frame)
                if encoded:
                    yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n"
    finally:
        camera.release()

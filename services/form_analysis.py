import cv2
import mediapipe as mp
import numpy as np

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils


def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - \
              np.arctan2(a[1]-b[1], a[0]-b[0])

    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180:
        angle = 360 - angle

    return angle


def generate_frames():

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    
    if not cap.isOpened():
        raise Exception("Could not open webcam")

    counter = 0
    stage = None
    feedback = "Stand Straight"

    # Prevent false counting
    started = False
    down_frames = 0

    with mp_pose.Pose(
        min_detection_confidence=0.6,
        min_tracking_confidence=0.6
    ) as pose:

        while cap.isOpened():

            success, frame = cap.read()
            
            print("Frame:", success)

            if not success:
                break

            frame = cv2.flip(frame, 1)

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rgb.flags.writeable = False

            results = pose.process(rgb)

            rgb.flags.writeable = True

            if results.pose_landmarks:

                landmarks = results.pose_landmarks.landmark

                try:

                    hip = [
                        landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                        landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y
                    ]

                    knee = [
                        landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                        landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y
                    ]

                    ankle = [
                        landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                        landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y
                    ]

                    angle = calculate_angle(hip, knee, ankle)

                    # Draw knee angle
                    cv2.putText(
                        frame,
                        str(int(angle)),
                        tuple(np.multiply(knee, [640, 480]).astype(int)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (255, 255, 255),
                        2,
                        cv2.LINE_AA
                    )

                    # -----------------------
                    # Wait until user is standing
                    # -----------------------
                    if not started:

                        if angle > 165:
                            started = True
                            stage = "UP"
                            feedback = "Ready! Start Squatting"

                    else:

                        # Standing
                        if angle > 165:
                            stage = "UP"
                            down_frames = 0
                            feedback = "Go Down"

                        # Going Down
                        elif angle < 100:

                            down_frames += 1

                            if down_frames >= 5 and stage == "UP":
                                stage = "DOWN"
                                counter += 1
                                feedback = "Good Squat!"

                        else:
                            feedback = "Go Lower"

                except Exception:
                    pass

                mp_drawing.draw_landmarks(
                    frame,
                    results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS,
                    mp_drawing.DrawingSpec(
                        color=(245, 117, 66),
                        thickness=2,
                        circle_radius=2
                    ),
                    mp_drawing.DrawingSpec(
                        color=(245, 66, 230),
                        thickness=2,
                        circle_radius=2
                    )
                )

            # -----------------------
            # UI
            # -----------------------

            cv2.rectangle(frame, (0, 0), (340, 140), (0, 0, 0), -1)

            cv2.putText(
                frame,
                f"Reps : {counter}",
                (10, 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )

            cv2.putText(
                frame,
                f"Stage : {stage}",
                (10, 70),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 255),
                2
            )

            cv2.putText(
                frame,
                feedback,
                (10, 105),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 255),
                2
            )

            cv2.putText(
                frame,
                "Press Q to Quit",
                (10, 135),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (200, 200, 200),
                2
            )

                        # Encode frame for browser
            ret, buffer = cv2.imencode(".jpg", frame)

            if not ret:
                continue

            frame = buffer.tobytes()

            yield (
                b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' +
                frame +
                b'\r\n'
            )

    cap.release()
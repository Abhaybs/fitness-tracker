import cv2
import numpy as np
from ultralytics import YOLO

# --- CONFIGURATION ---
VIDEO_PATH = "New folder\\video2.mp4" # Replace with your video path or 0 for webcam
VIEW = "left"                 # Choose: "left", "right", or "front"
MODEL_PATH = "yolov8n-pose.pt" # Nano model is fastest. Use 'yolov8m-pose.pt' for higher accuracy.

def calculate_angle(a, b, c):
    """Calculate the angle between 3 points (b is the vertex)."""
    a, b, c = np.array(a), np.array(b), np.array(c)
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    if angle > 180.0:
        angle = 360 - angle
    return angle

def main():
    model = YOLO(MODEL_PATH)
    cap = cv2.VideoCapture(VIDEO_PATH)
    
    counter = 0
    stage = "up" # Tracks if the user is 'up' or 'down'

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        # Run YOLOv8 inference
        frame = cv2.resize(frame, (1280, 720))
        results = model(frame, verbose=False)

        # Get keypoints from the first detected person
        if len(results[0].keypoints.xy) > 0:
            keypoints = results[0].keypoints.xy[0].cpu().numpy()
            
            # Ensure we actually detected enough points
            if len(keypoints) >= 11: 
                try:
                    if VIEW == "left":
                        shoulder, elbow, wrist = keypoints[5], keypoints[7], keypoints[9]
                        metric = calculate_angle(shoulder, elbow, wrist)
                        is_down = metric < 90
                        is_up = metric > 160
                        
                    elif VIEW == "right":
                        shoulder, elbow, wrist = keypoints[6], keypoints[8], keypoints[10]
                        metric = calculate_angle(shoulder, elbow, wrist)
                        is_down = metric < 90
                        is_up = metric > 160
                        
                    elif VIEW == "front":
                        # For front view, track how close the shoulder drops to the wrist (Y axis)
                        # Top-left of screen is (0,0), so Y increases as you go down.
                        avg_shoulder_y = (keypoints[5][1] + keypoints[6][1]) / 2
                        avg_wrist_y = (keypoints[9][1] + keypoints[10][1]) / 2
                        
                        metric = avg_wrist_y - avg_shoulder_y 
                        # Thresholds will depend on camera distance, tune these!
                        is_down = metric < 100  # Shoulders are close to wrists
                        is_up = metric > 250    # Shoulders are far above wrists

                    # --- STATE MACHINE LOGIC ---
                    if is_down and stage == "up":
                        stage = "down"
                    if is_up and stage == "down":
                        stage = "up"
                        counter += 1
                        for i, (x, y) in enumerate(keypoints):
                            if x > 0 and y > 0:
                                cv2.circle(frame, (int(x), int(y)), 5, (0, 0, 255), -1)
                                cv2.putText(frame, str(i), (int(x) + 5, int(y) - 5),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

                    # Draw visual feedback
                    cv2.putText(frame, f"Reps: {counter}", (50, 50), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
                    cv2.putText(frame, f"State: {stage}", (50, 100), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    cv2.putText(frame, f"Metric: {int(metric)}", (50, 150), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

                except IndexError:
                    pass # Keypoints not fully visible in this frame

        # Render YOLO bounding boxes & skeletons
        annotated_frame = results[0].plot()
        
        cv2.imshow("Pushup Counter", annotated_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
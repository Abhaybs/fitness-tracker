import cv2
import numpy as np
import requests
from ultralytics import YOLO

# --- CONFIGURATION ---
VIDEO_PATH = "C:\\Users\\Dell\\Desktop\\pushup\\New folder\\Bodyweight_Squats_1080p.mp4"        # 0 for webcam, or path to video file
VIEW = "left"         # "left" or "right"
API_URL = "http://127.0.0.1:8000/log_pushups/" # We can reuse the same endpoint for now

def calculate_angle(a, b, c):
    """Calculates the angle at the knee (b)."""
    a, b, c = np.array(a), np.array(b), np.array(c)
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    if angle > 180.0:
        angle = 360 - angle
    return angle

def main():
    model = YOLO('yolov8n-pose.pt')
    cap = cv2.VideoCapture(VIDEO_PATH)
    
    counter = 0
    stage = "up"
    
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break
        frame = cv2.resize(frame, (600, 900))
        results = model(frame, verbose=False)
        
        if results[0].keypoints is not None and len(results[0].keypoints.xy[0]) > 0:
            keypoints = results[0].keypoints.xy[0].cpu().numpy()
            
            # --- INDEX MAPPING ---
            # Left side:  11 (Hip), 13 (Knee), 15 (Ankle)
            # Right side: 12 (Hip), 14 (Knee), 16 (Ankle)
            
            if VIEW == "left":
                hip, knee, ankle = keypoints[11], keypoints[13], keypoints[15]
            else: # right
                hip, knee, ankle = keypoints[12], keypoints[14], keypoints[16]

            # Check visibility
            if all(pt[0] > 0 and pt[1] > 0 for pt in [hip, knee, ankle]):
                
                angle = calculate_angle(hip, knee, ankle)
                # ... inside the loop, after defining hip, knee, ankle ...

                # 1. Define the "Depth Line" at the Knee's Y-coordinate
                knee_y = int(knee[1])
                hip_y = int(hip[1])
                
                # 2. Determine Line Color based on depth
                # If Hip is lower on screen (greater Y) than Knee, we hit depth -> Green
                if hip_y >= knee_y:
                    line_color = (0, 255, 0)  # Green
                else:
                    line_color = (0, 0, 255)  # Red

                # 3. Draw the line across the screen width (assuming 640px width, or use frame.shape[1])
                frame_width = frame.shape[1]
                cv2.line(frame, (0, knee_y), (frame_width, knee_y), line_color, 2)

                # 4. Optional: Draw a "Hip Marker" to see exactly what point is being tracked
                cv2.circle(frame, (int(hip[0]), int(hip[1])), 10, line_color, -1)

                # ... continue with existing visualization code ...
                # --- STATE MACHINE ---
                # Squat Logic: 
                # < 90 means deep squat (down)
                # > 160 means standing straight (up)
                is_below_parallel = hip[1] >= knee[1]
                if angle < 90 and is_below_parallel and  stage == "up":
                    stage = "down"
                
                if angle > 160 and stage == "down":
                    stage = "up"
                    counter += 1
                    print(f"Squat count: {counter}")

                # --- VISUALIZATION ---
                # Draw the angle at the knee
                cv2.putText(frame, str(int(angle)), 
                           tuple(np.multiply(knee, [1, 1]).astype(int)), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)

                # Draw connections
                cv2.line(frame, (int(hip[0]), int(hip[1])), (int(knee[0]), int(knee[1])), (0,255,0), 3)
                cv2.line(frame, (int(knee[0]), int(knee[1])), (int(ankle[0]), int(ankle[1])), (0,255,0), 3)

                # UI Box
                cv2.rectangle(frame, (0, 0), (250, 80), (245, 117, 16), -1)
                cv2.putText(frame, 'REPS', (15, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
                cv2.putText(frame, str(counter), (10, 65), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2, cv2.LINE_AA)
                cv2.putText(frame, 'STAGE', (120, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
                cv2.putText(frame, stage, (120, 65), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2, cv2.LINE_AA)

        cv2.imshow("Squat Counter", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    # --- LOG TO API ---
    if counter > 0:
        try:
            payload = {"reps": counter, "view_type": "squat"}
            requests.post(API_URL, json=payload)
            print(f"Logged {counter} squats to API!")
        except:
            print("API logging failed.")

if __name__ == "__main__":
    main()
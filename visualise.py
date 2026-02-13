import cv2
from ultralytics import YOLO

def visualize_keypoints(video_source=0): 
    # Use 0 for your default webcam. 
    # To use a video file, replace 0 with the file path (e.g., "test_video.mp4")
    
    print("Loading model...")
    model = YOLO('yolov8n-pose.pt') 

    print(f"Opening video source: {video_source}")
    cap = cv2.VideoCapture(video_source)

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            print("Video stream ended or cannot be read.")
            break

        # Run YOLOv8 inference (verbose=False keeps your terminal clean)
        results = model(frame, verbose=False)

        # Check if any keypoints were detected in this frame
        if results[0].keypoints is not None:
            # Extract keypoints for all detected people in the frame
            # .xy gives us the X and Y coordinates
            all_keypoints = results[0].keypoints.xy.cpu().numpy()

            # Loop through each person detected
            for person_keypoints in all_keypoints:
                # Loop through all 17 keypoints for this person
                for i, (x, y) in enumerate(person_keypoints):
                    
                    # YOLOv8 returns (0,0) for joints it cannot see.
                    # We only draw the joints that are actively detected.
                    if x > 0 and y > 0:
                        # Draw a solid red circle at the joint
                        cv2.circle(frame, (int(x), int(y)), 5, (0, 0, 255), -1)
                        
                        # Draw the index number (0-16) in yellow next to the joint
                        cv2.putText(frame, str(i), (int(x) + 8, int(y) - 8), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

        # Display the frame
        cv2.imshow("YOLOv8 Keypoint Visualizer", frame)

        # Press 'q' on your keyboard to exit the loop
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    visualize_keypoints()
# YOLOv8 AI Fitness Tracker

A real-time computer vision application that counts repetitions and evaluates form for dynamic exercises (Pushups, Squats, and Planks) using YOLOv8 pose estimation. The system features automatic camera orientation detection and logs workout sessions to a PostgreSQL database via a decoupled FastAPI backend.

Features:

* **Real-Time Pose Estimation:** Utilizes Ultralytics YOLOv8 for high-speed, accurate joint tracking.
* **Dynamic View Detection:** Automatically detects if the user is facing the camera (front) or perpendicular to it (side) using spatial heuristics and bounding box confidence scores.
* **Exercise Modules:**
  * **Pushup Counter:** Tracks elbow-hinge angles (side view) or vertical shoulder/wrist displacement (front view).
  * **Squat Counter:** Enforces strict coordinate-based physics checks (hip-to-knee Y-coordinate ratio) to ensure the user breaks parallel before counting a rep.
* **Decoupled Architecture:** Features a REST API microservice that asynchronously logs session data without blocking the real-time video processing thread.
* **Persistent Storage:** Uses SQLAlchemy ORM and PostgreSQL to permanently log workout history.

## 🛠️ Tech Stack

* **Computer Vision:** Python, OpenCV, Ultralytics (YOLOv8), NumPy
* **Backend:** FastAPI, Uvicorn, Pydantic
* **Database:** PostgreSQL, SQLAlchemy, psycopg2-binary
* **Data Visualization:** Streamlit (Optional Dashboard)

⚙️ Installation & Setup
1. Clone the repository and install dependencies:

Bash

# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

# Install required packages
pip install ultralytics opencv-python numpy fastapi uvicorn requests sqlalchemy psycopg2-binary
2. Set up the PostgreSQL Database:
Ensure you have PostgreSQL running locally or via Docker. Update the SQLALCHEMY_DATABASE_URL in database.py with your credentials:

Python

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:password@localhost:5432/fitness"
3. Start the FastAPI Server:
Initialize the database tables and start listening for incoming session logs.

Bash

uvicorn api:app --reload
The API will be available at http://127.0.0.1:8000.

🏋️‍♂️ Usage
With the API running in the background, open a new terminal window to run the computer vision scripts. The system will use your default webcam (video_source=0) or a provided video file path.

To run the Pushup Counter:

Bash

python main.py
To run the strict pushup Counter:

Bash

python squat_counter.py
To run the squat count evaluator:

🧠 Core Logic & Architecture
Angle Calculation: Uses numpy.arctan2 to robustly calculate joint angles, avoiding division-by-zero errors inherent in standard Euclidean geometry.

State Machine: Repetitions are counted using a deterministic state machine (transitioning from up -> down -> up) to eliminate false positives caused by bounding box flickering.

Foreshortening Mitigation: To handle front-facing exercises where 2D angles fail due to camera foreshortening, the system tracks the raw vertical displacement (Y-axis) between joints.


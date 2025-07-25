# AI-based Face Recognition Attendance System

## 📌 Overview
This is a Flask-based web application for automated attendance using facial recognition. It uses FaceNet for facial embeddings, SQLite for storage, and includes features like:
- Faculty registration with face image
- Real-time face recognition for attendance marking
- Absentee alerts using Twilio SMS
- Chatbot for querying faculty attendance details
- Live location capture
- Dashboard with reports, logs, and statistics

## 🔧 Key Features
- User registration with face embedding
- Real-time face recognition using webcam
- Attendance marking and logging with timestamps
- SQLite-based database storage
- Web interface using Flask

### 🧑‍🏫 Faculty Registration
- Faculty register by providing details and uploading a clear face image.
- Face embedding is generated using FaceNet (`facenet_keras.h5`) and stored as `.npy` or in SQLite BLOB field.

### 🤳 Live Attendance Marking
- Webcam captures the faculty face during attendance.
- Face is detected and embedding is generated.
- Compared with stored embeddings using cosine similarity.
- If matched, attendance is marked with faculty ID, timestamp, and location.
- If mismatched, an alert is generated for wrong faculty ID.

### 🧠 Face Recognition Logic
- Face is extracted using Haar Cascade or MTCNN.
- Embedding is generated from preprocessed face using FaceNet.
- Cosine similarity > 0.7 (threshold) is considered a match.
- Top match is verified with provided faculty ID.

### ✅ Attendance Validation Flow
1. Faculty ID and webcam image submitted.
2. Embedding is generated from image.
3. System checks if the embedding matches a known ID.
4. If match is found and ID matches, attendance is marked.
5. If mismatch, alert message is flashed and SMS sent via Twilio.

### 🗺️ Location Tracking
- Uses browser’s geolocation API.
- Captures latitude and longitude during attendance.
- Stored with attendance record in SQLite.

### 💬 Chatbot Support
- Integrated chatbot (rule-based or AI) to respond to:
  - Daily attendance
  - Faculty records
  - Department-wise stats
  - Absentee summaries

### 🔔 Alerts (Twilio)
- Sends SMS alert to admin if:
  - Face doesn't match the given faculty ID
  - Same ID is used multiple times
  - Suspicious activity detected

### 🗂️ SQLite Database
- Tables:
  - `faculty`: stores ID, name, contact, embedding
  - `attendance`: stores records with date, time, ID, location
  - `alerts`: logs mismatches and alerts sent
  - `admin`: login credentials
- Embeddings stored in BLOB or `.npy` path.

### 🛠️ Flash Messages
- Shows feedback during attendance marking like:
  - ✅ "Attendance marked at 10:22 AM from Hyderabad"
  - ⚠️ "Wrong faculty ID – face mismatch"
  - ⚠️ "Attendance already marked"

### 🔍 Logs
- Application, error, attendance, and face recognition logs are stored and viewable in the dashboard.

## 🖼️ Technologies Used
- **Frontend**: HTML, CSS, JS, Bootstrap, AJAX
- **Backend**: Python, Flask, SQLite
- **Face Recognition**: FaceNet model (`facenet_keras.h5`), OpenCV
- **Alerts**: Twilio SMS
- **Location**: HTML5 Geolocation API
- **Chatbot**: Python rule-based / NLP-based

## ▶️ How to Run
1. Install dependencies from `requirements.txt`
2. Start Flask server: `python app.py`
3. Open in browser: `http://127.0.0.1:5000/`
4. Register a faculty and test attendance

## 🔐 Security Notes
- Validates face-ID match before attendance
- Secure credential storage for admins
- Logs every action

## 📦 Folder Structure
```
project/
│
├── app.py
├── face_utils.py
├── db_handler.py
├── routes/
│   ├── auth.py
│   ├── attendance.py
│   ├── reports.py
│   └── chatbot.py
├── static/
├── templates/
├── embeddings/
├── database/
│   └── attendance.db
├── facenet_keras.h5
└── requirements.txt
```

---
Created by Vadapalli Sravya Sri – AI-based Face Recognition Attendance System 💡#   A I - B a s e d - F a c e - R e c o g n i t i o n - S y s t e m  
 
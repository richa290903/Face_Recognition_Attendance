import os
import cv2
import dlib
import face_recognition
import numpy as np
from scipy.spatial import distance as dist
from datetime import datetime
from connect import connection, mycursor  # Assuming you have this in connect.py


# Initialize dlib's face detector (HOG-based) and facial landmark predictor
predictor_path = 'shape_predictor_68_face_landmarks.dat'
if not os.path.isfile(predictor_path):
    raise ValueError("Missing shape_predictor_68_face_landmarks.dat file. Please download and place it in the correct directory.")

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(predictor_path)

# Function to calculate eye aspect ratio
def eye_aspect_ratio(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    ear = (A + B) / (2.0 * C)
    return ear

# Function for determining if the eyes are blinking
def is_blinking(landmarks):
    left_eye = landmarks[36:42]
    right_eye = landmarks[42:48]
    left_ear = eye_aspect_ratio(left_eye)
    right_ear = eye_aspect_ratio(right_eye)
    ear = (left_ear + right_ear) / 2.0
    return ear < 0.2

# Function to detect if the image is likely a printed photo (non-live)
def is_printed_photo(frame, face_location):
    top, right, bottom, left = face_location
    face_region = frame[top:bottom, left:right]

    # Check if the face region has a uniform texture
    mean_pixel_value = cv2.mean(face_region)[0]
    if mean_pixel_value < 80:  # Adjust threshold as needed
        return True
    else:
        return False

# Global variable to track attendance
attendance_record = set()

# Function to load known faces from the database
def load_known_faces_from_db():
    known_face_encodings = []
    known_face_names = []

    # Query the database for student details
    query = "SELECT name, photo FROM stud_info1"
    mycursor.execute(query)
    results = mycursor.fetchall()

    for name, photo in results:
        # Convert binary data to image
        photo_np = np.frombuffer(photo, np.uint8)
        student_image = cv2.imdecode(photo_np, cv2.IMREAD_COLOR)

        # Get face encodings
        student_face_encodings = face_recognition.face_encodings(student_image)
        if student_face_encodings:
            student_face_encoding = student_face_encodings[0]
            known_face_encodings.append(student_face_encoding)
            known_face_names.append(name)

    return known_face_encodings, known_face_names

# Function to mark attendance using face recognition with anti-spoofing check
def mark_attendance_with_face_recognition(video_source=0):
    # Load known individual student photos from the database
    known_face_encodings, known_face_names = load_known_faces_from_db()

    # Initialize video capture (use a CCTV camera or any other video source)
    cap = cv2.VideoCapture(video_source)  # Using default backend

    if not cap.isOpened():
        print("Error: Unable to open video source.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Unable to read frame from video source.")
            break

        # Find all face locations and encodings in the current frame
        face_locations = face_recognition.face_locations(frame)
        face_encodings = face_recognition.face_encodings(frame, face_locations)

        # Match faces in the frame with known faces
        for face_encoding, face_location in zip(face_encodings, face_locations):
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.6)
            name = "Unknown"

            # Check if the detected face is likely a printed photo
            if is_printed_photo(frame, face_location):
                continue  

            # Perform blink detection
            top, right, bottom, left = face_location
            rect = dlib.rectangle(left, top, right, bottom)
            landmarks = predictor(frame, rect)
            landmarks = [(p.x, p.y) for p in landmarks.parts()]

            if not is_blinking(landmarks):
                continue  # Skip if no blink detected

            if True in matches:
                first_match_index = matches.index(True)
                name = known_face_names[first_match_index]

                # Check if already marked attendance
                if name not in attendance_record:
                    # Mark attendance with date and time
                    now = datetime.now()
                    date = now.strftime("%Y-%m-%d")
                    time = now.strftime("%H:%M:%S")
                    # print(f"{name} is present at {dt_string}.")
                    attendance_record.add(name)  # Add to attendance record

                    # Insert attendance record into the database
                    insert_query = "INSERT INTO `attendance1` (`name`, `date`,`time`) VALUES (%s, %s,%s)" 
                    values = (name,date,time)
                    try:
                        mycursor.execute(insert_query, values)
                        connection.commit()  # Commit the transaction
                    except Exception as e:
                        print(f"Error inserting data: {e}")

            # Draw a rectangle around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

            # Draw a label with the name below the face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        # Display the resulting frame
        try:
            cv2.imshow('Face Recognition Attendance', frame)
        except cv2.error as e:
            print("Error displaying frame:", e)
            break

        # Exit loop if 'q' key is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release video capture and close all OpenCV windows
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    video_source = 0  # Default to webcam. Replace with CCTV camera source if available.
    mark_attendance_with_face_recognition(video_source)
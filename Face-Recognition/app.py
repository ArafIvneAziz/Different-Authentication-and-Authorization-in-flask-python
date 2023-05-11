from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
import face_recognition
import cv2

app = Flask(__name__)
client = MongoClient('mongo-uri')
db = client['test']
collection = db['users']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/face_registration', methods=['POST'])
def face_registration():
    video_capture = cv2.VideoCapture(0)
    # Capture a single frame from the camera
    ret, frame = video_capture.read()
    if ret:
        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Find all the faces in the current frame of video
        face_locations = face_recognition.face_locations(rgb_frame)
        # Assume there is only one face in the image
        top, right, bottom, left = face_locations[0]
        face_image = rgb_frame[top:bottom, left:right]
        # Save the face image to MongoDB
        _, buffer = cv2.imencode('.jpg', face_image)
        img_binary = buffer.tobytes()
        collection.insert_one({'face': img_binary})
        video_capture.release()
        return redirect(url_for('dashboard'))
    else:
        video_capture.release()
        return "Error capturing image"

@app.route('/face_login', methods=['POST'])
def face_login():
    video_capture = cv2.VideoCapture(0)
    # Capture a single frame from the camera
    ret, frame = video_capture.read()
    if ret:
        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Find all the faces in the current frame of video
        face_locations = face_recognition.face_locations(rgb_frame)
        # Assume there is only one face in the image
        top, right, bottom, left = face_locations[0]
        face_image = rgb_frame[top:bottom, left:right]
        # Load the faces from MongoDB
        face_list = []
        for face_data in collection.find():
            face_binary = face_data['face']
            face_array = bytearray(face_binary)
            face_image = cv2.imdecode(face_array, cv2.IMREAD_COLOR)
            face_list.append(face_image)
        # Compute face encodings for the current frame of video
        unknown_face_encoding = face_recognition.face_encodings(face_image)
        # Compare the current face encoding to the known face encodings in the database
        for known_face_image in face_list:
            known_face_encoding = face_recognition.face_encodings(known_face_image)
            match_results = face_recognition.compare_faces([known_face_encoding], unknown_face_encoding)
            if match_results[0]:
                video_capture.release()
                return redirect(url_for('dashboard'))
        video_capture.release()
        return "Face not recognized"
    else:
        video_capture.release()
        return "Error capturing image"

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)
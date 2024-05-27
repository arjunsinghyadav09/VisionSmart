from flask import Flask, render_template, request,flash
import os
import cv2
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
import mysql.connector
import joblib
from mysql.connector import IntegrityError

app = Flask(__name__)

nimgs = 50
face_detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

if not os.path.isdir('website/static/faces'):
    os.makedirs('website/static/faces')

def extract_faces(img):
    try:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        face_points = face_detector.detectMultiScale(gray, 1.2, 5, minSize=(20, 20))
        return face_points
    except:
        return []

def train_model():
    faces = []
    labels = []
    userlist = os.listdir('website/static/faces')
    for user in userlist:
        for imgname in os.listdir(f'website/static/faces/{user}'):
            img = cv2.imread(f'website/static/faces/{user}/{imgname}')
            resized_face = cv2.resize(img, (50, 50))
            faces.append(resized_face.ravel())
            labels.append(user)
    faces = np.array(faces)
    knn = KNeighborsClassifier(n_neighbors=5)
    knn.fit(faces, labels)
    joblib.dump(knn, 'website/static/face_recognition_model.pkl')

class StudentRegAuthRoutes:
    def __init__(self, app):
        self.app = app
        self.route()

    def route(self):
        @self.app.route('/student_register', methods=['POST', 'GET'])
        def register_employee():
            if request.method == 'POST':
                try:
                    # MySQL connection
                    mydb = mysql.connector.connect(
                        host='localhost',
                        user='root',
                        password='',
                        database='vision'
                    )

                    mycursor = mydb.cursor()

                    register = request.form
                    fullName = register['fullName']
                    FatherName = register['FatherName']
                    Course = register['Course']
                    Branch = register['Branch']
                    Year = register['Year']
                    DOB = register['DOB']
                    email_id = register['email_id']
                    PhoneNumber = register['PhoneNumber']
                    gender = register['gender']
                    StudentID = register['StudentID']

                    img = request.files['img']
                    img.save('website/static/uploaded/' + img.filename)
                    image_save=img.filename
                    userimagefolder = 'website/static/faces/' + fullName + '_' + str(StudentID)
                    if not os.path.isdir(userimagefolder):
                        os.makedirs(userimagefolder)
                    i, j = 0, 0
                    cap = cv2.VideoCapture(0)
                    while 1:
                        _, frame = cap.read()
                        faces = extract_faces(frame)
                        for (x, y, w, h) in faces:
                            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 20), 2)
                            cv2.putText(frame, f'Images Captured: {i}/{nimgs}', (30, 30),
                                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 20), 2, cv2.LINE_AA)
                            if j % 5 == 0:
                                name = fullName + '_' + str(i) + '.jpg'
                                cv2.imwrite(userimagefolder + '/' + name, frame[y:y + h, x:x + w])
                                i += 1
                            j += 1
                        if j == nimgs * 5:
                            break
                        cv2.imshow('Adding new User', frame)
                        if cv2.waitKey(1) == 27:
                            break
                    cap.release()
                    cv2.destroyAllWindows()

                    print('Training Model')
                    train_model()

                    # Insert data into MySQL
                    mycursor.execute(
                        "INSERT INTO student_data (fullName, FatherName, Course, Branch, Year, DOB, email_id, PhoneNumber, gender, StudentID,img) VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                        (fullName, FatherName, Course, Branch, Year, DOB, email_id, PhoneNumber, gender, StudentID,image_save)
                    )

                    mydb.commit()
                    mycursor.close()
                    flash("Student registration successful!", "success")
                except IntegrityError as e:
                    mydb.rollback()
                    flash("Student ID already exists. Please use a different Student ID.", "error")
            return render_template("registerStudent.html")
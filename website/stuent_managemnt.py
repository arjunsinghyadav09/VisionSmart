from flask import render_template, request, redirect, url_for,flash,session
import mysql.connector
import string
import random
import smtplib
from dotenv import load_dotenv
from email.message import EmailMessage
import os
from datetime import date
import ssl
import uuid
import joblib
import cv2
from datetime import datetime, timedelta

db_config = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "vision"
}

load_dotenv()


email_sender = os.getenv("SENDER_Email_ID")
email_sender_pas = os.getenv("Password")

def generate_unique_token():
    return str(uuid.uuid4())

def connect_to_db():
    return mysql.connector.connect(
        host=os.getenv("Host"),
        user=os.getenv("USER_NAME"),
        password=os.getenv("Security_Key"),
        database=os.getenv("Database_Name")
    )

def store_token_in_database(user_id, token):
    try:
        mydb = connect_to_db()
        cursor = mydb.cursor()
        expiration = datetime.utcnow() + timedelta(hours=1)
        cursor.execute(
            "INSERT INTO `password_reset_tokens` (`user_id`, `token`, `expiration`) VALUES (%s, %s, %s)",
            (user_id, token, expiration)
        )
        mydb.commit()
        cursor.close()
    except mysql.connector.Error as err:
        flash(f"Error storing token in database: {err}", "error")

def send_password_reset_email(email_id, token):
    try:
        subject = "Password Reset Request"
        reset_link = f"http://127.0.0.1:5000/reset_password_student/{token}"
        body = f"Click the following link to reset your password: {reset_link}"

        context = ssl.create_default_context()
        em = EmailMessage()
        em['From'] = email_sender
        em['To'] = email_id
        em['Subject'] = subject
        em.set_content(body)

        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(email_sender, email_sender_pas)
            smtp.sendmail(email_sender, email_id, em.as_string())
    except Exception as e:
        flash(f"Error sending email: {e}", "error")

def validate_token(token):
    try:
        mydb = connect_to_db()
        cursor = mydb.cursor()
        current_time = datetime.utcnow()
        cursor.execute(
            "SELECT `user_id` FROM `password_reset_tokens` WHERE `token` = %s AND `expiration` > %s",
            (token, current_time)
        )
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result else None
    except mysql.connector.Error as err:
        flash(f"Error validating token: {err}", "error")
        return None

def update_password(user_id, new_password):
    try:
        mydb = connect_to_db()
        cursor = mydb.cursor()
        cursor.execute(
            "UPDATE `student_data` SET `password` = %s WHERE `StudentID` = %s",
            (new_password, user_id)
        )
        mydb.commit()
        cursor.close()
    except mysql.connector.Error as err:
        flash(f"Error updating password: {err}", "error")
imgBackground = cv2.imread("background.png")


datetoday = date.today().strftime("%m_%d_%y")
datetoday2 = date.today().strftime("%d-%B-%Y")
face_detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
def identify_face(facearray):
    model = joblib.load('website/static/face_recognition_model.pkl')
    return model.predict(facearray)

def extract_faces(img):
    try:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        face_points = face_detector.detectMultiScale(gray, 1.2, 5, minSize=(20, 20))
        return face_points
    except:
        return []

from datetime import datetime
def totalreg():
    return len(os.listdir('website/static/faces'))

def connect_to_db():
    return mysql.connector.connect(**db_config)



def add_attendance(name, status):
    try:
        student_id = name.split('_')[1]
        current_time = datetime.now().strftime("%H:%M")
        datetoday = date.today().strftime("%d-%m-%y")

        mydb = connect_to_db()
        mycursor = mydb.cursor()

        # Here firest fetch the branch from the student_data table take reference of StudentId
        mycursor.execute("SELECT Branch FROM student_data WHERE StudentID = %s", (student_id,))
        branch_result = mycursor.fetchone()

        if not branch_result:
            print(f"Check Branch found or not for StudentID {student_id}.")
            return
        branch = branch_result[0]

        # Here now applying logic using student branch and current time
        mycursor.execute("""
            SELECT t.Subject, t.StartTime, t.EndTime, t.facultyId
            FROM timetable t
            WHERE t.Branch = %s
                AND t.StartTime <= %s 
                AND t.EndTime >= %s 
        """, (branch, current_time, current_time))

        timetable_entries = mycursor.fetchall()

        if not timetable_entries:
            print(f"No timetable entries found for branch {branch} at the current time.")
            return

        # Now we can assume that only one faculty is assigned for a specific time to take class
        subject, start_time, end_time, faculty_id = timetable_entries[0]

        # Here we can check that if attencdance is already marked for the student for the session
        mycursor.execute("""
            SELECT *
            FROM attendance
            WHERE date = %s AND time >= %s AND time <= %s AND StudentID = %s
        """, (datetoday, start_time, end_time, student_id))
        existing_attendance = mycursor.fetchone()

        if existing_attendance:
            print("Attendance already marked for the student.")
            return

        # Insert record in attendance
        mycursor.execute("""
            INSERT INTO attendance (fullName, StudentID, Branch, Course, attend_status, time, date, subject)
            SELECT fullName, %s, Branch, Course, %s, %s, %s, %s
            FROM student_data
            WHERE StudentID = %s
        """, (student_id, status, current_time, datetoday, subject, student_id))

        # Applying logic for updating attendance record
        sql_query = """
        UPDATE attendance AS A
        JOIN (
            SELECT 
                subject, StudentID,
                ROUND((SUM(CASE WHEN attend_status = 'Present' THEN 1 ELSE 0 END) / COUNT(*)) * 100,2) AS percentage
            FROM 
                attendance GROUP BY subject, StudentID
        ) AS T
        ON A.subject = T.subject AND A.StudentID = T.StudentID
        SET A.percentage = T.percentage;
        """

        # Execute the query
        mycursor.execute(sql_query)

        # Commit the transaction
        mydb.commit()
        print("Attendance marked successfully.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if mycursor:
            mycursor.close()
        if mydb:
            mydb.close()


class student_mangement_Auth_Routes:
    def __init__(self, app):
        self.app = app
        self.route()

    def add_student_password(self):
        password_length = 8
        characters = string.ascii_letters + string.digits
        password = ''.join(random.choice(characters) for _ in range(password_length))
        return password


    def student_id_add_student_id(self):
        assigned_by = "admin"
        return assigned_by



    def route(self):
        @self.app.route('/start', methods=['GET'])
        def start():
            if 'face_recognition_model.pkl' not in os.listdir('website/static'):
                return render_template('faculty_dashboard/faculty_dashboard.html', totalreg=totalreg(),
                                       datetoday2=datetoday2,
                                       mess='There is no trained model in the static folder. Please add a new face to continue.')

            ret = True
            cap = cv2.VideoCapture(0)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

            all_student_ids = get_all_student_ids()

            while ret:
                ret, frame = cap.read()
                faces = extract_faces(frame)
                detected_student_ids = []
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (86, 32, 251), 1)
                    cv2.rectangle(frame, (x, y), (x + w, y - 40), (86, 32, 251), -1)
                    face = cv2.resize(frame[y:y + h, x:x + w], (50, 50))
                    identified_person = identify_face(face.reshape(1, -1))[0]

                    student_name = get_student_name(identified_person)

                    if student_name:
                        confirmation = request_confirmation(student_name)
                        if confirmation:
                            add_attendance(identified_person, 'Present')
                        else:
                            add_attendance(identified_person, 'Absent')

                    if student_name:
                        detected_student_ids.append(identified_person)

                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 1)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (50, 50, 255), 2)
                    cv2.rectangle(frame, (x, y - 40), (x + w, y), (50, 50, 255), -1)
                    cv2.putText(frame, f'{identified_person}', (x, y - 15), cv2.FONT_HERSHEY_COMPLEX, 1,
                                (255, 255, 255), 1)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (50, 50, 255), 1)

                for student_id in all_student_ids:
                    if student_id not in detected_student_ids:
                        add_attendance(f"Student_{student_id}", 'Absent')

                resized_frame = cv2.resize(frame, (640, 480))

                imgBackground[162:162 + 480, 55:55 + 640] = resized_frame
                cv2.imshow('Attendance', imgBackground)
                key = cv2.waitKey(1)
                if key == 27 or key == ord('q'):
                   break

            cap.release()
            cv2.destroyAllWindows()
            return render_template('faculty_dashboard/faculty_dashboard.html', totalreg=totalreg(),
                                   datetoday2=datetoday2)

        def get_all_student_ids():
            try:
                mydb = mysql.connector.connect(
                    host='localhost',
                    user='root',
                    password='',
                    database='vision'
                )
                mycursor = mydb.cursor()
                mycursor.execute("SELECT StudentID FROM student_data")
                student_ids = [row[0] for row in mycursor.fetchall()]
                mycursor.close()
                mydb.close()

                return student_ids

            except Exception as e:
                print(f"Koi error aaya toh bata dena Anni bhai: {e}")
                return []

        def request_confirmation(name):
            StudentID = name.split('_')[1]
            if StudentID:
                print(f"{StudentID} is Anni present hojao bhai.")
                return True
            else:
                print(f"{StudentID} is absent yahi maroo.")
                return False

        def get_student_name(student_id):
            student_id = student_id.split('_')[1]
            try:
                mydb = mysql.connector.connect(
                    host='localhost',
                    user='root',
                    password='',
                    database='vision'
                )

                mycursor = mydb.cursor()
                mycursor.execute("SELECT fullName, Branch,Course, StudentID FROM student_data WHERE StudentID = %s",
                                 (student_id,))
                student_data = mycursor.fetchone()
                print(f"Student Id yaha dikhaya shai sa aarhi hain abb {student_id}")

                if student_data:
                    print(f"Student ka data dikhaya {student_data}")
                    student_name = student_data[0]
                    student_id = student_data[1]
                    student_entry = f"{student_name}_{student_id}"
                    print(f"Student ki entry show kare {student_entry}")
                    return student_entry

                else:
                    print("Student nahi hain Anni bhai")
                    return None

            except Exception as e:
                print(f"Kya hee galat ho raha hain Anni bhai : {e}")
                return None

        @self.app.route('/addStudent', methods=['POST', 'GET'])
        def register_student():
            if request.method == 'POST':
                action = request.form['action']
                StudentID = request.form['StudentID']
                if action == 'accept':
                    fullName = request.form['fullName']
                    FatherName = request.form['FatherName']
                    Course = request.form['Course']
                    Branch = request.form['Branch']
                    Year = request.form['Year']
                    DOB = request.form['DOB']
                    email = request.form['email_id']
                    gender = request.form['gender']
                    PhoneNumber = request.form['PhoneNumber']
                    updated_by = request.form['updated_by']
                    password = self.add_student_password()

                    # Update student data in the database
                    mydb = mysql.connector.connect(
                        host='localhost',
                        user='root',
                        password='',
                        database='vision'
                    )

                    mycursor = mydb.cursor()
                    mycursor.execute(
                        "UPDATE student_data SET fullName =%s, FatherName=%s, Course=%s, Branch=%s, Year=%s, DOB=%s, email_id=%s, gender=%s, PhoneNumber=%s, updated_by = %s,password=%s WHERE StudentID=%s",
                        (
                            fullName, FatherName, Course, Branch, Year, DOB, email, gender, PhoneNumber,updated_by,password, StudentID)
                    )


                    mydb.commit()
                    mycursor.close()

                    email_receiver = email

                    subject = "Student Login Details"

                    body = (
                        f"You have been successfully registered\n"
                        f"Login Credentials\n"
                        f"UserName : {StudentID}\n"
                        f"Password : {password}\n"

                    )
                    em = EmailMessage()
                    em['From'] = email_sender
                    em['To'] = email_receiver
                    em['subject'] = subject
                    em.set_content(body)

                    context = ssl.create_default_context()
                    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
                        smtp.login(email_sender, email_sender_pas)
                        smtp.send_message(em)
                    print("Updated by:", updated_by)

                    if updated_by == 'admin':
                        print("Admin clicked accept button")
                        return redirect("/viewStudent")
                elif action == 'deny':
                    mydb = mysql.connector.connect(
                        host='localhost',
                        user='root',
                        password='',
                        database='vision'
                    )
                    mycursor = mydb.cursor()
                    mycursor.execute("DELETE FROM student_data WHERE StudentID = %s", (StudentID,))
                    mydb.commit()
                    mycursor.close()
                    return redirect("/addStudent")
            mydb = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='vision'
            )
            mycursor = mydb.cursor()
            mycursor.execute("SELECT * FROM student_data WHERE updated_by != 'admin'")
            data = mycursor.fetchall()
            mycursor.close()
            return render_template("admin_dashboard/addStudent.html", manage_profile_request_by_student=data, admin="admin")

        @self.app.route('/viewInsitestudent')
        def viewInsitestudent():
            mydb = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='vision'
            )
            mycursor = mydb.cursor()
            StudentID = request.args.get('StudentID')
            print("Received department name:", StudentID)
            mycursor = mydb.cursor(dictionary=True)
            # mycursor = mydb.cursor(MySQLdb.cursors.DictCursor)
            mycursor.execute("SELECT * FROM student_data WHERE StudentID = %s", (StudentID,))
            data_s = mycursor.fetchone()

            if data_s:
                print("Retrieved data:", data_s)
                return render_template("admin_dashboard/viewInsitestudent.html", data_s=data_s)

        @self.app.route('/viewStudent', methods=['POST', 'GET'])
        def viewStudent():
            mydb = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='vision'
            )
            mycursor = mydb.cursor()
            mycursor.execute("SELECT * FROM student_data WHERE updated_by = 'admin'")
            data_s = mycursor.fetchall()
            mycursor.close()

            return render_template("admin_dashboard/viewStudent.html", data_s=data_s)

        @self.app.route('/viewTablestudent')
        def viewTablestudent():
            mydb = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='vision'
            )
            mycursor = mydb.cursor()
            StudentID = request.args.get('StudentID')
            print("Received department name:", StudentID)
            mycursor = mydb.cursor(dictionary=True)
            # mycursor = mydb.cursor(MySQLdb.cursors.DictCursor)
            mycursor.execute("SELECT * FROM student_data WHERE StudentID = %s", (StudentID,))
            data_f = mycursor.fetchone()

            if data_f:
                print("Retrieved data:", data_f)
                return render_template("admin_dashboard/viewTablestudent.html", data_f=data_f)

        @self.app.route('/password_profile_student', methods=['POST', 'GET'])
        def passwordupdate():
            if request.method == 'POST':
                if 'StudentID' in session:
                    StudentID = session['StudentID']
                    current_password = request.form['current_password']
                    new_password = request.form['new_password']
                    confirm_new_password = request.form['confirm_new_password']

                    try:
                        mydb = mysql.connector.connect(
                            host='localhost',
                            user='root',
                            password='',
                            database='vision'
                        )
                        mycursor = mydb.cursor()

                        mycursor.execute("SELECT password FROM student_data WHERE StudentID = %s", (StudentID,))
                        result = mycursor.fetchone()

                        if result:
                            current_password_from_db = result[
                                0]
                        else:
                            flash("Student with the given StudentID not found", "error")
                            return render_template('student_dashboard/password_info.html')

                        if current_password_from_db == current_password:
                            if new_password == confirm_new_password:
                                mycursor.execute("UPDATE student_data SET password = %s WHERE StudentID = %s",
                                                 (new_password, StudentID))
                                mydb.commit()
                                flash("Password updated successfully", "success")
                            else:
                                flash("New passwords do not match", "error")
                        else:
                            flash("Incorrect current password", "error")

                    except mysql.connector.Error as err:
                        flash("An error occurred while updating the password", "error")
                    finally:
                        mycursor.close()
                        mydb.close()

            return render_template('student_dashboard/password_info.html')

        @self.app.route('/reset_password_request_student', methods=['GET', 'POST'])
        def reset_password_request_student():
            if request.method == 'POST':
                email = request.form['email_id']
                try:
                    mydb = connect_to_db()
                    cursor = mydb.cursor()
                    cursor.execute("SELECT `StudentID` FROM `student_data` WHERE `email_id` = %s", (email,))
                    result = cursor.fetchone()
                    cursor.close()

                    if result:
                        user_id = result[0]
                        token = generate_unique_token()
                        store_token_in_database(user_id, token)
                        send_password_reset_email(email, token)
                        flash('Check your email for password reset instructions.')
                    else:
                        flash('Email not found.', 'error')

                except mysql.connector.Error as err:
                    flash(f"Error requesting password reset: {err}", "error")

                return redirect('/login')

            return render_template('student_dashboard/reset_password_request_student.html')

        @self.app.route('/reset_password_student/<token>', methods=['GET', 'POST'])
        def reset_password_student(token):
            user_id = validate_token(token)

            if user_id is None:
                flash('Invalid or expired token. Please request a new password reset.')
                return redirect('/reset_password_request_student')

            if request.method == 'POST':
                new_password = request.form['new_password']
                confirm_password = request.form['confirm_password']

                if new_password != confirm_password:
                    flash('Passwords do not match. Please try again.')
                else:
                    update_password(user_id, new_password)
                    flash('Your password has been reset. You can now log in with your new password.')
                    return redirect('/login')

            return render_template('student_dashboard/reset_password_student.html', token=token)


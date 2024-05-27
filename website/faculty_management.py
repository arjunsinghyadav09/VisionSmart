from flask import render_template, request, redirect, flash, jsonify, url_for,session
import mysql.connector
import string
import random
import smtplib
from dotenv import load_dotenv
from email.message import EmailMessage
import os
import ssl
from datetime import datetime, timedelta
import uuid

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

def send_password_reset_email(email, token):
    try:
        subject = "Password Reset Request"
        reset_link = f"http://127.0.0.1:5000/reset_password/{token}"
        body = f"Click the following link to reset your password: {reset_link}"

        context = ssl.create_default_context()
        em = EmailMessage()
        em['From'] = email_sender
        em['To'] = email
        em['Subject'] = subject
        em.set_content(body)

        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(email_sender, email_sender_pas)
            smtp.sendmail(email_sender, email, em.as_string())
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
            "UPDATE `faculty_data` SET `password` = %s WHERE `facultyId` = %s",
            (new_password, user_id)
        )
        mydb.commit()
        cursor.close()
    except mysql.connector.Error as err:
        flash(f"Error updating password: {err}", "error")
class faculty_mangement_Auth_Routes:
    def __init__(self, app):
        self.app = app
        self.route()

    def add_student_password(self):
        password_length = 8
        characters = string.ascii_letters + string.digits
        password = ''.join(random.choice(characters) for _ in range(password_length))
        return password

    def update_faculty_add_faculty_id(self):
        assigned_by = "admin"
        return assigned_by

    def route(self):
        @self.app.route('/addfaculty', methods=['POST', 'GET'])
        def addfaculty():
            if request.method == 'POST':
                action = request.form['action']
                facultyId = request.form['facultyId']
                if action == 'accept':
                    degree = request.form['degree']
                    specialization = request.form['specialization']
                    Experience = request.form['Experience']
                    fullName = request.form['fullName']
                    Occupation = request.form['Occupation']
                    department = request.form['department']
                    Year = request.form['Year']
                    DOB = request.form['DOB']
                    email = request.form['email']
                    gender = request.form['gender']
                    ContactNumber = request.form['ContactNumber']
                    updated_by = request.form['updated_by']
                    password = self.add_student_password()



                    if updated_by == 'admin':
                        # Update faculty data in the database
                        mydb = mysql.connector.connect(
                            host='localhost',
                            user='root',
                            password='',
                            database='vision'
                        )
                        mycursor = mydb.cursor()
                        mycursor.execute(
                            "UPDATE faculty_data SET degree=%s, specialization=%s, Experience=%s, fullName=%s, Occupation=%s, department=%s, Year=%s, DOB=%s, email=%s, gender=%s, ContactNumber=%s, updated_by=%s,password=%s WHERE facultyId=%s",
                            (
                                degree, specialization, Experience, fullName, Occupation, department, Year, DOB, email,
                                gender,
                                ContactNumber, updated_by, password, facultyId))

                        mydb.commit()
                        mycursor.close()



                        email_receiver = email

                        subject = "Student Login Details"

                        body = (
                            f"You have been successfully registered\n"
                            f"Login Credentials\n"
                            f"Login Id : {facultyId}\n"
                            f"PASSOWRD : {password}\n"

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
                elif action == 'deny':
                    mydb = mysql.connector.connect(
                        host='localhost',
                        user='root',
                        password='',
                        database='vision'
                    )
                    mycursor = mydb.cursor()
                    mycursor.execute("DELETE FROM faculty_data WHERE facultyId = %s", (facultyId,))
                    mydb.commit()
                    mycursor.close()

                    return redirect("/addfaculty")

                return redirect("/viewFaculty")

            mydb = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='vision'
            )
            mycursor = mydb.cursor()
            mycursor.execute("SELECT * FROM faculty_data WHERE updated_by != 'admin'")
            data = mycursor.fetchall()
            mycursor.close()

            return render_template("admin_dashboard/addfaculty.html", manage_profile_request=data, admin="admin")

        @self.app.route('/viewFaculty', methods=['POST', 'GET'])
        def viewFaculty():
            mydb = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='vision'
            )
            mycursor = mydb.cursor()
            mycursor.execute("SELECT * FROM faculty_data WHERE updated_by = 'admin'")
            data = mycursor.fetchall()
            mycursor.close()
            if data:


                return render_template("admin_dashboard/viewFaculty.html",data=data)

        @self.app.route('/viewInsitefaculty')
        def viewInsitefaculty():
            mydb = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='vision'
            )
            mycursor = mydb.cursor()
            facultyId = request.args.get('facultyId')
            print("Received department name:", facultyId)
            mycursor = mydb.cursor(dictionary=True)
            # mycursor = mydb.cursor(MySQLdb.cursors.DictCursor)
            mycursor.execute("SELECT * FROM faculty_data WHERE facultyId = %s", (facultyId,))
            data_f = mycursor.fetchone()

            if data_f:
                print("Retrieved data:", data_f)
                return render_template("admin_dashboard/viewInsitefaculty.html",data_f=data_f)



        @self.app.route('/viewTablefaculty')
        def viewTablefaculty():
            mydb = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='vision'
            )
            mycursor = mydb.cursor()
            facultyId = request.args.get('facultyId')
            print("Received department name:", facultyId)
            mycursor = mydb.cursor(dictionary=True)
            # mycursor = mydb.cursor(MySQLdb.cursors.DictCursor)
            mycursor.execute("SELECT * FROM faculty_data WHERE facultyId = %s", (facultyId,))
            data_f = mycursor.fetchone()

            if data_f:
                print("Retrieved data:", data_f)
                return render_template("admin_dashboard/viewTablefaculty.html", data_f=data_f)

        @self.app.route('/timetable', methods=['GET', 'POST'])
        def timetable():
            if request.method == 'POST':
                facultyInfo = request.form.get('facultyInfo')
                if facultyInfo:
                    # Extract facultyId and fullName from facultyInfo
                    facultyId, fullName = facultyInfo.split(' - ')
                else:
                    # Handle missing facultyInfo
                    return "Faculty information is missing", 400

                subject = request.form.get('subject')
                branch = request.form.get('branch')
                startTime = request.form.get('startTime')
                endTime = request.form.get('endTime')
                day = request.form.get('day')


                if not all([subject, branch, startTime, endTime, day]):
                    # Handle missing fields
                    return "All fields are required", 400

                mydb = mysql.connector.connect(
                    host='localhost',
                    user='root',
                    password='',
                    database='vision'
                )
                mycursor = mydb.cursor()
                mycursor.execute(
                    "INSERT INTO timetable (facultyId, fullName, subject, branch, startTime, endTime, day) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (facultyId, fullName, subject, branch, startTime, endTime, day)
                )
                mydb.commit()
                mycursor.close()
                return redirect('/timetable')

            mydb = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='vision'
            )
            mycursor = mydb.cursor(dictionary=True)
            mycursor.execute("SELECT CONCAT(facultyId, ' - ', fullName) AS faculty_info FROM faculty_data")
            faculty_data = mycursor.fetchall()
            mycursor.close()
            return render_template("admin_dashboard/timetable.html", faculty_data=faculty_data)

        @self.app.route('/password_profile', methods=['POST', 'GET'])
        def passupdate():
            if request.method == 'POST':
                if 'facultyId' in session:
                    facultyId = session['facultyId']
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

                        mycursor.execute("SELECT password FROM faculty_data WHERE facultyId = %s", (facultyId,))
                        result = mycursor.fetchone()

                        if result:
                            current_password_from_db = result[
                                0]
                        else:
                            flash("Faculty with the given facultyId not found", "error")
                            return render_template('faculty_dashboard/password_info.html')

                        if current_password_from_db == current_password:
                            if new_password == confirm_new_password:
                                mycursor.execute("UPDATE faculty_data SET password = %s WHERE facultyId = %s",
                                                 (new_password, facultyId))
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

            return render_template('faculty_dashboard/password_info.html')

        @self.app.route('/reset_password_request', methods=['GET', 'POST'])
        def reset_password_request():
            if request.method == 'POST':
                email = request.form['email']
                try:
                    mydb = connect_to_db()
                    cursor = mydb.cursor()
                    cursor.execute("SELECT `facultyId` FROM `faculty_data` WHERE `email` = %s", (email,))
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

                return redirect('/faculty_login')

            return render_template('reset_password_request.html')

        @self.app.route('/reset_password/<token>', methods=['GET', 'POST'])
        def reset_password(token):
            user_id = validate_token(token)

            if user_id is None:
                flash('Invalid or expired token. Please request a new password reset.')
                return redirect('/reset_password_request')

            if request.method == 'POST':
                new_password = request.form['new_password']
                confirm_password = request.form['confirm_password']

                if new_password != confirm_password:
                    flash('Passwords do not match. Please try again.')
                else:
                    update_password(user_id, new_password)
                    flash('Your password has been reset. You can now log in with your new password.')
                    return redirect('/faculty_login')

            return render_template('reset_password.html', token=token)




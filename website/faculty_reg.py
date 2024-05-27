from flask import render_template, request,flash
import mysql.connector
from mysql.connector import IntegrityError

class Faculty_reg_Auth_Routes:
    def __init__(self, app):
        self.app = app
        self.route()

    def route(self):
        @self.app.route('/faculty_register', methods=['POST', 'GET'])

        def register_faculty():
            mydb = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='vision'
            )

            mycursor = mydb.cursor()
            if request.method == 'POST':
                try:
                    register = request.form
                    facultyId = register['facultyId']
                    degree=register['degree']
                    specialization=register['specialization']
                    Experience=register['Experience']
                    fullName=register['fullName']
                    Occupation=register['Occupation']
                    department=register['department']
                    Year=register['Year']
                    DOB=register['DOB']
                    email=register['email']
                    gender = register['gender']
                    ContactNumber=register['ContactNumber']

                    img = request.files['img']
                    img.save('website/static/uploaded/' + img.filename)
                    img_filename = img.filename


                    mycursor.execute(
                        "INSERT INTO faculty_data (facultyId, degree, specialization, Experience, fullName, Occupation, department, Year, DOB, email,gender,ContactNumber,img) VALUES (%s,%s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                        (facultyId, degree, specialization, Experience, fullName, Occupation, department, Year, DOB, email,gender,ContactNumber,img_filename)
                    )


                    mydb.commit()
                    mycursor.close()
                    flash("Registration successful!", "success")
                except IntegrityError as e:
                    mydb.rollback()  # Rollback the transaction
                    flash("Faculty ID already exists. Please use a different Faculty ID.", "error")

            return render_template("registerFaculty.html")












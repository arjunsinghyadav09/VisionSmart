from flask import Blueprint,render_template, request,redirect,session,flash
import mysql.connector
import mysql
from .student_reg import StudentRegAuthRoutes
from .faculty_reg import Faculty_reg_Auth_Routes
from .faculty_management import faculty_mangement_Auth_Routes
from .stuent_managemnt import student_mangement_Auth_Routes
from .contact_us_form import Contact_reg_Auth_Routes
import os

auth = Blueprint('auth', __name__)

Student_data_store= StudentRegAuthRoutes(auth)

Faculty_data_store = Faculty_reg_Auth_Routes(auth)

Contact_data_store = Contact_reg_Auth_Routes(auth)


@auth.route('/login', methods=['POST', 'GET'])
def student_login():
    if request.method == 'POST':
        StudentID = request.form['StudentID']
        password = request.form['password']

        mydb = connect_to_db()
        mycursor = mydb.cursor()


        mycursor.execute(
            "SELECT StudentID, fullName FROM student_data WHERE StudentID=%s AND password=%s",
            (StudentID, password)
        )
        student_data = mycursor.fetchone()
        r = mycursor.fetchall()
        count = mycursor.rowcount

        if student_data:
            session['is_student'] = True
            session['StudentID'] = StudentID
            session['fullName'] = student_data[1]
            image_filename = student_data[0]
            print(f"Is Student {StudentID}")

            image_path = os.path.join('website', 'static', 'uploaded', image_filename)

            if os.path.isfile(image_path):
                session['img'] = '/static/uploaded/' + image_filename
                print(f"Is Student {StudentID}")

                return Student_dashboard()
            else:
                flash("Image file not found", "error")
            if session['is_student']:
                return Student_dashboard()
        elif count > 1:
            return 'More than one user found'
        else:
            flash("Invalid Student ID or password", "error")
    return render_template("login.html")
def connect_to_db():
    return mysql.connector.connect(**db_config)

@auth.route('/faculty_login', methods=['POST', 'GET'])
def faculty_login():
    if request.method == 'POST':
        facultyId = request.form['facultyId']
        password = request.form['password']

        mydb = connect_to_db()
        mycursor = mydb.cursor()


        mycursor.execute(
            "SELECT facultyId, fullName FROM faculty_data WHERE facultyId=%s AND password=%s",
            (facultyId, password)
        )
        faculty_data = mycursor.fetchone()
        r = mycursor.fetchall()
        count = mycursor.rowcount

        if faculty_data:
            session['is_faculty'] = True
            session['facultyId'] = 	facultyId
            session['fullName'] = faculty_data[1]
            image_filename =faculty_data[0]
            print(f"Is Faculty {facultyId}")

            image_path = os.path.join('website', 'static', 'uploaded', image_filename)

            if os.path.isfile(image_path):
                session['img'] = '/static/uploaded/' + image_filename
                print(f"Is Faculty {facultyId}")

                return faculty_dashboard()
            else:
                flash("Image file not found", "error")
            if session['is_faculty']:
                return faculty_dashboard()
        elif count > 1:
            return 'More than one user found'
        else:
            flash("Invalid Faculty ID or password", "error")

    return render_template("faculty_login.html")


@auth.route('/faculty_dashboard')
def faculty_dashboard():
    if 'facultyId' in session:
        mydb = connect_to_db()
        mycursor = mydb.cursor()
        facultyId = session['facultyId']

        mycursor.execute("SELECT Branch, subject FROM timetable WHERE facultyId = %s", (facultyId,))
        timetable_data = mycursor.fetchall()

        mycursor.execute("""
                    SELECT s.fullName, s.StudentID, t.Branch, t.subject 
                    FROM student_data s
                    INNER JOIN timetable t ON s.Branch = t.Branch 
                    WHERE t.facultyId = %s
                """, (facultyId,))
        student_data = mycursor.fetchall()

        student_percentage = {}
        for student in student_data:
            student_id = student[1]
            branch = student[2]
            subject = student[3]
            mycursor.execute("SELECT AVG(percentage) FROM attendance WHERE StudentID = %s AND Branch = %s AND subject=%s",
                             (student_id, branch,subject))
            percentage = mycursor.fetchone()[0]
            student_percentage[student_id] = percentage
            print(f"Student percentage {student_percentage[student_id]}")

        mycursor.close()
        mydb.close()

        return render_template("faculty_dashboard/faculty_dashboard.html", timetable_data=timetable_data,
                               student_data=student_data, student_percentage=student_percentage)
    else:
        return redirect('/faculty_login')


@auth.route('/viewAttendence')
def viewAttendence():
    StudentID = request.args.get('StudentID')
    mydb = connect_to_db()
    mycursor = mydb.cursor()
    mycursor.execute("SELECT fullName, Branch, StudentID,img FROM student_data WHERE StudentID = %s", (StudentID,))
    student_details = mycursor.fetchone()
    mycursor.execute("SELECT date, attend_status FROM attendance WHERE StudentID = %s", (StudentID,))
    attendance_data = mycursor.fetchall()
    mycursor.close()
    mydb.close()

    return render_template("faculty_dashboard/viewAttendence.html", student_details=student_details, attendance_data=attendance_data)


@auth.route('/student_dash')
def Student_dashboard():
    if 'StudentID' in session:
        mydb = connect_to_db()
        mycursor = mydb.cursor()
        StudentID = session['StudentID']
        mycursor.execute("SELECT fullName, branch, year, StudentID FROM student_data WHERE StudentID = %s",
                         (StudentID,))
        student_data = mycursor.fetchone()
        mycursor.execute("SELECT DISTINCT percentage, subject FROM attendance WHERE StudentID = %s", (StudentID,))
        timetable_data = mycursor.fetchall()
        mycursor.close()
        mycursor.close()
        mydb.close()

        return render_template("student_dashboard/StudentProfile.html",student_data=student_data,timetable_data=timetable_data)

    else:
        return redirect('/login')


db_config = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "vision"
}

def connect_to_db():
    return mysql.connector.connect(**db_config)

@auth.route('/login_admin', methods=['POST', 'GET'])
def admin_Login():
    mydb = mysql.connector.Connect(
        host='localhost',
        user='root',
        password='',
        database='vision'
    )
    mycursor = mydb.cursor()
    if request.method == 'POST':
        admin_id = request.form['admin_id']
        password = request.form['password']
        print(f"Admin Id {admin_id}")

        mydb = connect_to_db()
        mycursor = mydb.cursor()

        mycursor.execute(
            "SELECT admin_id FROM admin_dash WHERE admin_id=%s AND password=%s",
            (admin_id, password)
        )
        admin_data = mycursor.fetchone()
        count = mycursor.rowcount

        if admin_data:
            print(f"Admin data {admin_id}")
            session['admin_id'] = admin_data[0]
            session['is_admin'] = True
            if session['is_admin']:
                print("Admin dashboard")
                return admin_dashboard()

        else:
            flash("Invalid admin ID or password", "error")
    mydb.commit()
    mycursor.close()

    return render_template("admin_login.html")

@auth.route('/Admin Dashboard')
def admin_dashboard():
    mydb = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='vision'
    )
    mycursor = mydb.cursor()

    # Define default values
    num_new_student = 0
    num_new_faculty = 0
    num_active_student = 0
    num_active_faculty = 0
    recent_activities = []

    try:
        # Fetch counts from respective tables
        mycursor.execute("SELECT COUNT(*) FROM student_data WHERE updated_by !='admin'")
        num_new_student = mycursor.fetchone()[0]

        mycursor.execute("SELECT COUNT(*) FROM faculty_data WHERE updated_by !='admin'")
        num_new_faculty = mycursor.fetchone()[0]

        mycursor.execute("SELECT COUNT(*) FROM student_data WHERE updated_by = 'admin'")
        num_active_student = mycursor.fetchone()[0]

        mycursor.execute("SELECT COUNT(*) FROM faculty_data WHERE updated_by = 'admin'")
        num_active_faculty = mycursor.fetchone()[0]

        # Fetch recent activity data
        mycursor.execute("SELECT name, member_type, date, status FROM recent_activity ORDER BY date DESC LIMIT 10")
        recent_activities = mycursor.fetchall()

    except Exception as e:
        print("Error:", str(e))

    finally:
        mycursor.close()
    return render_template("admin_dashboard/dashboard.html",
                           num_new_student=num_new_student,
                           num_new_faculty=num_new_faculty,
                           num_active_student=num_active_student,
                           num_active_faculty=num_active_faculty,
                           recent_activities=recent_activities)

Faculty_mange_data=faculty_mangement_Auth_Routes(auth)

Student_manage_data=student_mangement_Auth_Routes(auth)

@auth.route('/timetable_tables')
def timetable_TABLE():
    return render_template("faculty_dashboard/timetable_tables.html")
from flask import Flask, render_template, request, flash
import mysql.connector
from mysql.connector import IntegrityError

app = Flask(__name__)

class Contact_reg_Auth_Routes:
    def __init__(self, app):
        self.app = app
        self.route()

    def route(self):
        @self.app.route('/contactus', methods=['POST', 'GET'])
        def register_contact_us():
            if request.method == 'POST':
                mydb = mysql.connector.connect(
                    host='localhost',
                    user='root',
                    password='',
                    database='vision'
                )
                mycursor = mydb.cursor()
                try:
                    register = request.form
                    f_name = register['f_name']
                    l_name = register['l_name']
                    email = register['email']
                    mobile = register['mobile']
                    message = register['message']

                    mycursor.execute(
                        "INSERT INTO contact_us (f_name, l_name, email, mobile, message) VALUES (%s,%s,%s,%s,%s)",
                        (f_name, l_name, email, mobile, message)
                    )
                    mydb.commit()
                    mycursor.close()

                    flash("Query successfully sent!", "success")
                except IntegrityError as e:
                    mydb.rollback()  # Rollback the transaction
                    flash("No more queries allowed.", "error")
                finally:
                    mydb.close()
            return render_template("contactus.html")
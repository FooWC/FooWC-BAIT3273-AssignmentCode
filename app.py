from distutils.log import debug
from flask import Flask, redirect, render_template, request, session
from pymysql import connections

import os
import boto3
import jinja2
import cgi
import pymysql
import mysql.connector
app = Flask(__name__,template_folder='templates')

#database connection
def mysqlconnect():
    # To connect MySQL database
    conn = pymysql.connect(
        host='localhost',
        user='root', 
        password = "",
        db='employeedb',
        )


#routes(INITIAL DONE)
@app.route('/')
def index():
    return render_template('home.html')


#route to go to sign up page (DONE)
@app.route('/NewEmp')
def NewEmp():
    return render_template('NewEmp.html')


#route to sign up new acc
@app.route('/SignInEmp',methods=['POST'])
def signUpNew():
    #getData
    empID = request.form['emp_id']
    empName = request.form['emp_name']
    empEmail=request.form['emp_email']
    empPassword = request.form['emp_pswd']
    skill = request.form['pri_skill']
    location = request.form['location']
    empImage = request.files['emp_image_file']

    #plugin database
    try :
        cur = mysql.connection.cursor()
        insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s, %s, %s)"
        cur.execute(insert_sql,(empID,empName,empPassword,skill,location,empImage))

    finally:
        cur.close()

    #return and view result
    return render_template('NewEmpDone.html',emp_id=empID,emp_name=empName,emp_email=empEmail,pri_skill=skill,locations=location,img=empImage)


#route (login to main page)
@app.route('/loginEmp',methods=['GET'])
def loginEmp():
    #getvalue from form
    empEmail = request.form['emp_email']    
    password = request.form['emp_pswd']

    #compare with database
    try:
        cur = mysql.connection.cursor()
        cur.execute("select * where employeeName=%s and employeePassword=%s",[empEmail,password])
        result=cur.fetchone()
        if result:
            
            return render_template('EmpHome.html')
        else:
            return redirect('home.html')
    except Exception as e:
        print(e)
    finally:
        cur.close()

#route to attendance
@app.route('/Attendance')
def NewAtt():
    return render_template('Attendance.html')


#sign-in attendance
@app.route('/attendanceEmp',methods=['GET','POST'])
def checkIn():
    t=request.form['timeNow']
    empName=request.form['emp_name']
    #insert to database
    try :
        cur = mysql.connection.cursor()
        insert_sql = "INSERT INTO attendance VALUES (%s, %s)"
        cur.execute(insert_sql,(empName,t))
    except Exception as e:
        print(e)
    finally:
        cur.close()
    return render_template('DoneAttendance.html',emp_name=empName, time=t)

#tochange
if __name__ == "__main__":
    app.run(debug==True)
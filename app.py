from distutils.log import debug
from flask import Flask, redirect, render_template, request, session
from pymysql import connections
from config import *
import os
import boto3
import jinja2
import cgi
import pymysql

app = Flask(__name__,template_folder='templates')

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
    emp_image_file= request.files['image_file']
    
    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s, %s, %s)"
    cur = db_conn.cursor()
    
    if emp_image_file.filename == "":
        return "Please select a file"
    

    #plugin database
    try :
        cur.execute(insert_sql,(empID,empName,empPassword,skill,location,empImage))
        db_conn.commit()
        
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        s3 = boto3.resource('s3')
        
        try:
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)

        except Exception as e:
            return str(e)
    
    finally:
        cur.close()

    #return and view result
    return render_template('NewEmpDone.html',emp_id=empID,emp_name=empName,emp_email=empEmail,pri_skill=skill,locations=location,img=empImage)


#route (login to main page)
@app.route('/loginEmp',methods=['GET','POST'])
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
        cur.execute(insert_sql,(t,empName))
    except Exception as e:
        print(e)
    finally:
        cur.close()
    return render_template('DoneAttendance.html',emp_name=empName, time=t)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)

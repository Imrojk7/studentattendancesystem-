from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import time
from datetime import date
from datetime import datetime


app = Flask(__name__)
mysql = MySQL(app)

app.secret_key = 'system'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'login'

@app.route('/')
def home():
    return render_template('index.html')
    
@app.route('/login', methods =['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s AND pwd = %s", (email, password))
        data = cur.fetchone()
        if data:
            session['email'] = email
            session['stu_id'] = data[0]
            session['loggedin'] = True
            if data[2] == '2':
                session['stu'] = True
                return redirect(url_for('stdashboard'))
            else:
                session['tutor'] = True
                tutor_id = data[0]
                session['tutor_id'] = tutor_id
                #cur.execute("SELECT * FROM course WHERE tutor_id = %s",(tutor_id,))
                #course_data = cur.fetchone()
                # course_id = course_data[0]
                #session['course_id'] = course_id
                return redirect(url_for('trdashboard'))
    return render_template('login.html')



@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('email', None)
    session.pop('adloggedin', None)
    return redirect(url_for('home'))

@app.route('/signup', methods =['GET', 'POST'])
def signup():
    msg=''
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM course")
    courses = cur.fetchall()
    if request.method == 'POST' and 'username' in request.form and 'usertype' in request.form and 'course' in request.form and 'phone' in request.form and 'email' in request.form and 'password' in request.form:
        username = request.form['username']
        usertype = request.form['usertype']
        phone = request.form['phone']
        email = request.form['email']
        password = request.form['password']
        course = request.form['course']
        if username and usertype and phone and email and password:
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM users WHERE email = %s",(email,))
            usdata = cur.fetchone()
            if usdata:
                cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cur.execute("SELECT * FROM course")
                courses = cur.fetchall()
                valert = 'User with this email id already exists. Please try with another one.'
                return render_template('signup.html', msg=valert,courses=courses)
            else:
                cur.execute("INSERT INTO users(username, usertype, phone, email, pwd) VALUES(%s, %s, %s, %s, %s)", (username, usertype, phone, email, password))
                mysql.connection.commit()
                msg = 'You are now registered and can log in'
                return render_template('signup.html', msg=msg,courses=courses)
        else:
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cur.execute("SELECT * FROM course")
            courses = cur.fetchall()
            valert = 'Fields can not be empty.'
            return render_template('signup.html', msg=valert,courses=courses)
    return render_template('signup.html',courses=courses)


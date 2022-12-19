from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import time
from datetime import date
from datetime import datetime


app = Flask(__name__)
mysql = MySQL(app)

app.secret_key = 'asystem'

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
            session['loggedin'] = True
            if data[2] == '2':
                session['stu'] = True
                return redirect(url_for('stdashboard'))
            else:
                session['tutor'] = True
                tutor_id = data[0]
                cur.execute("SELECT * FROM course WHERE tutor_id = %s",(tutor_id,))
                course_data = cur.fetchone()
                course_id = course_data[0]
                session['course_id'] = course_id
                return redirect(url_for('trdashboard'))
    return render_template('login.html')

@app.route('/logout')
def logout():
	session.pop('loggedin', None)
	session.pop('email', None)
	return redirect(url_for('home'))

@app.route('/signup', methods =['GET', 'POST'])
def signup():
    msg=''
    if request.method == 'POST' and 'username' in request.form and 'usertype' in request.form and 'course' in request.form and 'phone' in request.form and 'email' in request.form and 'password' in request.form:
        username = request.form['username']
        usertype = request.form['usertype']
        phone = request.form['phone']
        email = request.form['email']
        password = request.form['password']
        course = request.form['course']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users(username, usertype, phone, email, pwd) VALUES(%s, %s, %s, %s, %s)", (username, usertype, phone, email, password))
        mysql.connection.commit()
        if usertype == '1':
            cur.execute("SELECT MAX( id ) FROM users")
            inserted_id = cur.fetchone()
            cur.execute("INSERT INTO course(tutor_id,course_id) VALUES(%s,%s)",(inserted_id,course))
            mysql.connection.commit()
        msg = 'You are now registered and can log in'
        return render_template('signup.html', msg=msg)
    return render_template('signup.html')


@app.route('/trdashboard', methods=['GET', 'POST'])
def trdashboard():
    email = session['email']
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM users WHERE usertype = 2")
    classdata = cur.fetchall()
    cur.execute("SELECT * FROM users WHERE email = %s",(email,))
    tutor_data = cur.fetchone()
    tutor_id = tutor_data['id']
    cur.execute("SELECT * FROM course WHERE tutor_id = %s",(tutor_id,))
    course_data = cur.fetchone()
    course_id = course_data['id']
    if request.args.get('meetmsg'):
        msg1 = request.args['meetmsg'] 
        return render_template('tr_dashboard.html', msg=email, msg1=msg1, classdata=classdata,course_id=course_id)
    return render_template('tr_dashboard.html', msg=email, classdata=classdata,course_id=course_id)

@app.route('/updategrades', methods=['GET', 'POST'])
def updategrades():
    if session.get('tutor'):
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM users WHERE usertype = 2")
        all_data = cur.fetchall()
        course_id = session['course_id']
        return render_template('updategrades.html',alldata=all_data,course_id=course_id)
    return redirect(url_for('home'))

@app.route('/updategrade', methods=['GET','POST'])
def updategrade():
    if request.method == 'POST' and 'stu_id' in request.form and 'course_id' in request.form and 'grade' in request.form:
        stu_id = request.form['stu_id']
        course_id = request.form['course_id']
        grade = request.form['grade']
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM grades WHERE student_id = %s AND course_id = %s",(stu_id,course_id))
        data = cur.fetchone()
        if data:
            cur.execute("UPDATE grades set marks = %s WHERE student_id = %s AND course_id = %s",(grade,stu_id,course_id))
            mysql.connection.commit()
        else:
            cur.execute("INSERT INTO grades(student_id,marks,course_id) VALUES(%s,%s,%s)",(stu_id,grade,course_id))
            mysql.connection.commit()
        return '1'




@app.route('/stdashboard', methods=['GET', 'POST'])
def stdashboard():
    if session.get('stu'):
        msg = session['email']
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM course")
        coursedata = cur.fetchall()
        return render_template('st_dashboard.html', msg=msg, coursedata=coursedata)


@app.route('/presentstu',  methods =['GET', 'POST'])
def presentstu():
    if request.method == 'POST' and 'stu_id' in request.form and 'course_id' in request.form:
        stu_id = request.form['stu_id']
        course_id = request.form['course_id']
        curdate = date.today()
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('INSERT INTO attendance VALUES (NULL,%s, %s, %s,%s)', (stu_id, curdate,course_id,'p'))
        mysql.connection.commit()
        return '1'

@app.route('/absentstu',  methods =['GET', 'POST'])
def absentstu():
    if request.method == 'POST' and 'stu_id' in request.form and 'course_id' in request.form:
        stu_id = request.form['stu_id']
        course_id = request.form['course_id']
        curdate = date.today()
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('INSERT INTO attendance VALUES (NULL,%s, %s, %s,%s)', (stu_id, curdate,course_id,'a'))
        mysql.connection.commit()
        return '1'

def getusertodayatten(user_id,course_id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    today = date.today()
    today = str(today)
    cur.execute('SELECT * FROM attendance WHERE stu_id = %s AND curdate = %s AND course_id = %s', (user_id,today,course_id))
    data = cur.fetchone()
    if data:
        return 1
    else:
        return 2
app.jinja_env.globals.update(getusertodayatten=getusertodayatten) 

def gettutorcourse(user_email):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM users WHERE email = %s ",(user_email,))
    data = cur.fetchone()
    if data:
        tutor_id = data['id']
        cur.execute("SELECT * FROM course WHERE tutor_id = %s",(tutor_id,))
        course_data = cur.fetchone()
        if course_data:
            course_id = course_data['course_id']
            if course_id == 1:
                return 'Course A'
            if course_id == 2:
                return 'Course B'
            if course_id == 3:
                return 'Course C'
app.jinja_env.globals.update(gettutorcourse=gettutorcourse) 

def getstudentgrade(user_id,course_id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM grades WHERE student_id = %s AND course_id = %s",(user_id,course_id))
    data = cur.fetchone()
    if data:
        grade = data['marks']
        return grade
    else:
        return 'Enter grade'
app.jinja_env.globals.update(getstudentgrade=getstudentgrade) 

def getcoursegradeforst(stu_email,course_id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM users WHERE email = %s",(stu_email,))
    stu_data = cur.fetchone()
    if stu_data:
        stu_id = stu_data['id']
        cur.execute("SELECT * FROM grades WHERE student_id = %s AND course_id = %s",(stu_id,course_id))
        grade_data = cur.fetchone()
        if grade_data:
            cur.execute("SELECT * FROM course WHERE id = %s",(course_id,))
            course_data = cur.fetchone()
            if course_data:
                coursename_id = course_data['course_id']
                course_name = ''
                if coursename_id == 1:
                    course_name = 'Course A'
                if coursename_id == 2:
                    course_name = 'Course B'
                if coursename_id == 3:
                    course_name = 'Course C'
                str = course_name + ' - ' + grade_data['marks']
                return str
app.jinja_env.globals.update(getcoursegradeforst=getcoursegradeforst) 

def getstudentattendancetotaldays(stu_email,course_id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM users WHERE email = %s",(stu_email,))
    stu_data = cur.fetchone()
    if stu_data:
        stu_id = stu_data['id']
        cur.execute("SELECT * FROM attendance WHERE stu_id = %s AND course_id = %s",(stu_id,course_id))
        count_total_days = len(cur.fetchall())
        return count_total_days

app.jinja_env.globals.update(getstudentattendancetotaldays=getstudentattendancetotaldays) 

def getstudentattendeddays(stu_email,course_id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM users WHERE email = %s",(stu_email,))
    stu_data = cur.fetchone()
    if stu_data:
        stu_id = stu_data['id']
        cur.execute("SELECT * FROM attendance WHERE stu_id = %s AND atype = 'p' AND course_id = %s ",(stu_id,course_id))
        count_total_attended_days = len(cur.fetchall())
        return count_total_attended_days
app.jinja_env.globals.update(getstudentattendeddays=getstudentattendeddays) 

def getcoursenameforstu(course_id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM course WHERE id = %s",(course_id,))
    course_data = cur.fetchone()
    print(course_data)
    if course_data:
        coursename_id = course_data['course_id']
        course_name = ''
        if coursename_id == 1:
            course_name = 'Course A'
        if coursename_id == 2:
            course_name = 'Course B'
        if coursename_id == 3:
            course_name = 'Course C'
        return course_name
app.jinja_env.globals.update(getcoursenameforstu=getcoursenameforstu) 

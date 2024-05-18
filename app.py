
from flask import Flask,flash,redirect,render_template,url_for,request,jsonify,session,abort
from flask_session import Session
#from flask_mysqldb import MySQL
from datetime import date
#from datetime import datetime
from sdmail import sendmail
from tokenreset import token
from stoken1 import token1
#from stoken2 import token2
from database import execute_query
from itertools import zip_longest
import os
from datetime import datetime
import datetime

from itsdangerous import URLSafeTimedSerializer
from key import *

#import stripe
#stripe.api_key='sk_test_51MzcVYSDVehZUuDTkwGUYe8hWu2LGN0krI8iO5QOAEqoRYXx3jgRVgkY7WzXqQmpN62oMWM59ii76NKPrRzg3Gtr005oVpiW82'
app=Flask(__name__)
app.secret_key='hello'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)




import random
def genotp():
    u_c=[chr(i) for i in range(ord('A'),ord('Z')+1)]
    l_c=[chr(i) for i in range(ord('a'),ord('z')+1)]
    otp=''
    for i in range(3):
        otp+=random.choice(u_c)
        otp+=str(random.randint(0,9))
        otp+=random.choice(l_c)
    return otp
@app.route('/')
def home():
    return render_template('home.html')
@app.route('/ulogin',methods=['GET','POST'])
def ulogin():
    if session.get('user'):
        return redirect(url_for('users_dashboard'))
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        # cursor = mydb.cursor(buffered=True)
        count=execute_query('SELECT count(*) as count from students where Student_ID=%s and password=%s',[username,password])[0]
        # count=cursor.fetchone()[0]
        if count==(1,):
            session['user']=username
            if not session.get(username):
                session[username]={}
            return redirect(url_for("users_dashboard"))
        else:
            flash('Invalid username or password')
            return render_template('userlogin.html')
    return render_template('userlogin.html')

@app.route('/uregistration',methods=['GET','POST'])
def uregistration():
    data = execute_query('select * from departments')
    if request.method=='POST':
        code = request.form['code']
        id1=request.form['id']
        name=request.form['name']
        department= request.form['department']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        passout_year=request.form['passout_year']
        password = request.form['password']
        # code1="student@123"
        if code =="student@123":
            #cursor = mydb.cursor(buffered=True)
            count = execute_query('select count(*) from students where Student_ID=%s',[id1])[0]
            #count=cursor.fetchone()[0]
            count1 = execute_query('select count(*) from students where Email=%s',[email])[0]
            #count1=cursor.fetchone()[0]
            #cursor.close()
            if count==(1,):
                flash('this id is alredy registered')
                return render_template('sregister.html')
            elif count1==(1,):
                flash('hotel_email already in use')
                return render_template('sregister.html')
            
            data={'id1':id1,'username':name,'department':department,'email':email,'phone':phone,'address':address,'passout_year':passout_year,'password':password}
            subject='email Confirmation'
            body=f"Thanks for signing up\n\nfollow this link for further steps-{url_for('uconfirm',token=token(data,salt),_external=True)}"
            sendmail(to=email,subject=subject,body=body)
            flash('Confirmation link sent to mail')
            return redirect(url_for('uregistration'))
        
    return render_template('sregister.html',data=data)
@app.route('/uconfirm/<token>')
def uconfirm(token):
    try:
        serializer=URLSafeTimedSerializer(secret_key)
        data=serializer.loads(token,salt=salt,max_age=180)
    except Exception as e:
      
        return 'Link Expired register again'
    else:
        #cursor = mydb.cursor(buffered=True)
        id1=data['id1']
        count = execute_query('select count(*) from students where Student_ID=%s',[id1])[0]
        #count=cursor.fetchone()[0]
        if count==(1,):
            #cursor.close()
            flash('You are already registerterd!')
            return redirect(url_for('ulogin'))
        else:
            #print("Data:", data)  # Print data to check if it's correct
            passout_year = int(data['passout_year'].split('-')[0]) 
            execute_query('INSERT INTO students (Student_ID, Name, Email, Phone, Department, Address, Passout_Year, password) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', [data['id1'], data['username'], data['email'], data['phone'], data['department'], data['address'], passout_year, data['password']], commit=True)

            # mydb.commit()
            # cursor.close()
            flash('Details registered!')
            return redirect(url_for('ulogin'))

@app.route('/uforget',methods=['GET','POST'])
def uforgot():
    if request.method=='POST':
        id1=request.form['id1']
        #cursor = mydb.cursor(buffered=True)
        count=execute_query('select count(*) from students where Student_ID=%s',[id1])[0]
        # count=cursor.fetchone()[0]
        # cursor.close()
        if count==(1,):
            #cursor = mydb.cursor(buffered=True)

            hotel_email=execute_query('SELECT Email from students where Student_ID=%s',[id1])[0]
            #hotel_email=cursor.fetchone()[0]
            # cursor.close()
            subject='Forget Password'
            confirm_link=url_for('ureset',token=token(id1,salt=salt2),_external=True)
            body=f"Use this link to reset your password-\n\n{confirm_link}"
            sendmail(to=hotel_email,body=body,subject=subject)
            flash('Reset link sent check your hotel_email')
            return redirect(url_for('ulogin'))
        else:
            flash('Invalid email ')
            return render_template('forgot.html')
    return render_template('forgot.html')


@app.route('/reset/<token>',methods=['GET','POST'])
def ureset(token):
    try:
        serializer=URLSafeTimedSerializer(secret_key)
        id1=serializer.loads(token,salt=salt2,max_age=180)
    except:
        abort(404,'Link Expired')
    else:
        if request.method=='POST':
            newpassword=request.form['npassword']
            confirmpassword=request.form['cpassword']
            if newpassword==confirmpassword:
                # cursor = mydb.cursor(buffered=True)
                execute_query('update students set password=%s where Student_ID=%s',[newpassword,id1],commit=True)
                # mydb.commit()
                flash('Reset Successful')
                return redirect(url_for('ulogin'))
            else:
                flash('Passwords mismatched')
                return render_template('newpassword.html')
        return render_template('newpassword.html')
@app.route('/ulogout')
def ulogout():
    if session.get('user'):
        session.pop('user')
        flash('Successfully loged out')
        return redirect(url_for('ulogin'))
    else:
        return redirect(url_for('ulogin'))
@app.route('/users_dashboard')
def users_dashboard():
    if session.get('user'):
        return render_template('users_dashboard.html')
    return redirect(url_for('ulogin'))
@app.route('/viewcompany')
def viewcompany():
    if session.get('user'):
        #print("========================",session['user'])
        applied_companies = execute_query('SELECT Company_ID, Application_Result FROM apply WHERE Student_ID = %s', [session['user']])
        applied_company_ids = {comp[0]: comp[1] for comp in applied_companies}
        
        data = execute_query('SELECT * FROM company')
        
        return render_template('viewcompany.html',d=data, applied_company_ids=applied_company_ids)
    return redirect(url_for('ulogin'))
@app.route('/apply_company/<cid>')
def apply_company(cid):
    if session.get('user'):
        student_id = session['user']
        check_query = 'SELECT COUNT(*) FROM apply WHERE Student_ID = %s AND Company_ID = %s'
        count = execute_query(check_query, [student_id, cid])[0]
        
        if count == (1,):  # Student has already applied
            flash('You have already applied for this job. View your application status.')
        else:
            insert_query = 'INSERT INTO apply (Student_ID, Company_ID) VALUES (%s, %s)'
            execute_query(insert_query, [student_id, cid], commit=True)
            flash('Applied successfully')
        
        return redirect(url_for('viewcompany'))
        
    return redirect(url_for('ulogin'))
#=====================================cordinater registratio and login

@app.route('/clogin',methods=['GET','POST'])
def clogin():
    if session.get('coordinator'):
        return redirect(url_for('coordinator_dashboard'))
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        # cursor = mydb.cursor(buffered=True)
        count=execute_query('SELECT count(*) as count from coordinator where Coordinator_ID=%s and password=%s',[username,password])[0]
        # count=cursor.fetchone()[0]
        if count==(1,):
            session['coordinator']=username
            if not session.get(username):
                session[username]={}
            return redirect(url_for("coordinator_dashboard"))
        else:
            flash('Invalid username or password')
            return render_template('clogin.html')
    return render_template('clogin.html')

@app.route('/cregistration',methods=['GET','POST'])
def cregistration():
    data = execute_query('select * from departments')
    if request.method=='POST':
        code = request.form['code']
        id1=request.form['coordinator_id']
        
        department= request.form['department']
        name=request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        code1="coordinator@12"
        if code == code1:
            #cursor = mydb.cursor(buffered=True)
            count = execute_query('select count(*) from coordinator where Coordinator_ID=%s',[id1])[0]
            #count=cursor.fetchone()[0]
            count1 = execute_query('select count(*) from coordinator where Email=%s',[email])[0]
            #count1=cursor.fetchone()[0]
            #cursor.close()
            if count==(1,):
                flash('this id is alredy registered')
                return render_template('cregister.html')
            elif count1==(1,):
                flash('hotel_email already in use')
                return render_template('cregister.html')
            
            data1={'id1':id1,'username':name,'department':department,'email':email,'phone':phone,'password':password}
            subject='email Confirmation'
            body=f"Thanks for signing up\n\nfollow this link for further steps-{url_for('cconfirm',token=token1(data1,salt),_external=True)}"
            sendmail(to=email,subject=subject,body=body)
            flash('Confirmation link sent to mail')
            return redirect(url_for('cregistration'))
        
    return render_template('cregister.html',data=data)
@app.route('/cconfirm/<token>')
def cconfirm(token):
    try:
        serializer=URLSafeTimedSerializer(secret_key)
        data=serializer.loads(token,salt=salt,max_age=180)
    except Exception as e:
      
        return 'Link Expired register again'
    else:
        #cursor = mydb.cursor(buffered=True)
        id1=data['id1']
        count = execute_query('select count(*) from coordinator where Coordinator_ID=%s',[id1])[0]
        #count=cursor.fetchone()[0]
        if count==(1,):
            #cursor.close()
            flash('You are already registerterd!')
            return redirect(url_for('clogin'))
        else:
            #print("Data:", data)  # Print data to check if it's correct
            
            execute_query('INSERT INTO coordinator (Coordinator_ID,Department_ID, Name, Email, Phone,password) VALUES (%s, %s, %s, %s, %s, %s)', [data['id1'],data['department'], data['username'], data['email'], data['phone'], data['password']], commit=True)

            # mydb.commit()
            # cursor.close()
            flash('Details registered!')
            return redirect(url_for('clogin'))

@app.route('/cforget',methods=['GET','POST'])
def cforgot():
    if request.method=='POST':
        print('==================================')
        id1=request.form['id1']
        #cursor = mydb.cursor(buffered=True)
        count=execute_query('select count(*) from coordinator where Coordinator_ID=%s',[id1])[0]
        # count=cursor.fetchone()[0]
        # cursor.close()
        print('================================',count)
        if count==(1,):
            #cursor = mydb.cursor(buffered=True)

            hotel_email=execute_query('SELECT Email from coordinator where Coordinator_ID=%s',[id1])[0]
            #hotel_email=cursor.fetchone()[0]
            # cursor.close()
            subject='Forget Password'
            confirm_link=url_for('creset',token=token1(id1,salt=salt2),_external=True)
            body=f"Use this link to reset your password-\n\n{confirm_link}"
            sendmail(to=hotel_email,body=body,subject=subject)
            flash('Reset link sent check your email')
            return redirect(url_for('clogin'))
        else:
            flash('Invalid email ')
            return render_template('forgot.html')
    return render_template('forgot.html')


@app.route('/creset/<token>',methods=['GET','POST'])
def creset(token):
    try:
        serializer=URLSafeTimedSerializer(secret_key)
        id1=serializer.loads(token,salt=salt2,max_age=180)
    except:
        abort(404,'Link Expired')
    else:
        if request.method=='POST':
            newpassword=request.form['npassword']
            confirmpassword=request.form['cpassword']
            if newpassword==confirmpassword:
                # cursor = mydb.cursor(buffered=True)
                execute_query('update coordinator set password=%s where Coordinator_ID=%s',[newpassword,id1],commit=True)
                # mydb.commit()
                flash('Reset Successful')
                return redirect(url_for('clogin'))
            else:
                flash('Passwords mismatched')
                return render_template('newpassword.html')
        return render_template('newpassword.html')
@app.route('/clogout')
def clogout():
    if session.get('coordinator'):
        session.pop('coordinator')
        flash('Successfully loged out')
        return redirect(url_for('clogin'))
    else:
        return redirect(url_for('clogin'))
@app.route('/coordinator_dashboard')
def coordinator_dashboard():
    if session.get('coordinator'):
        return render_template('coordinator_dashboard.html')
    return redirect(url_for('clogin'))
@app.route('/view_departments_students',methods=['GET','POST'])
def view_departments_students():
    if session.get('coordinator'):
        #print(session['coordinator'])
        c = execute_query('SELECT Department_ID FROM coordinator WHERE Coordinator_ID = %s', [session['coordinator']])[0][0]
        print("========================================",c)
        name = execute_query('select Department_Name from departments where Department_ID=%s',[c])[0][0]
        print("*"*10,name)
        data=execute_query('select * from students where Department=%s',[c])
        return render_template('view_department_students.html',d=data)
        
    return redirect(url_for('clogin'))
'''@app.route('/view_placement_results')
def view_placement_results():
    if session.get('coordinator'):
        c = execute_query('SELECT Department_ID FROM coordinator WHERE Coordinator_ID = %s', [session['coordinator']])[0][0]
        #print("========================================",c)
        name = execute_query('select Department_Name from departments where Department_ID=%s',[c])[0][0]
        sid = execute_query('select Student_ID from students where Department=%s',[name])
        status= execute_query('select * from apply where Student_ID=%s',[sid])
        data=execute_query('select * from students where Department=%s',[name])
        return render_template('view_placement_result.html',d=data,s=status)
    return redirect(url_for('clogin'))
@app.route('/view_placement_results')
def view_placement_results():
    if session.get('coordinator'):
        c = execute_query('SELECT Department_ID FROM coordinator WHERE Coordinator_ID = %s', [session['coordinator']])[0][0]
        name = execute_query('SELECT Department_Name FROM departments WHERE Department_ID = %s', [c])[0][0]
        student_ids = execute_query('SELECT Student_ID FROM students WHERE Department = %s', [name])[0][0]
        print('=================================',student_ids)
        #student_ids = [sid[0] for sid in student_ids]  # Extract Student_ID values from the list of tuples

        status = execute_query('SELECT Application_Result FROM apply WHERE Student_ID = %s', [student_ids])
        print("==========================================",status)
        data = execute_query('SELECT * FROM students WHERE Department=%s', [name])
        print("==================================================",data)
        # Zip the student data and application statuses manually
        zipped_data = list(zip_longest(data, status, fillvalue=None))
        return render_template('view_placement_result.html', zipped_data=zipped_data)
    
    return redirect(url_for('clogin'))'''
from flask import render_template, session, redirect, url_for
from itertools import zip_longest

@app.route('/view_placement_results')
def view_placement_results():
    if session.get('coordinator'):
        coordinator_id = session['coordinator']
        department_id = execute_query('SELECT Department_ID FROM coordinator WHERE Coordinator_ID = %s', [coordinator_id])[0][0]
        department_name = execute_query('SELECT Department_Name FROM departments WHERE Department_ID = %s', [department_id])[0][0]

        # Fetch placement data using SQL query
        placement_data = execute_query('''
            SELECT 
                students.Student_ID,
                students.Name AS Student_Name,
                students.Email,
                students.Department,
                company.Company_ID,
                company.Company_Name,
                company.Role AS Job_Role,
                company.Package,
                apply.Application_Result
            FROM 
                apply
            INNER JOIN 
                students ON apply.Student_ID = students.Student_ID
            INNER JOIN 
                company ON apply.Company_ID = company.Company_ID
            WHERE
                students.Department = %s
        ''', [department_id])
        print(placement_data)

        return render_template('view_placement_result.html', placement_data=placement_data)
    
    return redirect(url_for('clogin'))


#=================================================================================

@app.route('/administrator_login',methods=['GET','POST'])
def alogin():
  
    if request.method=='POST':
        email=request.form['email']
        code = request.form['code']
        
        if email == "gvaishnavi1661@gmail.com" and  code == "admin@123":
                session['admin']="admin@123"
                return redirect('admindashboard')
        else:
            flash("unauthorized access")
            return redirect(url_for('alogin'))
    
    return render_template('administrator_login.html')

@app.route('/alogout')
def alogout():
    if session.get('admin'):
        session.pop('admin')
        flash('successfully log out')
        return redirect(url_for('home'))
    else:
        return redirect(url_for('alogin'))
@app.route('/admindashboard')
def admindashboard():
    if session.get('admin'):
        return render_template('admindashboard.html')
    return redirect(url_for('alogin'))
@app.route('/adddepartment',methods=['GET','POST'])
def adddepartment():
    if session.get('admin'):
        if request.method=="POST":
            name=request.form['name']
            execute_query('insert into Departments (Department_Name) value (%s)',[name],commit=True)
            flash(f'{name} department added sucessfully')
            return redirect(url_for('adddepartment'))
        return render_template('add_department.html')
    return redirect(url_for('alogin'))
@app.route('/viewdepartments')
def viewdepartments():
    if session.get('admin'):
        data = execute_query('select * from departments')
        return render_template('viewdepartments.html',data=data)
    return redirect(url_for('alogin'))
@app.route('/deletedepartment/<did>',methods=['GET','POST'])
def deletedepartment(did):
    if session.get('admin'):
        execute_query('delete from Departments where Department_ID=%s',[did],commit=True)
        flash('department deleted sucessfully')
        return redirect(url_for('viewdepartments'))
    return redirect(url_for('alogin'))
@app.route('/updatedepartment/<did>',methods=['GET','POST'])
def updatedepartment(did):
    if session.get('admin'):
        if request.method=="POST":
            name=request.form['name']
            execute_query('UPDATE departments SET Department_Name = %s WHERE Department_ID = %s',[name,did],commit=True)
            flash(f'{name} department added sucessfully')
            return redirect(url_for('viewdepartments'))
    return redirect(url_for('alogin'))
@app.route('/addcompany',methods=['GET','POST'])
def addcompany():
    if session.get('admin'):
        if request.method=="POST":
            name=request.form['company_name']
            description=request.form['description']
            role = request.form['role']
            package=request.form['package']
            requirements=request.form['requirements']
            departments=request.form['departments']
            passout_year=request.form['passout_year']
            job_location=request.form['job_location']
            execute_query('INSERT INTO Company (Company_Name, Description, Role, Package, Requirements, Departments, Passout_Year, Job_Location) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', [name, description, role, package, requirements, departments, passout_year, job_location], commit=True)
            flash(f'{name} {role} added sucessfully')
            return redirect(url_for('addcompany'))
        return render_template('addcompany.html')
    return redirect(url_for('alogin'))
@app.route('/viewcomapny_admin',methods=['GET','POST'])
def viewcompany_a():
    if session.get('admin'):
        data=execute_query('select * from company')
        return render_template('viewcompanies_admin.html',d=data)
    return redirect(url_for('alogin'))
@app.route('/updatecompany/<cid>',methods=['GET','POST'])
def updatecompany(cid):
    if session.get('admin'):
        data=execute_query('select * from company where Company_ID=%s',[cid])
        if request.method=="POST":
            name=request.form['company_name']
            description=request.form['description']
            role = request.form['role']
            package=request.form['package']
            requirements=request.form['requirements']
            departments=request.form['departments']
            passout_year=request.form['passout_year']
            job_location=request.form['job_location']
            execute_query('''
                UPDATE company 
                SET Company_Name = %s, 
                    Description = %s, 
                    Role = %s, 
                    Package = %s, 
                    Requirements = %s, 
                    Departments = %s, 
                    Passout_Year = %s, 
                    Job_Location = %s 
                WHERE Company_ID = %s
            ''', [name, description, role, package, requirements, departments, passout_year, job_location, cid], commit=True)

            flash(f'{name}Company updated successfully!')
            return redirect(url_for('viewcompany_a'))
        return render_template('updatecompany.html',d=data)
    return redirect(url_for('alogin'))
@app.route('/deletecompany/<cid>',methods=['GET','POST'])
def deletecompany(cid):
    if session.get('admin'):
        execute_query('delete from comapny where Company_ID=%s',[cid])
        flash('company deleted sucessfilly')
        return redirect(url_for('viewcompany_a'))
    return redirect(url_for('alogin'))
@app.route('/viewappliedcompanies', methods=['GET', 'POST'])
def view_applied_companies():
    if session.get('admin'):
        query = """
                        SELECT 
                    students.Student_ID,
                    students.Name AS Student_Name,
                    students.Email,
                    students.Department,
                    company.Company_ID,
                    company.Company_Name,
                    company.Role AS Job_Role,
                    company.Package,
                    apply.Application_Result
                FROM 
                    apply
                INNER JOIN 
                    students ON apply.Student_ID = students.Student_ID
                INNER JOIN 
                    company ON apply.Company_ID = company.Company_ID;

        """
        applied_data = execute_query(query)
        return render_template('viewappliedcompanies.html', applied_data=applied_data)
    return redirect(url_for('alogin'))
@app.route('/update_application/<sid>',methods=['GET','POST'])
def update_application(sid):
    if session.get('admin'):
        if request.method=="POST":
            a_r=request.form['application_result']
            execute_query('UPDATE apply SET Application_Result =%s WHERE Student_ID =%s',[a_r,sid],commit=True)
            flash(f'{a_r} {sid} updated sucessfully') 
            return redirect(url_for('view_applied_companies'))
    return redirect(url_for('alogin'))
app.run(use_reloader=True,debug=True)

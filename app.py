from flask import Flask, render_template, request, redirect, url_for, session, flash
from schema.init_script import reinitializeDatabase

from middleware.keyGen import generateKey
from middleware.tokenGenerator import generateToken
from middleware.tokenValidator import validateToken
import sqlite3

from datetime import datetime

app = Flask(__name__)
app.secret_key = 'OkvzD0IvqdPOa47J0q3z5VaGy2cCDoP6V5GEfO0kGeq3vFfk1cb7vs8QMJiwF0nGIcXWCKoqD6wE6h1mUQZdQu7hR3FLjDwyRCCOY6bfuLBpr+WgQIDAQABAoGAENt4zTvrXc7Sig4N3tUsJ'

app.config['UPLOAD_FOLDER'] = 'static'


# /auth
@app.route('/auth/login', methods=['GET', 'POST'])
def loginScreen():
    if request.method == 'POST':
        # print(request.form.get('userEmail'))
        # print(request.form.get('userPassword'))
        userEmail = request.form.get('userEmail')
        userPassword = request.form.get('userPassword')

        if len(str(userEmail)) == 0 or len(str(userPassword)) == 0:
            flash('Please fill all the fields', 'danger')
            return redirect(url_for('loginScreen'))
        
        try:
            db_connection = sqlite3.connect('./schema/app_data.db')
            db_cursor = db_connection.cursor()
            db_cursor.execute(f"SELECT * FROM userData WHERE userEmail = ? AND userPassword = ? AND (userRoleId = 1 OR userRoleId = 2)", (userEmail, userPassword))
            userData = db_cursor.fetchone()
            db_connection.close()

            if userData is None:
                flash('Invalid credentials', 'danger')
                return redirect(url_for('loginScreen'))
            else:
                secretToken = generateToken({
                    "userId": userData[0],
                    "userName": userData[1],
                    "userEmail": userData[2],
                    "userRoleId": userData[4]
                })

                if secretToken == -1:
                    flash('Something went wrong', 'danger')
                    return redirect(url_for('loginScreen'))

                session['secretToken'] = secretToken
                session['userId'] = userData[0]
                session['userName'] = userData[1]
                session['userEmail'] = userData[2]
                session['userRoleId'] = userData[4]

                # TODO: Redirect to creator dashboard
                if userData[4] == 1:
                    return redirect(url_for('userDashboardScreen'))
                elif userData[4] == 2:
                    return redirect(url_for('creatorDashboardScreen'))
                else:
                    flash('Invalid user role', 'danger')
                    return redirect(url_for('loginScreen'))

        except Exception as e:
            f = open("logs/errorLogs.txt", "a")
            f.write(f"[ERROR] {datetime.now()}: {e}\n")
            f.close()
            flash('Something went wrong', 'danger')
            return redirect(url_for('loginScreen'))
        

    elif request.method == 'GET':
        return render_template('auth/login.html')

    
@app.route('/auth/adminLogin', methods=['GET', 'POST'])
def adminLoginScreen():
    if request.method == 'POST':
        adminEmail = request.form.get('adminEmail')
        adminPassword = request.form.get('adminPassword')

        if len(adminEmail) == 0 or len(adminPassword) == 0:
            flash('Please fill all the fields', 'danger')
            return redirect(url_for('adminLoginScreen'))
        
        try:
            db_connection = sqlite3.connect('./schema/app_data.db')
            db_cursor = db_connection.cursor()
            db_cursor.execute(f"SELECT * FROM userData WHERE userEmail = ? AND userPassword = ? AND userRoleId = '0'", (adminEmail, adminPassword))
            adminData = db_cursor.fetchone()
            db_connection.close()

            if adminData is None:
                flash('Invalid credentials', 'danger')
                return redirect(url_for('adminLoginScreen'))
            else:
                secretToken = generateToken({
                    "userId": adminData[0],
                    "userName": adminData[1],
                    "userEmail": adminData[2],
                    "userRoleId": adminData[4]
                })

                if secretToken == -1:
                    flash('Something went wrong', 'danger')
                    return redirect(url_for('adminLoginScreen'))

                session['secretToken'] = secretToken
                session['userId'] = adminData[0]
                session['userName'] = adminData[1]
                session['userEmail'] = adminData[2]
                session['userRoleId'] = adminData[4]

                return redirect(url_for('adminDashboard'))

        except Exception as e:
            f = open("logs/errorLogs.txt", "a")
            f.write(f"[ERROR] {datetime.now()}: {e}\n")
            f.close()
            flash('Something went wrong', 'danger')
            return redirect(url_for('adminLoginScreen'))

    elif request.method == 'GET':
        return render_template('auth/admin_login.html')
    

@app.route('/auth/register', methods=['GET', 'POST'])
def registerScreen():
    if request.method == 'POST':

        userEmail = request.form.get('userEmail')
        userPassword = request.form.get('userPassword')
        userName = request.form.get('userName')
        userDob = request.form.get('userDob')
        userGender = request.form.get('userGender')

        if len(str(userEmail)) == 0 or len(str(userPassword)) == 0 or len(str(userName)) == 0 or len(str(userDob)) == 0 or len(str(userGender)) == 0:
            flash('Please fill all the fields', 'danger')
            return redirect(url_for('registerScreen'))
        
        # Check DOB format (YYYY-MM-DD)
        if len(userDob.split('-')) != 3 and len(userDob.split('-')[0]) != 4 and len(userDob.split('-')[1]) != 2 and len(userDob.split('-')[2]) != 2:
            flash('Invalid DOB format', 'danger')
            return redirect(url_for('registerScreen'))
        
        try:
            db_connection = sqlite3.connect('./schema/app_data.db')
            db_cursor = db_connection.cursor()

            # Check if user already exists
            db_cursor.execute(f"SELECT * FROM userData WHERE userEmail = ?", (userEmail,))
            userData = db_cursor.fetchone()

            if userData is not None:
                flash('User already exists', 'danger')
                return redirect(url_for('registerScreen'))
            
            # Insert user data
            db_cursor.execute(f"INSERT INTO userData (userName, userEmail, userPassword, userDob, userGender, userRoleId, accountStatus) VALUES (?, ?, ?, ?, ?, ?, ?)", (userName, userEmail, userPassword, userDob, userGender, 1, '1'))

            affectedRows = db_cursor.rowcount
            if affectedRows == 0:
                flash('Something went wrong', 'danger')
                return redirect(url_for('registerScreen'))

            db_connection.commit()
            db_connection.close()

            flash('User created successfully', 'success')
            return redirect(url_for('loginScreen'))
        
        except Exception as e:
            f = open("logs/errorLogs.txt", "a")
            f.write(f"[ERROR] {datetime.now()}: {e}\n")
            f.close()
            flash('Something went wrong', 'danger')
            return redirect(url_for('registerScreen'))

    elif request.method == 'GET':
        return render_template('auth/register.html')
    
@app.route('/auth/logout', methods=['GET'])
def logoutScreen():
    try:
        session.clear()
        return redirect(url_for('loginScreen'))
    except Exception as e:
        f = open("logs/errorLogs.txt", "a")
        f.write(f"[ERROR] {datetime.now()}: {e}\n")
        f.close()
        flash('Something went wrong', 'danger')
        return redirect(url_for('loginScreen'))


# /admin
@app.route('/admin/dashboard', methods=['GET'])
def adminDashboard():
    try:
        secretToken = session['secretToken']
        userId = session['userId']
        userName = session['userName']
        userEmail = session['userEmail']
        userRoleId = session['userRoleId']

        if userRoleId != 0:
            flash('Unauthorized Access', 'danger')
            return redirect(url_for('loginScreen'))
        
        if len(str(secretToken)) == 0 or len(str(userId)) == 0 or len(str(userName)) == 0 or len(str(userEmail)) == 0 or len(str(userRoleId)) == 0:
            flash('Session Expired', 'danger')
            return redirect(url_for('adminLoginScreen'))
        
        decryptedToken = validateToken(secretToken.split(',')[0], secretToken.split(',')[1], secretToken.split(',')[2])

        if decryptedToken == -2:
            flash('Session Expired', 'danger')
            return redirect(url_for('adminLoginScreen'))
        elif decryptedToken == -1:
            flash('Session Expired', 'danger')
            return redirect(url_for('adminLoginScreen'))
        

    except Exception as e:
        f = open("logs/errorLogs.txt", "a")
        f.write(f"[ERROR] {datetime.now()}: {e}\n")
        f.close()
        flash('Something Went Wrong.\nPlease try again later.', 'danger')
        return redirect(url_for('adminLoginScreen'))
    
    return render_template('admin/admin_dashboard.html')

# /user
@app.route('/user/dashboard', methods=['GET'])
def userDashboardScreen():
    try:
        secretToken = session['secretToken']
        userId = session['userId']
        userName = session['userName']
        userEmail = session['userEmail']
        userRoleId = session['userRoleId']

        # print(session, "Here")

        if userRoleId != 1:
            flash('Unauthorized Access', 'danger')
            return redirect(url_for('loginScreen'))
        
        if len(str(secretToken)) == 0 or len(str(userId)) == 0 or len(str(userName)) == 0 or len(str(userEmail)) == 0 or len(str(userRoleId)) == 0:
            flash('Session Expired', 'danger')
            return redirect(url_for('loginScreen'))
        
        decryptedToken = validateToken(secretToken.split(',')[0], secretToken.split(',')[1], secretToken.split(',')[2])

        if decryptedToken == -2:
            flash('Session Expired', 'danger')
            return redirect(url_for('loginScreen'))
        elif decryptedToken == -1:
            flash('Session Expired', 'danger')
            return redirect(url_for('loginScreen'))
        

    except Exception as e:
        f = open("logs/errorLogs.txt", "a")
        f.write(f"[ERROR] {datetime.now()}: {e}\n")
        f.close()
        flash('Something Went Wrong.\nPlease try again later.', 'danger')
        return redirect(url_for('loginScreen'))
    
    return render_template('user/user_dashboard.html')

@app.route('/user/registerAsCreator', methods=['POST'])
def registerAsCreator():
    try:
        secretToken = session['secretToken']
        userId = session['userId']
        userName = session['userName']
        userEmail = session['userEmail']
        userRoleId = session['userRoleId']

        if userRoleId != 1 and userRoleId != 2:
            flash('Unauthorized Access', 'danger')
            return redirect(url_for('loginScreen'))
        
        if len(str(secretToken)) == 0 or len(str(userId)) == 0 or len(str(userName)) == 0 or len(str(userEmail)) == 0 or len(str(userRoleId)) == 0:
            flash('Session Expired', 'danger')
            return redirect(url_for('loginScreen'))
        
        decryptedToken = validateToken(secretToken.split(',')[0], secretToken.split(',')[1], secretToken.split(',')[2])

        if decryptedToken == -2:
            flash('Session Expired', 'danger')
            return redirect(url_for('loginScreen'))
        elif decryptedToken == -1:
            flash('Session Expired', 'danger')
            return redirect(url_for('loginScreen'))
        
        db_connection = sqlite3.connect('./schema/app_data.db')
        db_cursor = db_connection.cursor()

        # Check if user is currently a user
        db_cursor.execute(f"SELECT * FROM userData WHERE userId = ? AND userRoleId = 1", (userId,))
        userData = db_cursor.fetchone()

        if userData is None:
            flash('Unauthorized Access', 'danger')
            return redirect(url_for('userDashboardScreen'))

        # Check if user already exists as creator
        db_cursor.execute(f"SELECT * FROM userData WHERE userId = ? AND userRoleId = 2", (userId,))
        userData = db_cursor.fetchone()

        if userData is not None:
            flash('User already exists as creator', 'danger')
            return redirect(url_for('userDashboardScreen'))
        

        db_cursor.execute(f"UPDATE userData SET userRoleId = 2 WHERE userId = ?", (userId,))

        affectedRows = db_cursor.rowcount
        if affectedRows == 0:
            flash('Something went wrong', 'danger')
            return redirect(url_for('userDashboardScreen'))

        db_connection.commit()
        db_connection.close()

        session['userRoleId'] = 2

        return {
            "message": "Registered as creator successfully"
        }

    except Exception as e:
        f = open("logs/errorLogs.txt", "a")
        f.write(f"[ERROR] {datetime.now()}: {e}\n")
        f.close()
        flash('Something Went Wrong.\nPlease try again later.', 'danger')
        return redirect(url_for('userDashboardScreen'))
    

@app.route('/creator/dashboard', methods=['GET'])
def creatorDashboardScreen():
    try:
        secretToken = session['secretToken']
        userId = session['userId']
        userName = session['userName']
        userEmail = session['userEmail']
        userRoleId = session['userRoleId']

        # print(session)

        if userRoleId != 2:
            flash('Unauthorized Access', 'danger')
            return redirect(url_for('loginScreen'))
        
        if len(str(secretToken)) == 0 or len(str(userId)) == 0 or len(str(userName)) == 0 or len(str(userEmail)) == 0 or len(str(userRoleId)) == 0:
            flash('Session Expired', 'danger')
            return redirect(url_for('loginScreen'))
        
        decryptedToken = validateToken(secretToken.split(',')[0], secretToken.split(',')[1], secretToken.split(',')[2])

        if decryptedToken == -2:
            flash('Session Expired', 'danger')
            return redirect(url_for('loginScreen'))
        elif decryptedToken == -1:
            flash('Session Expired', 'danger')
            return redirect(url_for('loginScreen'))
        

    except Exception as e:
        f = open("logs/errorLogs.txt", "a")
        f.write(f"[ERROR] {datetime.now()}: {e}\n")
        f.close()
        flash('Something Went Wrong.\nPlease try again later.', 'danger')
        return redirect(url_for('loginScreen'))
    
    return render_template('creator/creator_dashboard.html')


if __name__ == '__main__':
    reinitializeDatabase()
    generateKey()
    app.run(debug=True)

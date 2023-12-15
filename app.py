from flask import Flask, render_template, request, redirect, url_for, session, flash
from schema.init_script import reinitializeDatabase, initEnvironment

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
        
        db_connection = sqlite3.connect('./schema/app_data.db')
        db_cursor = db_connection.cursor()

        # Get all songs
        db_cursor.execute(f"SELECT s.songId, s.songName, g.genreName FROM songData AS s JOIN genreData AS g ON g.genreId = s.songGenreId JOIN languageData AS l ON l.languageId = s.songLanguageId WHERE s.createdBy = ?", (userId,))
        songList = db_cursor.fetchall()

        db_connection.close()
        

    except Exception as e:
        f = open("logs/errorLogs.txt", "a")
        f.write(f"[ERROR] {datetime.now()}: {e}\n")
        f.close()
        flash('Something Went Wrong.\nPlease try again later.', 'danger')
        return redirect(url_for('loginScreen'))
    
    return render_template('creator/creator_dashboard.html', songList=songList)

@app.route('/song/new', methods=['GET', 'POST'])
def addNewSong():
    if request.method == 'GET':
        try:
            secretToken = session['secretToken']
            userId = session['userId']
            userName = session['userName']
            userEmail = session['userEmail']
            userRoleId = session['userRoleId']

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
            

            db_connection = sqlite3.connect('./schema/app_data.db')
            db_cursor = db_connection.cursor()

            # Get all genres
            db_cursor.execute(f"SELECT * FROM genreData")
            genreList = db_cursor.fetchall()

            db_cursor.execute(f"SELECT * FROM languageData")
            languageList = db_cursor.fetchall()

            db_connection.close()

            if genreList is None:
                flash('No Genres found to add new songs! Add new Genres to continue', 'danger')
                return redirect(url_for('addNewGenre'))
            
            if userRoleId == 2:
                return render_template('creator/new_song.html', genreList=genreList, languageList=languageList)
            elif userRoleId == 0:
                return render_template('admin/new_song.html', genreList=genreList, languageList=languageList)
            
        except Exception as e:
            f = open("logs/errorLogs.txt", "a")
            f.write(f"[ERROR] {datetime.now()}: {e}\n")
            f.close()
            flash('Something Went Wrong.\nPlease try again later.', 'danger')
            return redirect(url_for('loginScreen'))
        

    elif request.method == 'POST':
        try:
            secretToken = session['secretToken']
            userId = session['userId']
            userName = session['userName']
            userEmail = session['userEmail']
            userRoleId = session['userRoleId']

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
            

            songName = request.form.get('songName')
            songDescription = request.form.get('songDescription')
            songGenre = request.form.get('songGenre')
            songLanguage = request.form.get('songLanguage')
            songLyrics = request.form.get('songLyrics')
            songReleaseDate = request.form.get('songReleaseDate')
            songAudio = request.files['songAudio']
            songCover = request.files['songCover']

            print({
                "songName": songName,
                "songDescription": songDescription,
                "songGenre": songGenre,
                "songLanguage": songLanguage,
                "songLyrics": songLyrics,
                "songReleaseDate": songReleaseDate,
                "songAudio": songAudio.filename,
                "songCover": songCover.filename
            })

            print(songAudio.filename.split('.')[1])
            print(songCover.filename.split('.')[1])

            
            # INSERT DATA AND IF SUCCESSFUL, UPLOAD FILES
            if len(str(songName)) == 0 or len(str(songDescription)) == 0 or len(str(songGenre)) == 0 or len(str(songLanguage)) == 0 or len(str(songLyrics)) == 0 or len(str(songReleaseDate)) == 0:
                flash('Please fill all the fields', 'danger')
                return redirect(url_for('addNewSong'))
            
            db_connection = sqlite3.connect('./schema/app_data.db')
            db_cursor = db_connection.cursor()

            # Check if song already exists
            db_cursor.execute(f"SELECT * FROM songData WHERE songName = ?", (songName,))
            songData = db_cursor.fetchone()

            if songData is not None:
                flash('Song already exists', 'danger')
                return redirect(url_for('addNewSong'))
            
            # TODO: SongDuration
            # Insert song data
            db_cursor.execute(f"INSERT INTO songData (songName, songDescription, songLyrics, songReleaseDate, songGenreId, songLanguageId, isActive, createdBy) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (songName, songDescription, songLyrics, songReleaseDate, songGenre, songLanguage, "1", userId))

            affectedRows = db_cursor.rowcount
            songId = db_cursor.lastrowid

            if affectedRows == 0:
                flash('Something went wrong', 'danger')
                return redirect(url_for('addNewSong'))
            
            # Upload song audio
            songAudio.save(f"static/music/song/{songId}.{songAudio.filename.split('.')[-1]}")

            # Upload song cover
            songCover.save(f"static/music/poster/{songId}.{songCover.filename.split('.')[-1]}")

            db_connection.commit()
            db_connection.close()

            return redirect(url_for('creatorDashboardScreen'))
        
        except Exception as e:
            f = open("logs/errorLogs.txt", "a")
            f.write(f"[ERROR] {datetime.now()}: {e}\n")
            f.close()
            flash('Something Went Wrong.\nPlease try again later.', 'danger')
            return redirect(url_for('loginScreen'))


# /genre
@app.route('/genre/new', methods=['GET', 'POST'])
def addNewGenre():
    if request.method == "POST":
        try:
            secretToken = session['secretToken']
            userId = session['userId']
            userName = session['userName']
            userEmail = session['userEmail']
            userRoleId = session['userRoleId']

            if userRoleId != 2 and userRoleId != 0:
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
            
            genreName = request.form.get('genreName')
            genreDescription = request.form.get('genreDescription')

            if len(str(genreName)) == 0 or len(str(genreDescription)) == 0:
                flash('Please fill all the fields', 'danger')
                return redirect(url_for('creatorDashboardScreen'))
            
            db_connection = sqlite3.connect('./schema/app_data.db')
            db_cursor = db_connection.cursor()

            # Check if genre already exists
            db_cursor.execute(f"SELECT * FROM genreData WHERE genreName = ?", (genreName,))
            genreData = db_cursor.fetchone()

            if genreData is not None:
                flash('Genre already exists', 'danger')
                return redirect(url_for('creatorDashboardScreen'))

            db_cursor.execute(f"INSERT INTO genreData (genreName, genreDescription, isActive, createdBy) VALUES (?, ?, ?, ?)", (genreName, genreDescription, "1", userId))
            affectedRows = db_cursor.rowcount
            if affectedRows == 0:
                flash('Something went wrong', 'danger')
                return redirect(url_for('creatorDashboardScreen'))

            db_connection.commit()
            db_connection.close()

            if userRoleId == 2:
                return redirect(url_for('creatorDashboardScreen'))
            elif userRoleId == 0:
                return redirect(url_for('adminDashboard'))

        except Exception as e:
            f = open("logs/errorLogs.txt", "a")
            f.write(f"[ERROR] {datetime.now()}: {e}\n")
            f.close()
            flash('Something Went Wrong.\nPlease try again later.', 'danger')
            return redirect(url_for('creatorDashboardScreen'))
    elif request.method == "GET":
        try: 
            secretToken = session['secretToken']
            userId = session['userId']
            userName = session['userName']
            userEmail = session['userEmail']
            userRoleId = session['userRoleId']

            if userRoleId != 2 and userRoleId != 0:
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
            
            if userRoleId == 2:
                return render_template('creator/new_genre.html')
            elif userRoleId == 0:
                return render_template('admin/new_genre.html')

        except:
            f = open("logs/errorLogs.txt", "a")
            f.write(f"[ERROR] {datetime.now()}: {e}\n")
            f.close()
            flash('Something Went Wrong.\nPlease try again later.', 'danger')
            return redirect(url_for('creatorDashboardScreen'))


if __name__ == '__main__':
    # reinitializeDatabase()
    # initEnvironment()
    # generateKey()


    app.run(debug=True, port=5000)

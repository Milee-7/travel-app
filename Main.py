from flask import Flask, render_template, request, session, redirect, jsonify

#For database
from flask_mysqldb import MySQL

#For session
from flask_session import Session

#For unique tokens
import uuid

app =  Flask(__name__)

#Database Settings for mysql
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'db_travelapp'

mysql = MySQL(app) #initallizing mysql

#Session settings
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route('/')
def home():
    logged_in_user = None
    if session.get('email'):
        logged_in_user = session["email"]
    
    return render_template('index.html', result={'logged_in_user':logged_in_user})

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/doLogin', methods=['POST'])
def doLogin():
    email = request.form['email']
    password = request.form['psw']

    cursor = mysql.connection.cursor()
    resp = cursor.execute('''SELECT id, email, full_name, password FROM users WHERE email=%s and password=%s;''',(email,password))

    user = cursor.fetchone()
    cursor.close()
    if resp == 1:
        session["email"] = email
        session['userId'] = user[0]
        logged_in_user = session.get('email')
        return render_template('home.html', result={'logged_in_user':logged_in_user})
    else:
        return render_template('login.html', result="Invalid Credentials")


@app.route('/doRegister', methods=['POST'])
def doRegister():
    full_name = request.form['full_name']
    email = request.form['email']
    phone_number = request.form['phone_number']
    address = request.form['address']
    password = request.form['psw']

    cursor = mysql.connection.cursor()
    cursor.execute('''INSERT INTO users VALUES(NULL,%s,%s,%s,%s,%s)''',(full_name,address,email,phone_number,password))
    mysql.connection.commit()
    cursor.close()

    return render_template('login.html', result="Registered Successfully. Please login to continue.")

@app.route('/treks')
def allTreks():
    cursor = mysql.connection.cursor()
    cursor.execute('''SELECT td.id as 'SNO', td.title as 'Title', td.days as 'Days', td.difficulty as 'Difficulty', td.total_cost as 'Total Cost', td.upvotes as 'Upvotes', u.full_name as 'Full Name', u.id as 'User Id' FROM trek_destinations as td join users as u on td.users_id = u.id;''')
    treks = cursor.fetchall()
    cursor.close()

    logged_in_user = None
    if session.get('email'):
        logged_in_user = session['email']
    if session.get('userId'):
        userId = session.get('userId')
    return render_template('listing.html',result={"treks":treks,"logged_in_user":logged_in_user,"userId":userId})
 
@app.route('/trek/<int:trekId>')
def getTrekbyId(trekId):
    cursor = mysql.connection.cursor()
    cursor.execute('''SELECT td.id as 'SNO', td.title as 'Title', td.days as 'Days', td.difficulty as 'Difficulty', td.total_cost as 'Total Cost', td.upvotes as 'Upvotes', u.full_name as 'Full Name' FROM trek_destinations as td join users as u on td.users_id = u.id WHERE td.id = %s;''',(trekId,))
    trek = cursor.fetchone()
    cursor.close()

    cursor = mysql.connection.cursor()
    cursor.execute('''SELECT * FROM `iternaries` WHERE trek_destinations_id = %s;''',(trekId,))
    iternaries = cursor.fetchall()
    #print(iternaries)
    cursor.close()

    return render_template('trekdetail.html',result={"trek":trek, "iternaries":iternaries})

@app.route('/logout')
def logout():
    session["email"] = None
    session["userId"] = None
    return redirect("/") 

@app.route('/addTrek')
def addTrek():
    logged_in_user = None
    if session.get('email'):
        logged_in_user = session["email"]

    return render_template('addtrek.html', result={'logged_in_user':logged_in_user})

@app.route('/doAddTrek', methods=['POST'])
def doAddTrek():
    logged_in_user = None
    if session.get('email'):
        logged_in_user = session["email"]

    title = request.form['title']
    days = request.form['days']
    difficulty = request.form['difficulty']
    total_cost = request.form['total_cost']
    upvotes = 0

    cursor = mysql.connection.cursor()
    cursor.execute('''SELECT id from 'users' where 'email' = %s;''',(logged_in_user,))
    user = cursor.fetchone()
    cursor.close()

    userId = user[0]

    cursor = mysql.connection.cursor()
    cursor.execute('''INSERT INTO trek_destinations VALUES(NULL,%s,%s,%s,%s,%s,%s)''',(title,days,difficulty,total_cost,upvotes,userId))
    mysql.connection.commit()
    cursor.close()

    return redirect("/treks") 

@app.route('/editTrek/<int:trekId>')
def editTrek(trekId):
    logged_in_user = None
    if session.get('email'):
        logged_in_user = session["email"]
    
    cursor = mysql.connection.cursor()
    cursor.execute('''SELECT td.id as 'SNO', td.title as 'Title', td.days as 'Days', td.difficulty as 'Difficulty', td.total_cost as 'Total Cost', td.upvotes as 'Upvotes', u.full_name as 'Full Name' FROM trek_destinations as td join users as u on td.users_id = u.id WHERE td.id = %s;''',(trekId,))
    trek = cursor.fetchone()
    cursor.close()
    return render_template('editTrek.html',result={"trek":trek,'logged_in_user':logged_in_user}) 
    
@app.route('/doUpdateTrek', methods=['POST'])
def doUpdateTrek():
    logged_in_user = None
    if session.get('email'):
        logged_in_user = session["email"]

    trekId = request.form['trekId']
    title = request.form['title']
    days = request.form['days']
    difficulty = request.form['difficulty']
    total_cost = request.form['total_cost'] 

    cursor = mysql.connection.cursor()
    cursor.execute('''UPDATE trek_destinations SET 'title'=%s, 'days'= %s, 'difficulty'= %s, 'total_cost'= %s WHERE 'id' = %s;''',(title,days,difficulty,total_cost,trekId))
    mysql.connection.commit()
    cursor.close()

    return redirect("/treks") 

@app.route('/doDeleteTrek/<int:trekId>')
def doDelete(trekId):
    cursor = mysql.connection.cursor()
    cursor.execute('''DELETE FROM trek_destinations WHERE 'id' = %s;''',(trekId,))
    mysql.connection.commit()
    cursor.close()

    return redirect("/treks") 

@app.route('/addIternary')
def addIternary():
    logged_in_user = None
    if session.get('email'):
        logged_in_user = session["email"]
    
    cursor = mysql.connection.cursor()
    userId = None
    if session.get('userId'):
        userId = session.get('userId')
    cursor.execute('''SELECT id, title FROM `trek_destinations` where users_id=%s;''',(userId,))
    treks = cursor.fetchall()
    cursor.close()

    return render_template('additernary.html',result={"treks":treks,'logged_in_user':logged_in_user}) 

@app.route('/doAddIternary', methods=['POST'])
def doAddIternary():
    logged_in_user = None
    if session.get('email'):
        logged_in_user = session["email"]

    trek_destination_id = request.form['trek_destination_id']
    day = request.form['day']
    title = request.form['title']
    start_place = request.form['start_place']
    end_place = request.form['end_place']
    description = request.form['description']
    duration = request.form['duration']
    cost = request.form['cost']

    cursor = mysql.connection.cursor()
    cursor.execute('''INSERT INTO iternaries VALUES(NULL,%s,%s,%s,%s,%s,%s,%s,%s)''',(title,day,start_place,end_place,description,duration,cost,trek_destination_id))
    mysql.connection.commit()
    cursor.close()

    return redirect("/treks") 

@app.route('/iternary/<int:trekId>')
def getIternarybyTrekId(trekId):

    cursor = mysql.connection.cursor()
    cursor.execute('''SELECT * FROM `iternaries` WHERE trek_destinations_id = %s;''',(trekId,))
    iternaries = cursor.fetchall()
    cursor.close()

    return render_template('iternary.html',result={"trekId":trekId, "iternaries":iternaries})

#@app.route('/testAjax')
#def testAjax():
#    return render_template('login.html')

#def __getUserIdByEmail(email):
#    pass 

@app.route('/myTreks/<string:param>')
def getTreksbyUser(param):
    userId = None
    if session.get('email'):
        logged_in_user = session.get('email')
    if session.get('userId'):
        userId = session.get('userId')
    
    cursor = mysql.connection.cursor()
    if param == "user":
        cursor.execute('''SELECT * FROM trek_destinations WHERE users_id = %s;''',(userId,))
    else:
        cursor.execute('''SELECT * FROM trek_destinations; ''')

    treks = cursor.fetchall()
    cursor.close()

    return render_template('mytreks.html',result={"treks":treks,"userID":userId})

@app.route('/search/treks',)
def search():
    keyword = request.args.get("keyword")
    cursor = mysql.connection.cursor()
    searchString = "%" + keyword + "%"
    cursor.execute('''SELECT * FROM trek_destinations where title like %s;''',(searchString,))
    treks = cursor.fetchall()
    cursor.close()

    logged_in_user = None
    if session.get('email'):
        logged_in_user = session['email']
    if session.get('userId'):
        userId = session.get('userId')
    result={"treks":treks,"logged_in_user":logged_in_user}
    
    return render_template('mytreks.html',result={"treks":treks,"userID":userId})



"""
API Interfaces defined from here...
"""


@app.route('/api/doRegister', methods=['POST'])
def doRegisterAPI():
    
    full_name = request.json['full_name']
    email = request.json['email']
    phone_number = request.json['phone_number']
    address = request.json['address']
    password = request.json['psw']

    cursor = mysql.connection.cursor()
    cursor.execute('''INSERT INTO users VALUES(NULL,%s,%s,%s,%s,%s)''',(full_name,address,email,phone_number,password))
    mysql.connection.commit()
    cursor.close()

    #return render_template('login.html', result="Registered Successfully. Please login to continue.")
    
    return jsonify({"result":"Registered Successfully. Please login to continue."})

@app.route('/rest/treks')
def allTreksAPI():
    
    cursor = mysql.connection.cursor()
    cursor.execute('''SELECT td.id as 'SNO', td.title as 'Title', td.days as 'Days', td.difficulty as 'Difficulty', td.total_cost as 'Total Cost', td.upvotes as 'Upvotes', u.full_name as 'Full Name' FROM trek_destinations as td join users as u on td.users_id = u.id;''')
    treks = cursor.fetchall()
    cursor.close()

    logged_in_user = None
    if session.get('email'):
        logged_in_user = session['email']

    result={"treks":treks,"logged_in_user":logged_in_user}
    
    #return render_template('listing.html',result={"treks":treks,"logged_in_user":logged_in_user})
    
    return jsonify(result)

@app.route('/api/doLogin', methods=['POST'])
def doLoginAPI():
    email = request.json['email']
    password = request.json['psw']

    cursor = mysql.connection.cursor()
    resp = cursor.execute('''SELECT id, email, full_name, password FROM users WHERE email=%s and password=%s;''',(email,password))

    user = cursor.fetchone()
    cursor.close()

    token = ""

    if resp == 1:
        session["email"] = email
        session['userId'] = user[0]
        logged_in_user = session.get('email')

        token = str(uuid.uuid4())
        cursor = mysql.connection.cursor()
        resp = cursor.execute('''UPDATE users SET token = %s WHERE email = %s;''',(token,email))
        
        mysql.connection.commit()
        cursor.close()

        return jsonify({"message":"Successfull Login","loggedin":True, "token":token})
    else:
        return jsonify({"message":"Login Failed. Please check your username and password.", "loggedin":False})

@app.route('/rest/treks', methods=['POST'])
def doAddTrekAPI():
    logged_in_user = None
    if session.get('email'):
        logged_in_user = session["email"]

    title = request.json['title']
    days = request.json['days']
    difficulty = request.json['difficulty']
    total_cost = request.json['total_cost']
    token = request.json['token'] or None
    userId = __validate_token(token)
    if userId is 0:
        return jsonify({"message":"Please enter a valid token"})
    upvotes = 0

    cursor = mysql.connection.cursor()
    cursor.execute('''INSERT INTO trek_destinations VALUES(NULL,%s,%s,%s,%s,%s,%s)''',(title,days,difficulty,total_cost,upvotes,userId))
    mysql.connection.commit()
    cursor.close()

    return jsonify({"message":"Trek has been added successfully"}) 

def __validate_token(token):
    cursor = mysql.connection.cursor()
    cursor.execute('''SELECT id from users where token = %s;''',(token,))
    user = cursor.fetchone()
    cursor.close()
    userId = 0 
    if user is not None:
        userId = user[0] 
    return userId

@app.route('/rest/treks', methods=['PUT'])
def doUpdateTrekAPI():

    trekId = request.json['trekId']
    title = request.json['title']
    days = request.json['days']
    difficulty = request.json['difficulty']
    total_cost = request.json['total_cost'] 
    token = request.json['token'] or None
    userId = __validate_token(token)
    if userId is 0:
        return jsonify({"message":"Please enter a valid token"})

    cursor = mysql.connection.cursor()
    cursor.execute('''UPDATE trek_destinations SET title=%s, days= %s, difficulty= %s, total_cost= %s WHERE id = %s;''',(title,days,difficulty,total_cost,trekId))
    mysql.connection.commit()
    cursor.close()

    return jsonify({"message":"Trek has been updated successfully"}) 

@app.route('/rest/treks', methods=['DELETE'])
def doDeleteTrekAPI():

    trekId = request.json['trekId']
    token = request.json['token'] or None
    userId = __validate_token(token)
    if userId is 0:
        return jsonify({"message":"Please enter a valid token"})

    cursor = mysql.connection.cursor()
    resp = cursor.execute('''DELETE FROM trek_destinations WHERE 'id' = %s and 'users_id' = %s;''',(trekId,userId))
    if resp == 0:
        return jsonify({"message":"You cannot delete someone else's trek"}) 

    mysql.connection.commit()
    cursor.close()

    return jsonify({"message":"Trek has been deleted successfully"}) 

@app.route('/api/search/treks',)
#@app.route('/api/treks/search/<string:keyword>',)
def searchAPI():
    keyword = request.args.get("keyword")
    cursor = mysql.connection.cursor()
    searchString = "%" + keyword + "%"
    cursor.execute('''SELECT * FROM trek_destinations where title like %s;''',(searchString,))
    treks = cursor.fetchall()
    cursor.close()

    logged_in_user = None
    if session.get('email'):
        logged_in_user = session['email']

    result={"treks":treks,"logged_in_user":logged_in_user}
    return jsonify(result)


app.run(debug=True)

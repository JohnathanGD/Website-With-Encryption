from flask import Flask, render_template, request, session
from cryptography.fernet import Fernet
import sqlite3
from config import FERNET_KEY, APP_KEY

app = Flask(__name__)
app.secret_key = APP_KEY

f = Fernet(FERNET_KEY)

DATABASE = 'database/contest.db'

def get_Database():
    return sqlite3.connect(DATABASE)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_Database()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name, security_level, id, password
            FROM BakingContestUSERS
        """)
        users = cursor.fetchall()
        conn.close()

        # Check if the provided username matches any decrypted usernames
        for encrypted_name, security_level, user_id, stored_password in users:
            try:
                decrypted_name = f.decrypt(encrypted_name).decode('utf-8')
                decrypted_password = f.decrypt(stored_password).decode('utf-8')
            except Exception:
                continue

            if decrypted_name == username and decrypted_password == password:
                session['security_level'] = security_level
                session['name'] = decrypted_name
                session['id'] = user_id
                # Redirect based on security level
                if security_level == 3:
                    return render_template('home3.html', msg=f'Welcome, {decrypted_name}!')
                elif security_level == 2:
                    return render_template('home2.html', msg=f'Welcome, {decrypted_name}!')
                elif security_level == 1:
                    return render_template('home1.html', msg=f'Welcome, {decrypted_name}!')

        # Invalid login
        return render_template('login.html', error="Invalid username or password")
    return render_template('login.html')


@app.route('/home')
def home():

    security_level = session.get('security_level')
    name = session.get('name')

    if not security_level:
        return render_template('login.html', msg='Make sure you log in first')

    if security_level == 3:
        return render_template('home3.html', msg=f'Welcome, {name}!')
    elif security_level == 2:
        return render_template('home2.html', msg=f'Welcome, {name}!')
    elif security_level == 1:
        return render_template('home1.html', msg=f'Welcome, {name}!')
@app.route('/newUser', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        phone_number = request.form['phone_number']
        security_level = request.form['security_level']
        password = request.form['password']

        # Encrypt the username
        encrypted_name = f.encrypt(name.encode("utf-8"))
        encrypted_password = f.encrypt(password.encode("utf-8"))
        encrypted_phone = f.encrypt(phone_number.encode("utf-8"))

        # Validation
        errors = []
        if not name.strip():
            errors.append("You cannot enter an empty name.")
        if not age.isdigit() or not (0 < int(age) < 121):
            errors.append("Age must be a whole number between 1 and 120.")
        if not phone_number.strip():
            errors.append("You cannot enter an empty phone number.")
        if not security_level.isdigit() or not (1 <= int(security_level) <= 3):
            errors.append("Security level must be a number between 1 and 3.")
        if not password.strip():
            errors.append("You cannot enter an empty password.")

        if errors:
            return render_template('result.html', msg="<br>".join(errors))

        # Save to the database
        conn = get_Database()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO BakingContestUSERS (name, age, phone_number, security_level, password)
            VALUES (?, ?, ?, ?, ?)           
        """, (encrypted_name, age, encrypted_phone, security_level, encrypted_password))
        conn.commit()
        conn.close()
        return render_template('result.html', msg='Record successfully added!')
    return render_template('newUser.html')


@app.route('/newEntry', methods=['GET','POST'])
def add_entry():
    if request.method == 'POST':
        baking_item_name = request.form['baking_item_name']
        excellent_votes = request.form['excellent_votes']
        ok_votes = request.form['ok_votes']
        bad_votes = request.form['bad_votes']

        id = session.get("id")

        errors = []
        if not baking_item_name.strip():
            errors.append("You can not enter in an empty name!")
        if not excellent_votes.isdigit() or not (0 <= int(excellent_votes)):
            errors.append("Must be an integer greater or equal to 0!")
        if not ok_votes.isdigit() or not (0 <= int(ok_votes)):
            errors.append("Must be an integer greater or equal to 0!")
        if not bad_votes.isdigit() or not (0 <= int(bad_votes)):
            errors.append("Must be an integer greater or equal to 0!")
        
        if errors:
            return render_template('result.html', msg='<br>'.join(errors))
        
        conn = get_Database()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO BakingContestENTRIES(user_id, baking_item_name, excellent_votes, ok_votes, bad_votes)
                       VALUES(?,?,?,?,?)
        """, (id,baking_item_name, excellent_votes, ok_votes, bad_votes))

        conn.commit()
        conn.close()
        return render_template('result.html', msg='Record successfully added!')
    return render_template('newEntry.html')

@app.route('/userList')
def list_users():
    conn = get_Database()
    cursor = conn.cursor()
    cursor.execute("SELECT name, age, phone_number, security_level, password FROM BakingContestUSERS")
    users = cursor.fetchall()
    conn.close()

    decrypted_users = []
    for user in users:
        encrypted_name, age, phone_number, security_level, password = user
        try:
            # Decrypt the fields
            decrypted_name = f.decrypt(encrypted_name).decode('utf-8')
            decrypted_phone = f.decrypt(phone_number).decode('utf-8')
            decrypted_password = f.decrypt(password).decode('utf-8')
        except Exception:
            decrypted_name = "Decryption Error"
            decrypted_phone = "Decryption Error"
            decrypted_password = "Decryption Error"

        decrypted_users.append((decrypted_name, age, decrypted_phone, security_level, decrypted_password))

    return render_template('userList.html', users=decrypted_users)



@app.route('/contest_results')
def list_results():
    conn = get_Database()
    cursor = conn.cursor()
    cursor.execute("SELECT entry_id, user_id, baking_item_name, excellent_votes, ok_votes, bad_votes FROM BakingContestENTRIES")
    results = cursor.fetchall()
    conn.close()
    return render_template('contest_results.html', results=results)

@app.route('/my_contest_results')
def my_contest_results():
    id = session.get("id")

    if not id:
        return render_template("login.html", msg="Please login to view your results!")
    
    conn = get_Database()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT user_id, baking_item_name, excellent_votes, ok_votes, bad_votes 
        FROM BakingContestENTRIES
        WHERE user_id = ?
    """, (id,))
    results = cursor.fetchall()
    conn.close()
    return render_template("my_contest_results.html", results=results)

@app.route('/result')
def result():
    return('result.html')

if __name__ == '__main__':
    app.run(debug = True, host="0.0.0.0", port=60000)
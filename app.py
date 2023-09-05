# cSpell:disable
# Library imports
from flask import Flask, flash, redirect, render_template, request, session, jsonify, url_for, get_flashed_messages
from flask_session import Session
import query
import flask_email
from check_info import isValidEmail, isValidUsername, isValidPassword
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from functools import wraps
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os
from flask_apscheduler import APScheduler


# Add a global flag to track if any unverified users were deleted
deleted_users_flag = False


# Load the key for environment variables
load_dotenv()

app = Flask(__name__)
scheduler = APScheduler()
app.secret_key = os.getenv('FLASK_SECRET_KEY')
mail = Mail(app)

# CONFIGURE FLASK
app.config['SESSION_FILE_DIR'] = 'flask_session'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["TEMPLATES_AUTO_RELOAD"] = True
# Set the session timeout to 30 minutes (1800 seconds)
app.config['PERMANENT_SESSION_LIFETIME'] = 1800

Session(app)

# ENSURE TEMPLATE ARE AUTO RELOADED
@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# REQUIRE SIGNUP BEFORE ACCESSING EMAIL VERIFICATION PAGE
def require_signup(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if user_id is None:
            # User has not signed up or does not have a valid session
            return redirect(url_for('signup'))
        return f(*args, **kwargs)
    return decorated_function


# REQUIRE LOGIN BEFORE ACCESSING HOME PAGE
def require_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if user_id is None:
            # User has not logged in or does not have a valid session
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# DELETE USER IF NOT VERIFY EMAIL WITHIN AN HOUR
def check_and_delete_unverified_user():
    global deleted_users_flag
    global deleted_user_id
    # Get a list of unverified users
    unverified_users = query.get_unverified_users()
    if len(unverified_users) == 0:
        print("No unverified users")
        return None

    # Check each unverified user signup time
    for user in unverified_users:
        signup_time = user['created_at']
        current_time = datetime.now()
        time_difference = current_time - signup_time
        # Check if an hour has passed since the user signed up
        if time_difference.seconds >= 3600:
            # Delete the user
            print(f"Delete expired unverified user: {user['username']} with email: {user['email']}")
            query.delete_user(user['email'])
            deleted_users_flag = True  # Set the flag to True if any unverified users were deleted
            deleted_user_id = user['id']
        else:
            print(f"Unverified user: {user['username']} with email: {user['email']} has not expired")

# Before each request, check the deleted_users_flag and perform the redirect if necessary
@app.before_request
def check_deleted_users():
    global deleted_users_flag
    global deleted_user_id
    if deleted_users_flag:
        if session['user_id'] == deleted_user_id:
            print(f"Logout user: {session['user_id']}")
            session.pop('user_id', None)
            deleted_users_flag = False  # Reset the flag
            return redirect(url_for('signup'))
    
# Config for APScheduler
app.config['SCHEDULER_API_ENABLED'] = True
app.config['JOBS'] = [
    {
        'id': 'check_unverified_users',
        'func': check_and_delete_unverified_user,
        'trigger': 'interval',
        'seconds': 1800  # Run every 30 mins
    }
]

# Initialize the scheduler
scheduler.init_app(app)
scheduler.start()

# Intro page
@app.route('/')
def intro():
    if (session.get('user_id') is not None):
        print("User already logged in, redirect to home page")
        return redirect(url_for('home'))
    print("intro page") 
    return render_template('intro.html')

# Home page
@app.route('/home')
@require_signup
def home():
    username = query.get_username(session['user_id'])
    email_verify = query.check_email_verified(username)
    if email_verify == 0:
        print("Email not verified, redirect to verify email page")
        return redirect(url_for('verify'))
    elif session['valid_access'] == False:
        print("Invalid access, redirect to login page")
        return redirect(url_for('login'))
    print("Home page")

    #return render_template('index.html', username=query.get_username(session['user_id']))
    return render_template('index2.html', username=query.get_username(session['user_id']))
# Login page
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'GET':
        print("Login page")
        # Clear sessions
        if (session.get('user_id')):
            session.pop('user_id', None)
        # Set the session values to default
        session['update_password'] = False # Set to defaul
        session['sign_up'] = False # Set to defaul
        session['valid_access'] = True # Set to defaul
        return render_template('login.html')
    elif request.method == 'POST':
        # Get the user inputs
        username = request.form.get('username')
        password = request.form.get('password')
        remember_me = request.form.get('remember_me')
        
        print(f"Username: {username}")
        print(f"Password: {password}")
        # Check if username is inputted
        if not username:
            print("Username not inputted")
            status_message = 'username_not_inputted'
            return jsonify({'status': False, 'message': status_message})
        
        # Check if password is inputted
        if not password:
            print("Password not inputted")
            status_message = 'password_not_inputted'
            return jsonify({'status': False, 'message': status_message})
             
        # Check if username exists
        if not query.check_username_exists(username):
            print("Username does not exist")
            status_message = 'username_not_exist'
            return jsonify({'status': False, 'message': status_message})

        # Check if password matches
        password_check = check_password_hash(query.get_hashed_password(username), password)
        if not password_check:
            print("Password does not match")
            status_message = 'password_not_match'
            return jsonify({'status': False, 'message': status_message})

        # Log user in
        session['user_id'] = query.get_id(username)
        
        # Check wether user check the remember me checkbox
        if (remember_me):
            session["PERMANENT_SESSION_LIFETIME"] = 604800 # 7 days
        else:
            session["PERMANENT_SESSION_LIFETIME"] = 1800 # 1 hour

        print("Session life time: ", session["PERMANENT_SESSION_LIFETIME"])
        # Check whether user has verified email
        email_verified = query.check_email_verified(username)

        # Move to verify page if email not verified
        if email_verified == 0:
            return redirect('/verify')
        else:
            # Move to home page if email verified
            return redirect('/home')
        
@app.route('/logout', methods=['GET'])
def logout():
   
    # Clear the user's session data
    if session.get('user_id'):
        session.pop('user_id', None)
    session['update_password'] = False # Set to defaul
    session['sign_up'] = False # Set to defaul
    session['valid_access'] = True # Set to defaul
    # Redirect the user to the home page or any other page after logout
    return redirect('/login')

# Signup page
@app.route('/signup', methods=["GET", "POST"])
def signup():
    print("Signup page")
    # Client react to check valid inputs
    if request.method == 'GET':
        # Clear sessions
        if session.get('user_id'):
            session.pop('user_id', None)
        # Set the session values to default
        session['update_password'] = False # Set to defaul
        session['sign_up'] = False # Set to defaul
        session['valid_access'] = True # Set to default

        username = request.args.get('username')
        email = request.args.get('email')
        
        if username:
            username_exists = query.check_username_exists(username)
            return jsonify({"username_exists": username_exists})
        if email:
            email_exists = query.check_email_exists(email)
            return jsonify({"email_exists": email_exists})

    elif request.method == 'POST':
        # Delete expired verification code
        print("Delete expired verification code")
        query.delete_email()

        # Get the user inputs
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        email = request.form.get('email')
        rules = request.form.get('rules')

        # Perform the password match check
        password_match = password == confirm_password

        # Server side check valid inputs
        if not isValidUsername(username):
            print("Invalid username")
            return redirect('/signup')
        
        if query.check_username_exists(username):
            print("Username exist") 
            return redirect('/signup')

        if not isValidPassword(password):
            print("Invalid password")
            return redirect('/signup')

        if not password_match:
            print("Password does not match")
            return redirect('/signup')

        if not isValidEmail(email):
            print("Invalid email")
            return redirect('/signup')

        if query.check_email_exists(email):
            print("Email exist")
            return redirect('/signup')

        if not rules:
            print("You must accept the rules")
            return redirect('/signup')
        
        # Hash passwords
        hash_password = generate_password_hash(password)
        print(f"Hash password generated: {hash_password}")

        # Add the user to the database temporarily
        print("Add user to the database")
        query.add_user(username, hash_password, email)
        
        # Generate verification code and save into the database
        verification_code, expiration_time = flask_email.generate_verification_code()
        print(f"Verification code generated: {verification_code}, expired in {expiration_time}")
        query.save_verification_code(email, verification_code, expiration_time)

        # Send verification email
        print("Send verification email")
        flask_email.send_verification_email(email, verification_code, username, 'signup')
        
        # Log user in for verification only
        print("Log user in for verification only")
        session['user_id'] = query.get_id(username)
        session['sign_up'] = True

        print('Redirect to verify page, username: ', username, 'email: ', email)

        return redirect(url_for('verify', username=username, user_email=email))

    return render_template('signup.html')

# Forget password page
@app.route('/forget', methods=["GET", "POST"])
def forget():
    if request.method == 'GET':
        print("Forget password page")
        # Clear sessions
        if (session.get('user_id')):
            session.pop('user_id', None)
         # Set the session values to default
        session['update_password'] = False # Set to defaul
        session['sign_up'] = False # Set to defaul
        session['valid_access'] = True # Set to default

        return render_template('forget.html')
    elif request.method == 'POST':
        # Delete expired verification code
        print("Delete expired verification code")
        query.delete_email()

        # Get the user inputs
        username = request.form.get('username')
        email = request.form.get('email')
        check_data = request.form.get('check_data')
        print(f"Username: {username}")
        print(f"Email: {email}")

        print("Check data: ", check_data)
        if (check_data):
            # Check if username is inputted
            if not username:
                print("Username not inputted")
                status_message = 'username_not_inputted'
                return jsonify({'status': False, 'message': status_message})
            
            # Check if email is inputted
            if not email:
                print("Email not inputted")
                status_message = 'Email_not_inputted'
                return jsonify({'status': False, 'message': status_message})
                
            # Check if username exists
            if not query.check_username_exists(username):
                print("Username does not exist")
                status_message = 'username_not_exist'
                return jsonify({'status': False, 'message': status_message})
            

            # Check if email matches username
            user_id = query.get_id(username)
            user_email = query.get_email(user_id)
            if (email != user_email):
                print("Email not match username")
                status_message = 'email_not_match_username'
                return jsonify({'status': False, 'message': status_message})
            # Return successful message to client
            print("Data check pass, return JSON: status: True, message: success")
            return jsonify({'status': True, 'message': 'success'})
        
        # Data check pass, real submission
        else:
            # Generate verification code and save into the database
            verification_code, expiration_time = flask_email.generate_verification_code()
            print(f"Verification code generated: {verification_code}, expired in {expiration_time}")
            print("Save verification code into database")
            query.save_verification_code(email, verification_code, expiration_time)

            # Send verification email
            print("Send verification email")
            flask_email.send_verification_email(email, verification_code, username, 'reset_password')
            
            # Log user in for verification only
            print("Log user in for verification only")
            session['user_id'] = query.get_id(username)
            session['valid_access'] = False # Only allow access to the verification page, not allow to sign in
            session['update_password'] = True # Indicate that the user is using forget password feature

            # Redirect to Verify page
            print('Redirect to verify page, username: ', username, 'email: ', email)
            return redirect(url_for('verify', username=username, user_email=email))

# Update password page
@app.route('/update_password', methods=["GET", "POST"])
@require_login
def update_password():
    if request.method == 'GET':
        print("Update password page")
        return render_template('update.html')
    elif request.method == 'POST':
        # Get the user inputs
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        print(f"Password: {password}")
        print(f"Confirm password: {confirm_password}")
        # Check for inputs
        if not password:
            print("Password not inputted")
            return jsonify({'status': False, 'message': 'CANNOT BE EMPTY', 'key': 'password'})
        if not confirm_password:
            print("Confirm password not inputted")
            return jsonify({'status': False, 'message': 'CANNOT BE EMPTY', 'key': 'confirm_password'})
        # Check whether password has at least 8 characters
        if len(password) < 8:
            print("Password must have at least 8 characters")
            return jsonify({'status': False, 'message': 'AT LEAST 8 CHARACTERS', 'key': 'password'})
        # Check whether password and confirm password match
        if password != confirm_password:  
            print("Password and confirm password do not match")
            return jsonify({'status': False, 'message': 'PASSWORD DO NOT MATCH', 'key': 'confirm_password'})

        # If the form is submitted by user (not by default POST method)
        message = request.form.get('pass')
        print(f"Message: {message}")
        if (message):
        # Hash password
            print("Hash password")
            hash_password = generate_password_hash(password)

            # Update password in the database
            print("Update password in the database")
            query.update_password(session['user_id'], hash_password)

            # Reset the flag
            print("Reset the flag")
            session['update_password'] = False
            session['valid_access'] = True

        # Redirect to the flash message page
        print("Redirect to the flash message page")
        flash("Update password successfully!")
        flash_message = get_flashed_messages()
        return render_template('flash_message.html', flash_message=flash_message[0])
        
# Email verification page
@app.route('/verify', methods=["GET", "POST"], defaults={'path': ''})
@app.route('/verify/<path:path>', methods=["GET", "POST"])
@require_login
def verify(path):
    print("Verify page")
    if request.method == 'GET':
        # Get info back
        username = request.args.get('username')
        user_email = request.args.get('user_email')
        print('user email: ', user_email)
        resend = request.args.get('resend')
        if resend == 'true':
            print('Resend verification email')
            # Generate verification code
            print('Generate verification code')
            verification_code, expiration_time = flask_email.generate_verification_code()
            print(f"Verification code generated: {verification_code}, expired in {expiration_time}")
            query.save_verification_code(user_email, verification_code, expiration_time)

            # Send verification email
            print('Send verification email')
            if session['update_password'] == True:
                purpose = 'reset_password'
            elif session['sign_up'] == True:
                purpose = 'sign_up'
            flask_email.send_verification_email(user_email, verification_code, username, purpose)
        return render_template('verify.html', username=query.get_username(session.get('user_id')), user_email=query.get_email(session.get('user_id')))
    
    elif request.method == 'POST':
        # Get the verification code entered by the user
        verification_code_entered = request.form.get('verification_code')
        print('Verification code entered: ', verification_code_entered)

        if not verification_code_entered:
            print('Please fill the verification code')
            flash('Please fill the verification code', 'error')
            return jsonify({"missing_code": verification_code_entered})
        
        user_email = query.get_email(session.get('user_id'))
        # Retrieve the verification code and its expiration time from the database
        verification_code_stored, expiration_time = query.get_verification_code_expiration_time(user_email)
        print(f'Verification code stored: {verification_code_stored}, expired in {expiration_time}')
        
        # Check if the verification code is valid
        if verification_code_stored == verification_code_entered:
            print('Verification code is correct')
        else:
            flash('Invalid verification code. Please try again.', 'error')
            print('Invalid verification code. Please try again.')
            return jsonify({"invalid_code": verification_code_entered})

        if expiration_time is None or datetime.now() > expiration_time:
            flash('Verification code has expired. Please request a new one.', 'error')
            print('Verification code has expired. Please request a new one.')
            return jsonify({"expired_code": verification_code_entered})
        
        # Execute code when all conditions are met
        print("Session Sign up: ", session.get('sign_up'))
        print("Session Update password: ", session.get('update_password'))
        print("Session Valid access: ", session.get('valid_access'))

        if (session.get('sign_up')):
            # Mark the email as verified in the database (e.g., set a flag)
            query.mark_email_as_verified(user_email)
            
            print('Email verification successful!')

            flash("Account created successfully!")
            print("Account created successfully.")

            # Log user out and redirect to login page
            print("Log user out and redirect to login page")
            session['valid_access'] = True

            flash_message = get_flashed_messages()
            print(f"Flash message: {flash_message}")
            if flash_message:
                return render_template('flash_message.html', flash_message=flash_message[0])
        if (session.get('update_password')):
            session['update_password'] = True
            # Move to the update password page
            return redirect('/update_password')
        
@app.route('/session_lifetime', methods=['GET'])
def get_session_lifetime():
    session_lifetime = app.config['PERMANENT_SESSION_LIFETIME']
    return jsonify({'session_lifetime': session_lifetime})
    

if __name__ == "__main__":
    app.run(debug=True)
import random
import string
from datetime import datetime, timedelta
from flask import Flask, flash, redirect, render_template, request, session, jsonify, url_for
from flask_mail import Mail, Message
from dotenv import load_dotenv, dotenv_values
import os

# Load the key for environment variables
load_dotenv()

app = Flask(__name__)   

# Configure Flask app with mail settings
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

# Initialize Flask-Mail
mail = Mail(app)

# Generate a random verification code
def generate_verification_code():
    characters = string.ascii_letters + string.digits
    verification_code = ''.join(random.choice(characters) for i in range(6))
    expiration_time = datetime.now() + timedelta(minutes=3)
    return verification_code, expiration_time

# Send the verification code to the user's email
def send_verification_email(email, verification_code, username, purpose):
    if purpose == 'signup':
        subject = 'Music Generator: Verify your email'
    elif purpose == 'reset_password':
        subject = 'Music Generator: Reset your password'
    sender_email = app.config['MAIL_USERNAME']  # Use the configured sender email
    message = Message(subject=subject, sender=sender_email, recipients=[email])
    if purpose == 'signup':
        email_template = render_template('signup_email_template.html', verification_code=verification_code, username=username)
    elif purpose == 'reset_password':
        email_template = render_template('reset_password_email_template.html', verification_code=verification_code, username=username)
    message.html = email_template
    mail.send(message)



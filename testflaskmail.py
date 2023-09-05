from flask import Flask
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

@app.route('/')
def send_email():
    # Create a message to be sent
    subject = 'Hello from Flask-Mail'
    sender_email = app.config['MAIL_USERNAME']  # Use the configured sender email
    recipient_email = 'buiphucthinh02@gmail.com'  # Replace with the recipient's email address
    body = 'This is a test email sent from Flask-Mail!'
    message = Message(subject=subject, sender=sender_email, recipients=[recipient_email])
    message.body = body

    try:
        # Send the email
        mail.send(message)
        return 'Email sent successfully!'
    except Exception as e:
        return f'Error sending email: {str(e)}'

if __name__ == '__main__':
    app.run(debug=True)

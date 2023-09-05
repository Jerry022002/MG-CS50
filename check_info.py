import re
def isValidEmail(email):
    # Regular expression for email validation
    emailRegex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(emailRegex, email)

def isValidUsername(username):
    # Regular expression for username validation
    usernameRegex = r'^[a-zA-Z0-9]{3,}$'
    return re.match(usernameRegex, username)

def isValidPassword(password):
    # Regular expression for password validation
    passwordRegex = r'^[a-zA-Z0-9]{8,}$'
    return re.match(passwordRegex, password)

print(isValidPassword("Jerry123"))
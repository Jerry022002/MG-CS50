import os, glob
import query
import pickle

# Step 2: Retrieve active user sessions from the flask_session folder
folder_name = 'flask_session'
current_dir = os.path.dirname(os.path.abspath(__file__))
session_folder = os.path.join(current_dir, folder_name)

session_files = os.listdir(session_folder)

print(session_files)
        
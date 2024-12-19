import streamlit as st
from streamlit_option_menu import option_menu
import sqlite3
import os
import uuid
from PIL import Image

# Create a folder to store images if it doesn't exist
IMAGE_FOLDER = "images"
if not os.path.exists(IMAGE_FOLDER):
    os.makedirs(IMAGE_FOLDER)

# Create a SQLite database and a table for user information
conn = sqlite3.connect('users.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT
    )
''')

# Create Complaints table if not exists
cursor.execute('''
CREATE TABLE IF NOT EXISTS Complaints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    image_name TEXT,
    complaint_type TEXT,
    complaint_title TEXT,
    complaint_description TEXT,
    complaint_area TEXT,
    priority TEXT,
    raising_person_name TEXT,
    raising_person_mobile TEXT,
    raising_person_email TEXT,
    status TEXT
)
''')
# here is geolocation

conn.commit()

def is_user_exists(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    return cursor.fetchone() is not None

def is_username_exists(username):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    return cursor.fetchone() is not None

def create_user(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
    conn.commit()

def login(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()
    if user:
        return True
    return False

# Sidebar for navigation
with st.sidebar:
    selected = option_menu('Pothole & Light Complaint Website',
                           ['Register',
                           'Login',
                            'Raise Complaint',
                            'View Complaint Status',
                            'Logout'],
                           icons=['file-earmark-person', 'person', 'hand-index', 'view-list', 'box-arrow-right'],
                           default_index=0)

if selected == "Login":
    st.header("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if login(username, password):
            st.success("Logged in as " + username)
            st.session_state.logged_in = True
        else:
            st.error("Invalid username or password")
            st.session_state.logged_in = False

if selected == "Register":
    st.header("Register")
    new_username = st.text_input("New Username")
    new_password = st.text_input("New Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    if new_password == confirm_password:
        if st.button("Register"):
            if new_username and new_password:
                if is_username_exists(new_username):
                    st.error('Username already exists. Please choose a different one.')
                else:
                    create_user(new_username, new_password)
                    st.success("Registration successful. You can now log in.")
    else:
        st.error("Passwords do not match")

if selected == "Raise Complaint":
    st.title("Raise Complaint")

    if st.session_state.get("logged_in", False):

        complaint_type = st.radio("Complaint Type", ["Pothole", "Light Complaint"])
        complaint_title = st.text_input("Complaint Title")
        complaint_description = st.text_area("Complaint Description")
        complaint_area = st.text_input("Complaint Area/Address")
        priority = st.selectbox("Priority", ["High", "Low", "Mid"])
        raising_person_name = st.text_input("Your Name")
        raising_person_mobile = st.text_input("Your Mobile Number")
        raising_person_email = st.text_input("Your Email")
        uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])
        st.write(f"**Note:** Please fill all fields")

        if st.button("Submit Complaint"):

            try:
                #print(complaint_type, complaint_title, complaint_description, complaint_area, priority, raising_person_name, raising_person_email, raising_person_mobile, uploaded_file)

                if (uploaded_file is not None and complaint_type !='' and complaint_title !='' and complaint_description !='' and complaint_area !='' and priority !='' and raising_person_name !=''):
                    # Generate a random unique ID for the image filename
                    unique_id = str(uuid.uuid4().hex)[:8]
                    image_name = f"{unique_id}.png"  # Save all images as PNG for simplicity

                    # Save image to the folder
                    image_path = os.path.join(IMAGE_FOLDER, image_name)
                    with open(image_path, "wb") as f:
                        f.write(uploaded_file.getvalue())

                    cursor.execute('''
                        INSERT INTO Complaints (image_name, complaint_type, complaint_title, complaint_description, 
                                                complaint_area, priority, raising_person_name, 
                                                raising_person_mobile, raising_person_email, status)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (image_name, complaint_type, complaint_title, complaint_description, complaint_area,
                          priority, raising_person_name, raising_person_mobile, raising_person_email, 'Pending'))

                    # cursor.execute('''
                    #         INSERT INTO Complaints (complaint_type, complaint_title, complaint_description,
                    #                                 complaint_area, priority, raising_person_name,
                    #                                 raising_person_mobile, raising_person_email, image_name)
                    #         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    #     ''', (complaint_type, complaint_title, complaint_description, complaint_area,
                    #           priority, raising_person_name, raising_person_mobile, raising_person_email, image_name))
                    conn.commit()
                    st.success("Complaint submitted successfully.")

                else:
                    st.warning("Please fill in all the required fields before submitting the complaint.")

            except Exception as e:
                st.error(f"Error: {e}")
                print(e)

    else:
        st.warning("Please log in to access this page.")

if selected == "View Complaint Status":
    st.title("View Complaint Status")

    if st.session_state.get("logged_in", False):

        cursor.execute('''SELECT complaint_type, complaint_title, complaint_description, 
                          complaint_area, priority, status, id, image_name FROM Complaints''')
        complaints = cursor.fetchall()

        for complaint in complaints:
            st.image(os.path.join(IMAGE_FOLDER, complaint[7]), caption=f"Image ID: {complaint[6]}", use_column_width=True)
            st.write(f"**Title:** {complaint[1]}")
            st.write(f"**Description:** {complaint[2]}")
            st.write(f"**Address:** {complaint[3]}")
            st.write(f"**Type:** {complaint[0]} | **Priority:** {complaint[4]} | **Status:** {complaint[5]}")
            st.write("---")

    else:
        st.warning("Please log in to access this page.")
        print("I'm warning")


if selected == "Logout":
    st.session_state.logged_in = False
    st.success("You have been logged out.")

# Close the database connection when the Streamlit app is done
conn.close()



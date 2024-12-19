import streamlit as st
from streamlit_option_menu import option_menu
import sqlite3
import os
import uuid

IMAGE_FOLDER = "images"

# Create a SQLite database and a table for user information
conn = sqlite3.connect('users.db')
cursor = conn.cursor()

conn.commit()


def login(username, password):
    if username=='admin' and password=='admin123':
        return True
    return False

# Sidebar for navigation
with st.sidebar:
    selected = option_menu('Pothole & Light Complaint Website',
                           ['Login',
                            'View Complaint Status',
                            'Logout'],
                           icons=['person', 'view-list', 'box-arrow-right'],
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


if selected == "View Complaint Status":
    st.title("View Complaint Status")

    if st.session_state.get("logged_in", False):

        cursor.execute('''SELECT complaint_type, complaint_title, complaint_description, 
                          complaint_area, priority, status, id, image_name, raising_person_name, 
                          raising_person_mobile FROM Complaints''')
        complaints = cursor.fetchall()

        for complaint in complaints:
            st.image(os.path.join(IMAGE_FOLDER, complaint[7]), caption=f"Image ID: {complaint[6]}", use_column_width=True)
            st.write(f"**Title:** {complaint[1]}")
            st.write(f"**Description:** {complaint[2]}")
            st.write(f"**Address:** {complaint[3]}")
            st.write(f"**Type:** {complaint[0]} | **Priority:** {complaint[4]} | **Status:** {complaint[5]}")
            st.write(f"**Citizen Name:** {complaint[8]} | **Mobile No:** {complaint[9]}")
            # Button to edit status
            new_status = st.selectbox(f"Edit Status for Complaint {complaint[6]}",
                                      ["Pending", "In-Process", "Completed"], key=f"edit_status_{complaint[6]}")
            if st.button(f"Update Status for Complaint {complaint[6]}", key=f"update_status_{complaint[6]}"):
                # Update status in the database
                cursor.execute("UPDATE Complaints SET status=? WHERE id=?", (new_status, complaint[6]))
                conn.commit()
                st.success(f"Status for Complaint {complaint[6]} updated successfully.")

            st.write("---")

    else:
        st.warning("Please log in to access this page.")
        print("I'm warning")


if selected == "Logout":
    st.session_state.logged_in = False
    st.success("You have been logged out.")

# Close the database connection when the Streamlit app is done
conn.close()



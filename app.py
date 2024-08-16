from dotenv import load_dotenv
import os
import pyodbc
import streamlit as st
from urllib.parse import quote_plus
from userManagement import UserAuth
from datetime import datetime
import requests

# Load environment variables from .env file
load_dotenv()

# Read database configuration from environment variables
db_driver = os.getenv('DB_DRIVER')
db_server = os.getenv('DB_SERVER')
db_name = os.getenv('DB_NAME')
db_username = os.getenv('DB_USERNAME')
db_password = os.getenv('DB_PASSWORD')

# Construct the database connection string
db_conn_str = f"DRIVER={db_driver};SERVER={db_server};DATABASE={db_name};UID={db_username};PWD={db_password}"

# Initialize UserAuth
auth = UserAuth(db_conn_str=db_conn_str)

# Function to get IP address and location data
def get_location_data():
    try:
        ip_response = requests.get("https://api.ipify.org?format=json")
        ip = ip_response.json()["ip"]

        geo_response = requests.get(f"https://ipinfo.io/{ip}/json")
        geo_data = geo_response.json()

        return ip, geo_data
    except Exception as e:
        st.error("Failed to retrieve location data.")
        return None, None

# Function to save location data to the database
def save_location_data(user_id, status, geo_data, ip):
    conn = pyodbc.connect(db_conn_str)
    cursor = conn.cursor()
    
    coordinates = geo_data.get('loc') if geo_data else None
    event_time = datetime.now()
    
    cursor.execute("""
        INSERT INTO UserLocationData (user_id, status, event_time, geolocation_coordinates, ip_address)
        VALUES (?, ?, ?, ?, ?)
    """, user_id, status, event_time, coordinates, ip)
    
    conn.commit()
    cursor.close()
    conn.close()

# Automatically get location data
ip, geo_data = get_location_data()

# Main application logic
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'doc_info' not in st.session_state:
    st.session_state.doc_info = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'user_input' not in st.session_state:
    st.session_state.user_input = ''

if st.session_state.authenticated:
    st.sidebar.write(f"Welcome, {st.session_state.email}")
    
    if 'login_event_saved' not in st.session_state:
        save_location_data(st.session_state.user_id, "Logged In", geo_data, ip)
        st.session_state.login_event_saved = True
    
    if st.sidebar.button("Logout"):
        save_location_data(st.session_state.user_id, "Logged Out", geo_data, ip)
        st.session_state.authenticated = False
        st.session_state.email = None
        st.session_state.user_id = None
        st.session_state.reset_code = None
        st.session_state.doc_info = None
        st.session_state.login_event_saved = False
        st.rerun()

    # Sidebar content: source selection, document upload, database, and submit button
    st.sidebar.header("Upload Documents and Connect to Database")
    
    uploaded_files = st.sidebar.file_uploader("Choose a file", type=["docx", "xlsx", "pptx", "pdf"], accept_multiple_files=True)
    database = st.sidebar.text_input("Enter database name")
    submit_button = st.sidebar.button("Submit")

    if submit_button and uploaded_files:
        # Prepare files for upload
        files = []
        for file in uploaded_files:
            files.append(('file', file))

        # Upload the document to the Flask server
        response = requests.post("http://127.0.0.1:8080/saveDB", files=files)
        response_data = response.json()
        system_status = response.status_code

        if system_status == 200:
            st.sidebar.success("File uploaded successfully!")
            st.sidebar.write(response_data)
        else:
            st.sidebar.error("Failed to upload the file.")

    # Main Page: LLM Chat Interface
    st.title("LLM Chat Interface")

    # Choose between vector database or general model based on user input
    mode = st.selectbox("Choose mode:", ["General Model", "Vector Database"])

    # User input for chat
    user_input = st.text_input("Ask a question:", value=st.session_state.user_input, key="user_input")

    # Buttons to send or cancel the query
    col1, col2 = st.columns([1, 1])
    with col1:
        send_button = st.button("Send", key="send_button")
    with col2:
        cancel_button = st.button("Cancel", key="cancel_button")

    # Display previous chat history with the latest chat on top
    def display_chat_history():
        for chat in reversed(st.session_state.chat_history):
            st.write(f"**User:** {chat['user']}")
            st.write(f"**LLM:** {chat['llm']}")
            st.markdown("---")

    display_chat_history()

    # Clear the input box if the cancel button is clicked
    if cancel_button:
        st.session_state.user_input = ''
        st.rerun()

    # Handle sending the query when the send button is clicked
    if send_button:
        if user_input:
            # Choose between vector database or general model based on user input
            if mode == "Vector Database":
                endpoint = "http://127.0.0.1:8080/dbQuerying"
            
                response = requests.post(endpoint, json={"query": user_input})
                
                if response.status_code == 200:
                    response_data = response.json()
                    llm_response = response_data.get("answer", "No response from LLM")
                    sources = response_data.get("sources", [])
                    
                    # Append to chat history
                    st.session_state.chat_history.append({"user": user_input, "llm": llm_response, "sources": sources})

                    # Clear the input box after sending
                    display_chat_history()
                    st.rerun()  # Refresh the app to show the updated chat history
                else:
                    st.error("Failed to get a response from the model.")

            else:
                endpoint = "http://127.0.0.1:8080/ai"
                response = requests.post(endpoint, json={"query": user_input})
                
                if response.status_code == 200:
                    response_data = response.json()
                    llm_response = response_data['response']
                    # Append to chat history
                    st.session_state.chat_history.append({"user": user_input, "llm": llm_response})
                    # Display the updated chat history
                    display_chat_history()
                    st.rerun()  # This ensures the updated chat history is immediately displayed
                else:
                    st.error("Failed to get a response from the model.")

    # Option to clear chat history
    if st.button("Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()

else:
    st.title("User Authentication")

    auth_option = st.selectbox("Choose option:", ["Log In", "Sign Up"])

    if auth_option == "Log In":
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Log In"):
            user_id = auth.login_user(email, password)
            if user_id:
                st.session_state.authenticated = True
                st.session_state.email = email
                st.session_state.user_id = user_id
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error("Invalid email or password.")

    elif auth_option == "Sign Up":
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        first_name = st.text_input("Enter First Name")
        surname = st.text_input("Enter Surname")
        mobile_number = st.text_input("Enter Mobile Number")

        if st.button("Sign Up"):
            if password == confirm_password:
                user_id = auth.register_user(email, password, first_name, surname, mobile_number)
                if user_id:
                    st.success('Signed up successfully! Please select "log in" option above to log in.', icon="🟢")
                else:
                    st.error("🔴 Failed to sign up. Email might already be registered.")
            else:
                st.error("🔴 Passwords do not match.")

    elif auth_option == "Reset Password":
        email = st.text_input("Email")

        if st.button("Send Reset Code"):
            reset_code = auth.send_reset_code(email)
            if reset_code:
                st.session_state.reset_code = reset_code
                st.success("Reset code sent to your email.")
            else:
                st.error("Failed to send reset code. Email might not be registered.")

        if 'reset_code' in st.session_state:
            entered_code = st.text_input("Enter Reset Code")
            new_password = st.text_input("New Password", type="password")
            confirm_new_password = st.text_input("Confirm New Password", type="password")

            if st.button("Reset Password"):
                if new_password == confirm_new_password:
                    success = auth.reset_password(st.session_state.reset_code, new_password)
                    if success:
                        st.success("Password reset successfully. Please log in.")
                        st.session_state.reset_code = None
                        st.rerun()
                    else:
                        st.error("Failed to reset password.")
                else:
                    st.error("Passwords do not match.")

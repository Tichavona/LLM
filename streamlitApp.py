import streamlit as st
import requests
import pyodbc
from userManagement import UserAuth
from datetime import datetime

# Connection string for SQL Server
db_conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=TVAKISAI\\DECISIONEDGE;DATABASE=dbGPT;UID=deAdmin;PWD=D3c!s!0n3dg3'

# Initialize UserAuth
auth = UserAuth(db_conn_str=db_conn_str)

# Initialize session state for the authenticated user
def init_user_session():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'doc_info' not in st.session_state:
        st.session_state.doc_info = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = {}
    if 'user_input' not in st.session_state:
        st.session_state.user_input = ''
    if 'current_chat' not in st.session_state:
        st.session_state.current_chat = None
    if 'login_event_saved' not in st.session_state:
        st.session_state.login_event_saved = False
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None  # Ensure user_id is initialized

# Call the session initialization function before checking authenticated state
init_user_session()

# Helper function to generate a chat name based on user input
def generate_chat_name(user_input):
    words = user_input.split()
    return ' '.join(words[:5]) + "..." if len(words) > 5 else ' '.join(words)

# Function to get IP address and location data
def get_location_data():
    try:
        ip_response = requests.get("https://api.ipify.org?format=json")
        ip = ip_response.json()["ip"]

        geo_response = requests.get(f"https://ipinfo.io/{ip}/json")
        geo_data = geo_response.json()

        return ip, geo_data
    except Exception as e:
        return None, None  # No feedback if location data retrieval fails

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

# Function to save chat activity to the database
def save_chat_activity(user_id, chat_name, user_input, llm_response):
    conn = pyodbc.connect(db_conn_str)
    cursor = conn.cursor()
    
    event_time = datetime.now()
    
    cursor.execute("""
        INSERT INTO ChatActivities (user_id, chat_name, event_time, user_question, llm_response)
        VALUES (?, ?, ?, ?, ?)
    """, user_id, chat_name, event_time, user_input, llm_response)
    
    conn.commit()
    cursor.close()
    conn.close()

# Function to save chat session to the database
def save_chat_session(user_id, chat_name, chat_history):
    conn = pyodbc.connect(db_conn_str)
    cursor = conn.cursor()
    
    event_time = datetime.now()
    chat_history_str = str(chat_history)  # Convert dictionary to string
    
    cursor.execute("""
        INSERT INTO ChatSessions (user_id, chat_name, chat_history, event_time)
        VALUES (?, ?, ?, ?)
    """, user_id, chat_name, chat_history_str, event_time)
    
    conn.commit()
    cursor.close()
    conn.close()

# Function to get chat history from the database
def get_chat_history(user_id):
    conn = pyodbc.connect(db_conn_str)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT chat_name, chat_data
        FROM ChatSessions
        WHERE user_id = ?
    """, user_id)
    
    rows = cursor.fetchall()
    chat_history = {}
    
    for row in rows:
        chat_name = row.chat_name
        chat_history_str = row.chat_history
        chat_history[chat_name] = eval(chat_history_str)  # Convert string back to dictionary
    
    cursor.close()
    conn.close()
    
    return chat_history

# Automatically get location data
ip, geo_data = get_location_data()

if st.session_state.authenticated:
    st.sidebar.write(f"Welcome, {st.session_state.email}")

    if not st.session_state.login_event_saved:
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
        st.session_state.chat_history = {}
        st.rerun()

    # Sidebar content: source selection, document upload, database, and submit button
    st.sidebar.header("Upload Documents and Connect to Database")
    
    uploaded_files = st.sidebar.file_uploader("Choose a file", type=["docx", "xlsx", "pptx", "pdf"], accept_multiple_files=True, key="file_uploader")
    database = st.sidebar.text_input("Enter database name", key="database_name")
    submit_button = st.sidebar.button("Submit", key="submit_button")

    if submit_button and uploaded_files:
        files = []
        for file in uploaded_files:
            files.append(('file', file))

        response = requests.post("http://127.0.0.1:8080/saveDB", files=files)
        response_data = response.json()
        system_status = response.status_code

        if system_status == 200:
            st.sidebar.success("File uploaded successfully!")
            st.sidebar.write(response_data)
        else:
            st.sidebar.error("Failed to upload the file.")

    # Start a new chat session (Dropdown)
    st.sidebar.subheader("Select or Start a New Chat")
    chat_options = list(st.session_state.chat_history.get(st.session_state.user_id, {}).keys()) + ["New Chat"]
    selected_chat = st.sidebar.selectbox("Select a chat", chat_options, key="chat_selection")

    if selected_chat == "New Chat":
        st.session_state.current_chat = None
        st.session_state.user_input = ''
        st.session_state.chat_history[st.session_state.user_id] = {}  # Clear existing chat history for the user
        st.rerun()
    else:
        st.session_state.current_chat = selected_chat

    # Main Page: LLM Chat Interface
    st.title("LLM Chat Interface")

    # Choose between vector database or general model based on user input
    mode = st.selectbox("Choose mode:", ["General Model", "Vector Database"], key="mode_selection")

    # User input for chat
    user_input = st.text_input("Ask a question:", value=st.session_state.user_input, key="user_input")

    # Buttons to send or cancel the query
    col1, col2 = st.columns([1, 1])
    with col1:
        send_button = st.button("Send", key="send_button")
    with col2:
        cancel_button = st.button("Cancel", key="cancel_button")

    # Display previous chat history with the latest chat on top
    def display_chat_history(chat_name):
        if chat_name in st.session_state.chat_history.get(st.session_state.user_id, {}):
            for chat in reversed(st.session_state.chat_history[st.session_state.user_id][chat_name]):
                st.write(f"**User:** {chat['user']}")
                st.write(f"**LLM:** {chat['llm']}")
                st.markdown("---")

    if st.session_state.current_chat:
        display_chat_history(st.session_state.current_chat)

    # Clear the input box if the cancel button is clicked
    if cancel_button:
        st.session_state.user_input = ''
        st.rerun()

    # Handle sending the query when the send button is clicked
    if send_button:
        if user_input:
            if st.session_state.user_id not in st.session_state.chat_history:
                st.session_state.chat_history[st.session_state.user_id] = {}
            
            if mode == "Vector Database":
                endpoint = "http://127.0.0.1:8080/dbQuerying"
                response = requests.post(endpoint, json={"query": user_input})
                
                if response.status_code == 200:
                    response_data = response.json()
                    llm_response = response_data.get("answer", "No response from LLM")
                    sources = response_data.get("sources", [])
                    
                    chat_name = st.session_state.current_chat or generate_chat_name(user_input)
                    
                    if chat_name not in st.session_state.chat_history[st.session_state.user_id]:
                        st.session_state.chat_history[st.session_state.user_id][chat_name] = []
                    
                    st.session_state.chat_history[st.session_state.user_id][chat_name].append({"user": user_input, "llm": llm_response})
                    st.session_state.current_chat = chat_name  # Set the current chat to the generated name
                    
                    save_chat_activity(st.session_state.user_id, chat_name, user_input, llm_response)
                    save_chat_session(st.session_state.user_id, chat_name, st.session_state.chat_history[st.session_state.user_id])
                    
                    st.session_state.user_input = ''  # Clear input field after sending the message
                    
                    st.write(f"**User:** {user_input}")
                    st.write(f"**zbGPT:** {llm_response}")
                    if sources:
                        st.markdown("**Sources:**")
                        for source in sources:
                            st.markdown(f"- {source}")
                    st.markdown("---")
                else:
                    st.error("Failed to retrieve response from LLM.")
                    st.session_state.user_input = ''  # Clear input field
                    st.rerun()
            
            elif mode == "General Model":
                endpoint = "http://127.0.0.1:8080/dbDocumentReading"
                response = requests.post(endpoint, json={"query": user_input})
                
                if response.status_code == 200:
                    response_data = response.json()
                    llm_response = response_data.get("answer", "No response from LLM")
                    
                    chat_name = st.session_state.current_chat or generate_chat_name(user_input)
                    
                    if chat_name not in st.session_state.chat_history[st.session_state.user_id]:
                        st.session_state.chat_history[st.session_state.user_id][chat_name] = []
                    
                    st.session_state.chat_history[st.session_state.user_id][chat_name].append({"user": user_input, "llm": llm_response})
                    st.session_state.current_chat = chat_name  # Set the current chat to the generated name
                    
                    save_chat_activity(st.session_state.user_id, chat_name, user_input, llm_response)
                    save_chat_session(st.session_state.user_id, chat_name, st.session_state.chat_history[st.session_state.user_id])
                    
                    st.session_state.user_input = ''  # Clear input field after sending the message
                    
                    st.write(f"**User:** {user_input}")
                    st.write(f"**zbGPT:** {llm_response}")
                    st.markdown("---")
                else:
                    st.error("Failed to retrieve response from LLM.")
                    st.session_state.user_input = ''  # Clear input field
                    st.rerun()
        else:
            st.warning("Please enter a question before sending.")

    # Display existing chat sessions if user is authenticated
    if st.session_state.current_chat:
        display_chat_history(st.session_state.current_chat)

else:
    # User authentication
    st.title("User Authentication")

    auth_option = st.selectbox("Choose option:", ["Log In", "Sign Up", "Reset Password"])

    # Handle user authentication
    if auth_option == "Log In":
        email = st.text_input("Email", key="auth_email")
        password = st.text_input("Password", type="password", key="auth_password")

        if st.button("Login", key="auth_login"):
            if email and password:
                user_id = auth.get_user_id(email)  # Get the user ID from the database
                if auth.login_user(email, password) and user_id:
                    st.session_state.authenticated = True
                    st.session_state.email = email
                    st.session_state.user_id = user_id  # Set user ID in session state
                    st.session_state.user_input = ''
                    st.session_state.chat_history = get_chat_history(st.session_state.user_id)
                    st.session_state.login_event_saved = False
                    st.rerun()
                else:
                    st.error("Invalid email or password.")
            else:
                st.warning("Please enter both email and password.")

    elif auth_option == "Sign Up":
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

        if st.button("Sign Up"):
            if password == confirm_password:
                user_id = auth.register_user(email, password)
                if user_id:
                    st.success("Registered successfully!")
                    st.session_state.authenticated = True
                    st.session_state.email = email
                    st.session_state.user_id = user_id
                    st.rerun()
                else:
                    st.error("Registration failed. Please try again.")
            else:
                st.error("Passwords do not match.")

    elif auth_option == "Reset Password":
        email = st.text_input("Email")
        if st.button("Send Reset Code"):
            reset_code = auth.generate_reset_code(email)
            if reset_code:
                st.session_state.reset_code = reset_code
                st.success("Reset code sent to your email.")
            else:
                st.error("Failed to send reset code.")

        reset_code_input = st.text_input("Enter Reset Code")
        new_password = st.text_input("New Password", type="password")

        if st.button("Reset Password"):
            if reset_code_input == st.session_state.reset_code:
                user_id = auth.reset_password(email, new_password)
                if user_id:
                    st.success("Password reset successfully!")
                    st.session_state.authenticated = True
                    st.session_state.email = email
                    st.session_state.user_id = user_id
                    st.rerun()
                else:
                    st.error("Password reset failed. Please try again.")
            else:
                st.error("Invalid reset code.")


import subprocess
import time

def start_flask_app():
    subprocess.run(["python", "flaskApp.py"])

def start_streamlit_app():
    subprocess.run(["streamlit", "run", "streamlitApp.py"])

if __name__ == "__main__":
    # Start Flask app
    flask_process = subprocess.Popen(["python", "flaskApp.py"])
    
    # Wait a bit for Flask to start
    time.sleep(5)
    
    # Start Streamlit app
    streamlit_process = subprocess.Popen(["streamlit", "run", "streamlitApp.py"])
    
    # Wait for processes to complete
    flask_process.wait()
    streamlit_process.wait()

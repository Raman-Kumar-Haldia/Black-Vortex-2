import os
import subprocess
import sys
import time
import webbrowser

# Locate the folder where run.py is stored
current_folder = os.path.dirname(os.path.abspath(__file__))
app_path = os.path.join(current_folder, "app.py")

if os.path.exists(app_path):
    print("🚀 Starting Black Vortex server...")

    # Launch Streamlit with --server.address=0.0.0.0
    # This allows other devices (like your phone) on the same Wi-Fi to connect!
    subprocess.Popen(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            app_path,
            "--server.address=0.0.0.0",
        ]
    )

    # Wait 2 seconds for the server to spin up, then open local browser
    time.sleep(2)
    webbrowser.open("http://localhost:8501")
    print("🎉 Black Vortex is now running!")
    print(
        "📱 To open on your phone, use your PC's IP address: http://<YOUR_IP>:8501"
    )
else:
    print(f"❌ Could not find app.py in: {current_folder}")

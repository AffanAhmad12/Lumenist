import json
import bcrypt
import os

USER_FILE = os.path.join(os.path.dirname(__file__), "..", "config","users.json")

def load_users():
    with open(USER_FILE, "r") as f:
        return json.load(f)
    
def authenticate(username, password):
    """
    checks if username + password match.
    Returns the user's role if valid, None if invalid.
    """

    users = load_users()
    username = username.strip().lower()
    users_lower ={k.lower(): v for k, v in users.items()}

    if username not in users_lower:
        return None
    #storing both as bytes
    stored_hash= users_lower[username]["password"].encode("utf-8")
    if not bcrypt.checkpw(password.encode("utf-8"), stored_hash):
        return None
   #blocking non active users
    if users_lower[username].get("status") != "active":
        return None
    
    return users_lower[username]["role"]

if __name__ == "__main__":
    result = authenticate("HR", "Hr00123")
    print(result)
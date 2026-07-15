import json
import bcrypt
import os

USER_PATH = os.path.join(os.path.dirname(__file__), "..","config","users.json" )

def load_users():
    if not os.path.isfile(USER_PATH):
        return{}
    with open(USER_PATH, "r") as f:
        return json.load(f)
    
def save_users(users):
    with open(USER_PATH, "w") as f:
        json.dump(users, f , indent = 4)

def register_user(username, password):
    users= load_users()
    
    if username in users:
        return False, "Username already taken"
    
    hashed = bcrypt.hashpw(password.encode ("utf-8"), bcrypt.gensalt())
    hashed = hashed.decode("utf-8")

    users[username] = {
        "password" : hashed,
        "role" : None,
        "status":"pending" 
    }

    save_users(users)
    return True, "Account created. Waiting for admin approval."
if __name__ == "__main__":
    print(register_user("HARSH", "harsh123"))
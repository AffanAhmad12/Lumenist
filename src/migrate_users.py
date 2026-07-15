import json
import bcrypt
import os

USERS_PATH =os.path.join(os.path.dirname(__file__),"..","config","users.json")

def load_users():
    with open(USERS_PATH,"r")as f:
        return json.load(f)
    
def save_users(users):
    with open(USERS_PATH, "w") as f:
        json.dump(users, f , indent=4)
def migrate_users():
    users = load_users()

    for username, info in users.items():
        if info["password"].startswith("$2b$"):
            continue
        
        hashed = bcrypt.hashpw(info["password"].encode ("utf-8"), bcrypt.gensalt())
        info["password"] = hashed.decode("utf-8")
        info["status"]= "active"

    save_users(users)
    print("Migrate complete.")


if __name__ == "__main__":
    migrate_users()
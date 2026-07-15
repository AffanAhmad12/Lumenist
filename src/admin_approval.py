import json
import os
from signup import load_users, save_users

ROLES_PATH = os.path.join(os.path.dirname(__file__),"..","config","roles.json")

def load_valid_roles():
    with open(ROLES_PATH, "r") as f:
        roles = json.load(f)
    return list(roles.keys())

def list_pending_usrs(users):
    return{u: info for u,info in users.items()if info.get("status")== "pending"}

def approve_user(username,role, users, valid_roles):
    if role not in valid_roles:
        return False, f"Invalid role. Choose from: {valid_roles}"
    
    users[username]["role"] = role
    users[username]["status"] = "active"
    return True, f"{username} approved as {role}"
def main():
    users = load_users()
    valid_roles = load_valid_roles()

    pending = list_pending_usrs(users)
    if not pending:
        print("No pending users.")
        return
    
    print("Pending users:")
    for username in pending:
        print(f" - {username}")
    print(f"\nValid roles: {valid_roles}")

    for username in pending:
        role = input(f"Assign role for '{username}' (or leave blank to skip):").strip().upper()
        if not role:
            continue
        success, message = approve_user(username, role , users , valid_roles)
        print(message)
    save_users(users)
    print("\nDone. Saved changes to users.json.")

if __name__ == "__main__":
    main()
import os 
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    conn_str = os.environ.get("PG_CONNECTION","")
    conn_str = conn_str.replace("postgresql+psycopg://", "postgresql://")
    return psycopg2.connect(conn_str)

def load_valid_roles():
    """Get all role names from the roles table."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT role_name FROM roles ORDER BY role_name")
        roles = [row[0] for row in cur.fetchall()]
        cur.close()
        conn.close()
        return roles
    except Exception as e:
        print(f"Error loading roles: {e}")
        return[]
def list_pending_users():
    """Get all users waiting for approval."""
    try:
     conn = get_connection()
     cur = conn.cursor()
     cur.execute(
        "SELECT username FROM users WHERE is_approved= FALSE ORDER BY CREATED_at"
     )
     users = [row[0] for row in cur.fetchall()]
     cur.close()
     conn.close()
     return users
    except Exception as e:
        print(f"Error linstening pending users: {e}")
        return[]
def approve_user(username, role, valid_roles):
    """Approve a user and assign their role."""
    if role not in valid_roles:
        return False, f"Invalid role. Choos from :{valid_roles}"
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE users SET role=%s, is_approved=TRUE WHERE username=%s",
             (role, username.strip().lower())
        )

        conn.commit()
        cur.close()
        conn.close()
        return True, f"{username} approved as {role}"
    except Exception as e:
        return False, f"Approval failed: {e}"
def main():
    valid_roles = load_valid_roles()
    pending = list_pending_users()
    
    if not pending:
        print("No pending users.")
        return
    
    print("Pending users:")
    for username in pending:
        print(f"- {username}")
    print(f"\nValid roles : {valid_roles}")

    for username in pending:
        role = input(f"Assign role for '{username}' (or leave blank to skip):").strip().upper()
        if not role:
            continue
        success, message = approve_user(username, role, valid_roles)
        print(message)
    print("\nDONE.")

if __name__ == "__main__":
    main()
        
import os
import bcrypt
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    conn_str = os.environ.get("PG_CONNECTION", "")
    conn_str = conn_str.replace("postgresql+psycopg://","postgresql://")
    return psycopg2.connect(conn_str)

def register_user(username, password):
    """Register a new user with pending approval."""
    try:
        conn = get_connection()
        cur  = conn.cursor()

 # check if username already exists
        cur.execute("SELECT username FROM users WHERE username=%s", (username.strip().lower(),))
        if cur.fetchone():
            cur.close()
            conn.close()
            return False, "username already taken"
        
# hashing the pass

        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

  # insert new user with is_approved=FALSE until admin approves       
        cur.execute(
            "INSERT INTO users (username, password, role,is_approved) VALUES (%s, %s, %s, FALSE)",
            (username.strip().lower(),hashed,None)
        )
        conn.commit()
        cur.close()
        conn.close()
        return True, "Account created. Waiting for admin approval."
    except Exception as e:
        print(f"signup error: {e}")
        return False, f"Registration failed: {e}"
if __name__ == "__main__":
    print(register_user("HARSH", "harsh123"))
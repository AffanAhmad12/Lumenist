import os 
import psycopg2
import bcrypt
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    conn_str = os.environ.get("PG_CONNECTION", "")
    conn_str = conn_str.replace("postgresql+psycopg://", "postgresql://")
    return psycopg2.connect(conn_str)

def authenticate(username, password):
    """
    Check if username + password match in database.
    Returns the user's role if valid, None if invalid.
    """
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT password, role FROM users WHERE username=%s AND is_approved=TRUE",
            (username.strip().lower(),)   
        )
        result = cur.fetchone()
        cur.close()
        conn.close()

        if result:
           stored_password = result[0]
           role = result[1]
  # handle both bcrypt and plain text passwords          
           try:
               if bcrypt.checkpw(password.strip().encode("utf-8"), stored_password.encode("utf-8")):
                   return role
           except Exception:
 # fallback to plain text for existing users            
            if stored_password == password.strip():
                  return role
        return None
    except Exception as e:
        print(f"Auth error: {e}")
        return None
if __name__ == "__main__":
    result = authenticate("harsh", "harsh123")
    print(result)
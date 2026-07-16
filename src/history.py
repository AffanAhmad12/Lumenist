import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    conn_str = os.environ["PG_CONNECTION"]
     # convert langchain format to psycopg2
    conn_str= conn_str.replace("postgresql+psycopg://", "postgresql://")
    return psycopg2.connect(conn_str)

def save_message(username, question, answer, sources):
    """Save a Q&A pair to chat history."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO chat_history(username, question, answer , sources) VALUES(%s, %s, %s, %s)",
            (username, question, answer, ", ".join(sources)if sources else"")
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"History save error: {e}")
def get_user_history(username):
    """Get all past conversation for a user."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT question, answer , sources , timestamp FROM chat_history WHERE username= %s ORDER BY timestamp DESC",
            (username,)
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return[
            {
                "question": row[0],
                "answer" : row[1],
                "sources": row[2],
                "timestamp": row[3].strftime("%Y-%m-%d %H:%M")
            }
            for row in rows
        ]
    except Exception as e:
        print(f"History fetch error: {e}")
        return[]
def clear_user_history(username):
    """Delete all history for a user."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM chat_history WHERE username=%s", (username,))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"History clear error{e}")
import os 
import psycopg2
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    conn_str = os.environ.get("PG_CONNECTION", "")
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
            "SELECT username, created_at FROM users WHERE is_approved=FALSE ORDER BY created_at"
        )
        users = cur.fetchall()
        cur.close()
        conn.close()
        return users
    except Exception as e:
        print(f"Error listing pending users: {e}")
        return []
def approved_users(username, role, valid_roles):
    """Approve a user and assign their role."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE users SET role=%s, is_approved=TRUE WHERE username=%s",
            (role.upper(), username.lower())
        )
        conn.commit()
        cur.close()
        conn.close()
        return True, f"{username} approved as {role}"
    except Exception as e:
        return False, f"Approval Failed: {e}"
def delete_user(username):
    """Permanently delete a user from the database."""
    try:
        conn= get_connection()
        cur = conn.cursor()
        cur.execute(
            "DELETE FROM users WHERE username=%s",
            (username.strip().lower(),)
        )
        conn.commit()
        deleted = cur.rowcount
        cur.close()
        conn.close()
        if deleted:
            return True, f"{username} deleted."
        else:
            return False, f"no user found '{username}' found."
    except Exception as e:
        return False, f"Delete failed: {e}"
    

def show_admin_pannel():
    st.subheader("Admin: Approve Pending Users")

    pending = list_pending_users()
    if not pending:
        st.info("No pending users to approve.")
        return
    
    valid_roles = load_valid_roles()

    for username, created_at in pending:
        st.write(f"**{username}**")
        selected_role = st.selectbox(
            "Role", valid_roles, key=f"role_select_{username}"
        )
        if st.button("Approve", key=f"approve_{username}", use_container_width=True):
            success, message = approved_users(username, selected_role, valid_roles)
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)
        st.divider()
def show_delete_pannel():
    st.subheader("Admin: Remove Users")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT username FROM users ORDER BY username")
    all_usernames = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()

    if not all_usernames:
        st.info("No users in the database.")
        return
    
    for username in all_usernames:
        with st.expander(f"⚠️ Delete {username}"):
                st.warning(f"This will permanently delete user '{username}'. This cannot be undone.")
                confirm = st.checkbox("I understand this cannot be undone", key=f"confirm_delete_{username}")
                if st.button("Delete", key=f"delete_{username}", disabled=not confirm, use_container_width=True):
                   success, message = delete_user(username)
                   if success:
                    st.success(message)
                    st.rerun()
                   else:
                    st.error(message)
        

def main():
    valid_roles = load_valid_roles()
    pending = list_pending_users()

    if not pending:
        print("No pending users.")
        return
    
    print("Pending users:")
    for username, created_at in pending:
        print(f" - {username}")
    print(f"\nValid roles: {valid_roles}")

    for username in pending:
        role = input(f"Assign role for '{username}' (or leave blank to skip):").strip().upper()
        if not role:
            continue
        success, message = approved_users(username, role, valid_roles)
        print(message)
    print("\nDone.")
    
if __name__ == "__main__":
    main()
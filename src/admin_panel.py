from signup import load_users, save_users
import streamlit as st
import json


def show_admin_panel():
    st.subheader("Admin: Approve Pending Users")
    
    users = load_users()
    pending = {u: info for u, info in users.items() if info.get("status") == "pending"}

    if not pending:
        st.info("No pending users to approve.")
        return
    
    with open("config/roles.json", "r") as f:
        valid_roles = list(json.load(f).keys())
    
    for username in list(pending.keys()):
        st.write(f"**{username}**")
        selected_role = st.selectbox(
            "Role", valid_roles, key=f"role_select_{username}"
        )
        if st.button("Approve", key=f"approve_{username}", use_container_width=True):
            users[username]["role"]=selected_role
            users[username]["status"]="active"
            save_users(users)
            st.success(f"{username} approved as {selected_role}")
            st.rerun()
        st.divider()
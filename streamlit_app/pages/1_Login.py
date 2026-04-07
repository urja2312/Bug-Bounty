"""
Streamlit Auth Page (Login & Register)
"""
import streamlit as st
import requests
import re
import string

API_URL = "http://localhost:8000/api/v1"

def validate_password(password: str) -> bool:
    if len(password) < 8:
        st.error("Password must be at least 8 characters long.")
        return False
    if not any(c.isupper() for c in password):
        st.error("Password must contain at least one uppercase letter.")
        return False
    if not any(c.islower() for c in password):
        st.error("Password must contain at least one lowercase letter.")
        return False
    if not any(c.isdigit() for c in password):
        st.error("Password must contain at least one digit.")
        return False
    if not any(c in string.punctuation for c in password):
        st.error("Password must contain at least one special character.")
        return False
    return True

if st.session_state.token:
    st.success("You are already logged in!")
    if st.button("Logout"):
        st.session_state.token = None
        st.session_state.user = None
        st.rerun()
else:
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.header("Login")
        login_email = st.text_input("Email", key="login_email")
        login_pass = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            try:
                res = requests.post(
                    f"{API_URL}/auth/login",
                    data={"username": login_email, "password": login_pass}
                )
                if res.status_code == 200:
                    data = res.json()
                    st.session_state.token = data["access_token"]
                    st.session_state.user = data["user"]
                    st.success("Logged in successfully!")
                    st.rerun()
                else:
                    st.error(f"Login failed: {res.json().get('detail', 'Unknown error')}")
            except Exception as e:
                st.error(f"Connection error: {e}")
                
    with tab2:
        st.header("Register")
        reg_name = st.text_input("Full Name", key="reg_name")
        reg_email = st.text_input("Email", key="reg_email")
        reg_pass = st.text_input("Password", type="password", key="reg_pass", 
                                 help="Min 8 chars, 1 uppercase, 1 lowercase, 1 digit, 1 special char")
        reg_pass_confirm = st.text_input("Confirm Password", type="password", key="reg_pass_confirm")
        
        if st.button("Register"):
            if reg_pass != reg_pass_confirm:
                st.error("Passwords do not match.")
            elif validate_password(reg_pass):
                try:
                    res = requests.post(
                        f"{API_URL}/users", 
                        json={"email": reg_email, "password": reg_pass, "full_name": reg_name}
                    )
                    if res.status_code == 201:
                        st.success("Registration successful! Please login.")
                    else:
                        st.error(f"Registration failed: {res.json().get('detail', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Connection error: {e}")

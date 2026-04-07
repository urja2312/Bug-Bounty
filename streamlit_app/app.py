"""
Main Entry point for the Bug Bounty Platform Streamlit UI
"""
import streamlit as st

st.set_page_config(
    page_title="Bug Bounty Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize Session State
if "token" not in st.session_state:
    st.session_state.token = None
if "user" not in st.session_state:
    st.session_state.user = None

# Navigation
pages = {
    "Auth": [
        st.Page("pages/1_Login.py", title="Login / Register", icon="🔑"),
    ],
    "Platform": [
        st.Page("pages/2_Dashboard.py", title="Dashboard", icon="📊"),
        st.Page("pages/3_Programs.py", title="Programs", icon="🎯"),
        st.Page("pages/4_Reports.py", title="Vulnerability Reports", icon="🛡️"),
        st.Page("pages/5_Cryptography.py", title="Cryptography", icon="🔐"),
        st.Page("pages/6_Security_Logs.py", title="Security Operations Center", icon="🚨"),
    ]
}

pg = st.navigation(pages)
pg.run()

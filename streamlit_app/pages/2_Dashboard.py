"""
Streamlit Dashboard Page
"""
import streamlit as st
import requests
import pandas as pd

API_URL = "http://localhost:8000/api/v1"

if not st.session_state.token:
    st.warning("Please log in to view this page.")
    st.stop()

user = st.session_state.user

st.title("Dashboard")
st.write(f"Welcome back, **{user['full_name']}**! You are logged in as **{user['role']}**.")

col1, col2, col3 = st.columns(3)

# Fetch stats (dummy or real depending on backend readiness)
headers = {"Authorization": f"Bearer {st.session_state.token}"}
try:
    if user['role'] == "RESEARCHER":
        res = requests.get(f"{API_URL}/reports/me", headers=headers)
        reports = res.json().get("items", []) if res.status_code == 200 else []
        col1.metric("Total Submitted", len(reports))
        resolved = [r for r in reports if r['status'] == 'RESOLVED']
        col2.metric("Resolved", len(resolved))
        col3.metric("Bounties Earned", f"${sum(r.get('bounty_awarded', 0) for r in resolved)}")
        
        st.subheader("Your Recent Reports")
        if reports:
            df = pd.DataFrame(reports)
            st.dataframe(df[['title', 'severity', 'status', 'created_at']], use_container_width=True)
        else:
            st.info("No reports submitted yet.")
            
    else:
        # Company / Admin View
        res = requests.get(f"{API_URL}/programs", headers=headers)
        programs = res.json().get("items", []) if res.status_code == 200 else []
        col1.metric("Active Programs", len([p for p in programs if p['status'] == 'ACTIVE']))
        col2.metric("Total Reports", "...")
        col3.metric("Bounties Paid", "...")
        
        st.subheader("Your Programs")
        if programs:
            df = pd.DataFrame(programs)
            st.dataframe(df[['name', 'status', 'visibility', 'created_at']], use_container_width=True)
        else:
            st.info("No programs created yet.")
            
except Exception as e:
    st.error(f"Failed to load dashboard data: {e}")

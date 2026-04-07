"""
Streamlit Programs Page
"""
import streamlit as st
import requests
import pandas as pd

API_URL = "http://localhost:8000/api/v1"

if not st.session_state.token:
    st.warning("Please log in to view this page.")
    st.stop()

st.title("Bug Bounty Programs")

headers = {"Authorization": f"Bearer {st.session_state.token}"}

try:
    res = requests.get(f"{API_URL}/programs", headers=headers)
    if res.status_code == 200:
        programs = res.json().get("items", [])
        if not programs:
            st.info("No active bug bounty programs available at this time.")
        else:
            for p in programs:
                with st.expander(f"🛡️ {p['name']} ({p['status']})"):
                    st.write(f"**Description:** {p['description']}")
                    st.write(f"**Rules:** {p['rules']}")
                    if p.get('assets'):
                        st.subheader("In-Scope Assets")
                        assets_df = pd.DataFrame(p['assets'])
                        st.dataframe(assets_df[['asset_type', 'identifier', 'description']], use_container_width=True)
                    
                    st.button("Submit Report for this Program", key=f"btn_{p['id']}")
    else:
        st.error(f"Failed to fetch programs: {res.text}")
except Exception as e:
    st.error(f"Error loading programs: {e}")

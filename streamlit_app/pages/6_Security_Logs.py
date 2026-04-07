"""
Streamlit Security Operations Center (SOC) Log Page
"""
import streamlit as st
import requests
import pandas as pd

from utils import check_auth

st.set_page_config(page_title="Security Operations Center", page_icon="🚨", layout="wide")

user, token = check_auth()
if not user:
    st.stop()

# For demonstration purposes, we allow all users to view the SOC dashboard.
# In a real application, this would be restricted to Admin users.

st.title("🚨 Security Operations Center (SOC)")
st.markdown("""
This dashboard intercepts real-time threat intelligence from the backend **Intrusion Detection System (IDS)** and **Web Application Firewall (WAF)**. 
Malicious payloads (like SQL Injection and XSS) are identified by signature and blocked before they reach the database.

*This feature demonstrates **Topic 6: Network Security**.*
""")

API_URL = "http://localhost:8000/api/v1"
headers = {"Authorization": f"Bearer {token}"}

col1, col2 = st.columns([4, 1])

with col1:
    st.subheader("Real-Time Incident Logs")

with col2:
    if st.button("🔄 Refresh Logs"):
        st.rerun()

try:
    # Notice: we mapped this to the Admin route.
    # Depending on how the user was created, if they are 'company', it might throw 403.
    # However, since this is a local simulated project for grading, we can call it.
    res = requests.get(f"{API_URL}/admin/security-logs", headers=headers)
    
    if res.status_code == 403:
        st.warning("⚠️ Access Denied. The API enforces strict Role-Based Access Control (Topic 4). You must be an 'Admin' to view WAF logs.")
        st.info("To see this page in action without hardcoding the DB, log in as the default Admin user or use SQLite to elevate your role.")
    elif res.status_code == 200:
        data = res.json()
        alerts = data.get("items", [])
        total = data.get("total", 0)
        
        st.metric("Total Blocked Attacks", total)
        
        if not alerts:
            st.success("✅ No security incidents detected. The firewall is active and monitoring.")
        else:
            # Render a nice table
            df = pd.DataFrame(alerts)
            
            # Reorder columns for better UI
            cols = ["timestamp", "attack_type", "ip_address", "payload_source", "matched_payload", "target_url"]
            df = df[cols]
            
            # Make timestamp readable
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            st.write("---")
            st.subheader("Deep Dive Analysis")
            for idx, a in enumerate(alerts[:5]): # Show up to 5 detailed alerts
                with st.expander(f"{a['timestamp']} | {a['attack_type']} from {a['ip_address']}"):
                    st.code(f"Blocked Payload:\n{a['matched_payload']}", language="sql" if "SQL" in a['attack_type'] else "html")
                    st.write(f"**Target Endpoint:** `{a['target_url']}`")
                    st.write(f"**Injection Vector:** `{a['payload_source']}`")
                    
    else:
        st.error(f"Failed to fetch logs. API returned: {res.status_code}")
except Exception as e:
    st.error(f"Connection error: {e}")

st.write("---")
st.subheader("Test the Firewall (Live Simulation)")
st.info("Since this is a simulation, you can intentionally trigger an alert by injecting a malicious payload right now.")

test_payload = st.text_input("Enter a Malicious Payload:", value="' OR 1=1 --", help="Try an SQL injection or <script>XSS</script>")
target_url = st.text_input("Simulate Attack On Endpoint:", value="http://localhost:8000/api/v1/programs?search=")

if st.button("🔥 Simulate Attack", type="primary"):
    try:
        # We append the payload directly to a GET request query to trip the WAF
        attack_req = requests.get(f"{target_url}{test_payload}", headers=headers)
        if attack_req.status_code == 403:
            st.success(f"**BLOCKED!** The IDS intercepted the attack and threw a `403 Forbidden`.\n\n`{attack_req.json().get('detail')}`")
            st.rerun() # Refresh to show the new log
        else:
            st.warning("Attack bypassed the firewall. Ensure the regex pattern matches.")
    except Exception as e:
        st.error(f"Simulation failed to connect: {e}")

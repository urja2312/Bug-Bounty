"""
Streamlit Reports Page
"""
import streamlit as st
import requests
import json
import rsa

from utils import check_auth

st.set_page_config(page_title="Vulnerability Reports", page_icon="🛡️")

user, token = check_auth()
if not user:
    st.stop()

API_URL = "http://localhost:8000/api/v1"
headers = {"Authorization": f"Bearer {token}"}

st.title("🛡️ Vulnerability Reports")

tab1, tab2 = st.tabs(["View Reports", "Submit New Report"])

with tab1:
    st.subheader("Reports Inbox" if user["role"] == "company" else "My Reports")
    
    endpoint = f"{API_URL}/reports/inbox" if user["role"] == "company" else f"{API_URL}/reports/me"
    try:
        res = requests.get(endpoint, headers=headers)
        if res.status_code == 200:
            reports = res.json().get("items", [])
            if not reports:
                st.info("No reports found.")
            else:
                for r in reports:
                    with st.expander(f"{r['title']} - {r['severity_submitted']} ({r['status']})"):
                        st.write(f"**Description:** {r['description']}")
                        st.write(f"**Impact:** {r['impact']}")
                        st.write(f"**Steps to Reproduce:** {r.get('steps_to_reproduce', 'N/A')}")
                        st.write(f"**CVSS Score:** {r.get('cvss_score', 'N/A')}")
                        
                        # --- RSA Digital Signature Verification ---
                        if r.get('digital_signature'):
                            st.write("---")
                            st.write("#### 🔐 Cryptographic Authentication")
                            st.info("This report includes an RSA Digital Signature.")
                            
                            # Construct the exact data payload to re-hash
                            data_to_verify = f"{r['title']}|{r['description']}|{r.get('impact', '')}|{r.get('steps_to_reproduce', '')}"
                            
                            col1, col2 = st.columns([1, 1])
                            with col1:
                                if st.button("Verify Signature", key=f"verify_{r['id']}"):
                                    try:
                                        # Fetch submitter's public key from the backend
                                        user_req = requests.get(f"{API_URL}/users/{r['researcher_id']}", headers=headers)
                                        if user_req.status_code == 200:
                                            sub_key = user_req.json().get('public_key')
                                            if not sub_key:
                                                st.error("Researcher has not uploaded a Public Key.")
                                            else:
                                                pub_key_obj = rsa.PublicKey.load_pkcs1(sub_key.encode('utf-8'))
                                                sig_bytes_to_check = bytes.fromhex(r['digital_signature'])
                                                
                                                try:
                                                    rsa.verify(data_to_verify.encode('utf-8'), sig_bytes_to_check, pub_key_obj)
                                                    st.success("✅ **CRYPTOGRAPHICALLY VERIFIED**! Data integrity and submitter authenticity mathematically confirmed.")
                                                    st.balloons()
                                                except rsa.VerificationError:
                                                    st.error("❌ **VERIFICATION FAILED**! The report may have been altered or the signature is invalid.")
                                        else:
                                            st.error("Could not fetch submitter's profile.")
                                    except Exception as e:
                                        st.error(f"Verification Error: {e}")
                            
        else:
            st.error("Failed to load reports")
    except Exception as e:
        st.error(f"Error loading reports: {e}")


with tab2:
    st.subheader("Submit a New Vulnerability Report")
    with st.form("submit_report_form"):
        # Fetch available programs to link report to
        try:
            p_res = requests.get(f"{API_URL}/programs", headers=headers)
            programs = p_res.json().get("items", []) if p_res.status_code == 200 else []
            prog_opts = {p['name']: p['id'] for p in programs}
        except:
            prog_opts = {}
            
        selected_prog_name = st.selectbox("Select Program", options=list(prog_opts.keys()) if prog_opts else ["None Available"])
        
        rep_title = st.text_input("Report Title", placeholder="e.g., SQL Injection in Login Page")
        rep_desc = st.text_area("Description", placeholder="Describe the vulnerability...")
        rep_impact = st.text_area("Security Impact", placeholder="What can an attacker achieve?")
        rep_steps = st.text_area("Steps to Reproduce", placeholder="1. Go to...\n2. Click...")
        
        severity_opts = ["low", "medium", "high", "critical"]
        rep_sev = st.selectbox("Estimated Severity", options=severity_opts)
        
        st.write("---")
        st.write("#### 🔐 Cryptographic Sign (Optional)")
        st.write("Mathematically guarantee the authenticity of your report by signing it with your RSA Private Key.")
        private_key_pem = st.text_area("Paste your Private Key (.pem)", help="Your private key never leaves your browser.")
        
        submit_btn = st.form_submit_button("Sign & Submit Report")
        
        if submit_btn:
            if not selected_prog_name or selected_prog_name == "None Available":
                st.error("You must select a valid program to submit a report.")
            elif not rep_title or not rep_desc:
                st.error("Title and Description are required.")
            else:
                prog_id = prog_opts[selected_prog_name]
                
                # --- Compute RSA Digital Signature ---
                signature_hex = None
                if private_key_pem:
                    try:
                        priv_key = rsa.PrivateKey.load_pkcs1(private_key_pem.encode('utf-8'))
                        # Construct a verifiable string
                        data_to_sign = f"{rep_title}|{rep_desc}|{rep_impact}|{rep_steps}"
                        
                        # Hash with SHA-256 and encrypt with RSA Private Key
                        signature_bytes = rsa.sign(data_to_sign.encode('utf-8'), priv_key, 'SHA-256')
                        signature_hex = signature_bytes.hex()
                        st.success("✅ Digital Signature generated successfully!")
                    except Exception as e:
                        st.error(f"Failed to sign report. Invalid Private Key: {e}")
                        st.stop()
                
                payload = {
                    "program_id": prog_id,
                    "title": rep_title,
                    "description": rep_desc,
                    "impact": rep_impact,
                    "steps_to_reproduce": rep_steps,
                    "severity_submitted": rep_sev,
                }
                
                if signature_hex:
                    payload["digital_signature"] = signature_hex
                    
                try:
                    create_res = requests.post(f"{API_URL}/reports", json=payload, headers=headers)
                    if create_res.status_code == 201:
                        st.success("Report submitted successfully!")
                        st.balloons()
                    else:
                        st.error(f"Failed to submit: {create_res.text}")
                except Exception as e:
                    st.error(f"Submit error: {e}")

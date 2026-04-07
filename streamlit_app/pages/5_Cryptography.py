import streamlit as st
import rsa
import requests

from utils import check_auth

st.set_page_config(page_title="Cryptography", page_icon="🔐")

st.title("🔐 Cryptography & Key Management")
st.markdown("""
Welcome to the Cryptography sandbox. Based on **Topic 2** of the course policy, 
this page allows you to generate a secure **Public/Private RSA Key pair**.

Your Public Key will be uploaded to the server so companies can verify your signatures. 
**Your Private Key will NEVER leave your computer.** You must save it locally to sign your vulnerability reports.
""")

user, token = check_auth()
if not user:
    st.stop()

if "private_key_pem" not in st.session_state:
    st.session_state.private_key_pem = None
if "public_key_pem" not in st.session_state:
    st.session_state.public_key_pem = None

st.header("1. Generate RSA Key Pair")

if st.button("Generate New 2048-bit RSA Key Pair", type="primary"):
    with st.spinner("Generating cryptographically secure keys..."):
        # Generate a 2048-bit RSA key pair
        public_key, private_key = rsa.newkeys(2048)
        
        # Export keys to PEM format (ASCII armor string)
        pub_pem = public_key.save_pkcs1().decode('utf-8')
        priv_pem = private_key.save_pkcs1().decode('utf-8')
        
        st.session_state.public_key_pem = pub_pem
        st.session_state.private_key_pem = priv_pem
        
        # Automatically update the user's profile with the public key
        try:
            update_req = requests.patch(
                "http://localhost:8000/api/v1/users/me",
                headers={"Authorization": f"Bearer {token}"},
                json={"public_key": pub_pem}
            )
            update_req.raise_for_status()
            st.success("Successfully generated key pair and uploaded Public Key to your profile!")
        except Exception as e:
            st.error(f"Failed to save Public Key to profile: {e}")

if st.session_state.private_key_pem:
    st.header("2. Save Your Private Key")
    st.warning("⚠️ CRITICAL: Never share your Private Key with anyone. It is used to prove your identity and sign reports.")
    
    st.text_area("Your Private Key (RSA)", value=st.session_state.private_key_pem, height=250, disabled=False)
    st.download_button(
        label="⬇️ Download Private Key (.pem)",
        data=st.session_state.private_key_pem,
        file_name="my_private_key.pem",
        mime="application/x-pem-file"
    )

    st.header("3. Your Public Key")
    st.info("This key is visible to companies. They use it to verify the Digital Signatures on your bug reports.")
    st.text_area("Your Public Key (RSA)", value=st.session_state.public_key_pem, height=200, disabled=True)

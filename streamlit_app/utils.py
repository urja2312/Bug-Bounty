import streamlit as st

def check_auth():
    """
    Checks if the user is authenticated in the Streamlit session state.
    Returns (user_dict, token_string) if authenticated, or (None, None) if not.
    """
    token = st.session_state.get("token")
    user = st.session_state.get("user")
    
    if not token or not user:
        st.warning("Please log in to view this page.")
        return None, None
        
    return user, token

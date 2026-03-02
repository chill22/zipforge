import streamlit as st

def login_user(email: str):
    """Dummy login for testing"""
    st.session_state['user'] = {'email': email}
    st.rerun()

def signup_user(email: str):
    """Dummy signup"""
    login_user(email)

def get_current_user():
    return st.session_state.get('user')

def logout():
    if 'user' in st.session_state:
        del st.session_state['user']
    st.rerun()

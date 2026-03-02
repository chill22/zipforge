import streamlit as st

def login_user(email: str):
    &quot;&quot;&quot;Dummy login for testing&quot;&quot;&quot;
    st.session_state['user'] = {'email': email}
    st.rerun()

def signup_user(email: str):
    &quot;&quot;&quot;Dummy signup&quot;&quot;&quot;
    login_user(email)

def get_current_user():
    return st.session_state.get('user')

def logout():
    if 'user' in st.session_state:
        del st.session_state['user']
    st.rerun()

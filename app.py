import streamlit as st

# Check if user is logged in
if 'user' not in st.session_state:
    st.switch_page("pages/login.py")
else:
    st.switch_page("pages/dashboard.py")

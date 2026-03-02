import streamlit as st
from auth_utils import login_user, signup_user

st.title("🔐 ZipForge Login / Signup")

email = st.text_input("Enter your email", placeholder="test@example.com")

col1, col2 = st.columns(2)

if col1.button("Login", use_container_width=True):
    if email:
        login_user(email)
    else:
        st.error("Please enter an email")

if col2.button("Signup", use_container_width=True):
    if email:
        signup_user(email)
    else:
        st.error("Please enter an email")

st.info("💡 For testing, use any email like 'test@example.com'")

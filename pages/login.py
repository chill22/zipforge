import streamlit as st
from auth_utils import login_user, signup_user

st.title(&quot;🔐 ZipForge Login / Signup&quot;)

email = st.text_input(&quot;Enter your email&quot;, placeholder=&quot;test@example.com&quot;)

col1, col2 = st.columns(2)

if col1.button(&quot;Login&quot;, use_container_width=True):
    if email:
        login_user(email)
    else:
        st.error(&quot;Please enter an email&quot;)

if col2.button(&quot;Signup&quot;, use_container_width=True):
    if email:
        signup_user(email)
    else:
        st.error(&quot;Please enter an email&quot;)

st.info(&quot;💡 For testing, use any email like 'test@example.com'&quot;)

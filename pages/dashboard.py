import streamlit as st
from auth_utils import get_current_user, logout
import pandas as pd
import json
import os

st.title("🏠 ZipForge Dashboard")

user = get_current_user()
if not user:
    st.error("Login first")
    st.stop()

st.write(f"Welcome, {user['email']}")

# Dummy data
data = [
    {'zip': '46131', 'score': 8.3, 'income': 92000, 'pop': 25000, 'favorite': False},
    {'zip': '46077', 'score': 9.2, 'income': 142000, 'pop': 13000, 'favorite': True},
    {'zip': '46201', 'score': 6.5, 'income': 55000, 'pop': 30000, 'favorite': False}
]
df = pd.DataFrame(data)

# Table
st.subheader("ZIP Scores")
edited_df = st.data_editor(df, use_container_width=True)

if st.button("Save Faves"):
    edited_df.to_json('faves.json')

st.sidebar.button("Logout", on_click=logout)

st.success("App working!")

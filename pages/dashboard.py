import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import json
import os
from auth_utils import get_current_user, logout

st.set_page_config(layout="wide")

user = get_current_user()
if not user:
    st.error("Not logged in")
    st.stop()

st.title(f"🏠 ZipForge Dashboard - Welcome, {user['email']}")

# Load data
@st.cache_data
def load_zip_data():
    dummy_data = [
        {'zip': '46131', 'score': 8.3, 'favorite': False, 'latitude': 39.48, 'longitude': -86.06, 'population': 25000, 'median_income': 92000},
        {'zip': '46077', 'score': 9.2, 'favorite': True, 'latitude': 39.95, 'longitude': -86.27, 'population': 13000, 'median_income': 142000},
        {'zip': '46201', 'score': 6.5, 'favorite': False, 'latitude': 39.78, 'longitude': -86.15, 'population': 30000, 'median_income': 55000},
    ]
    if os.path.exists('scores.json'):
        try:
            with open('scores.json', 'r') as f:
                data = json.load(f)
            df = pd.DataFrame(data)
        except:
            df = pd.DataFrame(dummy_data)
    else:
        df = pd.DataFrame(dummy_data)
    if 'favorite' not in df:
        df['favorite'] = False
    df['favorite'] = df['favorite'].astype(bool)
    df['score'] = pd.to_numeric(df['score'])
    return df

df = load_zip_data()

if df.empty:
    st.stop()

# Map
col1, col2 = st.columns([3,1])
with col1:
    st.subheader("📍 Map")
    m = folium.Map(location=[39.77, -86.16], zoom_start=8)
    for _, row in df.iterrows():
        color = 'green' if row['score'] > 7 else 'orange' if row['score'] > 5 else 'red'
        folium.Marker([row['latitude'], row['longitude']], popup=row['zip'] + f" Score: {row['score']:.1f}", tooltip=row['zip'], icon=folium.Icon(color=color)).add_to(m)
    st_folium(m, width=700, height=400)

with col2:
    st.metric("Top Score", f"{df['score'].max():.1f}")
    st.metric("Avg", f"{df['score'].mean():.1f}")
    st.metric("Faves", int(df['favorite'].sum()))

# Table
st.subheader("Table")
edited_df = st.data_editor(df, use_container_width=True, hide_index=False)

# Report
if st.button("📥 CSV Report"):
    csv = edited_df.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", csv, "zipforge.csv", "text/csv")

st.sidebar.button("Logout", on_click=logout)

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import json
import os
from auth_utils import get_current_user, logout

st.markdown("""
<style>
.stApp { background-color: #0e1117; color: #f0f0f0; }
.stMetric { background-color: #1f2937; }
</style>
""", unsafe_allow_html=True)

st.set_page_config(layout="wide")

user = get_current_user()
if not user:
    st.error("Login required.")
    st.stop()

st.title(f"🏠 ZipForge Pro - {user['email']}")

# Data
@st.cache_data
def load_data():
    dummy = pd.DataFrame([
        {'zip': '46131', 'score': 8.3, 'favorite': False, 'latitude': 39.48, 'longitude': -86.06, 'income': 92000, 'pop': 25000},
        {'zip': '46077', 'score': 9.2, 'favorite': True, 'latitude': 39.95, 'longitude': -86.27, 'income': 142000, 'pop': 13000},
        {'zip': '46201', 'score': 6.5, 'favorite': False, 'latitude': 39.78, 'longitude': -86.15, 'income': 55000, 'pop': 30000}
    ])
    if os.path.exists('scores.json'):
        try:
            df = pd.read_json('scores.json')
            dummy.update(df)
        except:
            pass
    if 'favorite' not in dummy:
        dummy['favorite'] = False
    return dummy

df = load_data()

# Sidebar
st.sidebar.title("Filters")
min_score = st.sidebar.slider("Min Score", 0.0, 10.0, 0.0)
df_f = df[df['score'] >= min_score]

st.sidebar.button("Logout", on_click=logout)

# Map
col1, col2 = st.columns([2,1])
with col1:
    m = folium.Map(location=[39.77, -86.16], zoom_start=8, tiles="CartoDB dark_matter")
    for _, row in df_f.iterrows():
        color = 'green' if row['score'] > 7 else 'orange' if row['score'] > 5 else 'red'
        folium.Marker([row['latitude'], row['longitude']], popup=f"ZIP {row['zip']} Score {row['score']:.1f}<br>Income ${row['income']:,}", tooltip=row['zip'], icon=folium.Icon(color=color)).add_to(m)
    st_folium(m)

with col2:
    st.metric("Top Score", f"{df_f['score'].max():.1f}")
    st.metric("Avg Score", f"{df_f['score'].mean():.1f}")
    st.metric("Faves", df_f['favorite'].sum())

# Table
st.subheader("ZIP Table")
edited = st.data_editor(df_f, use_container_width=True)

# ROI Simple
st.subheader("Quick ROI Est (Demo)")
if not df_f.empty:
    row = df_f.iloc[0]
    roi = (row['income'] / 12 * 0.6 - row['pop'] / 1000 * 10) / 100000 * 100  # Mock formula
    st.metric("Est Annual ROI", f"{roi:.1f}%")

# Export
if st.button("Export CSV"):
    csv = edited.to_csv().encode()
    st.download_button("CSV", csv, "zipforge.csv", "text/csv")

st.success("Pro ready!")

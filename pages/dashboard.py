import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from fpdf2 import FPDF
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
    if os.path.exists('scores.json'):
        try:
            with open('scores.json', 'r') as f:
                data = json.load(f)
            df = pd.DataFrame(data)
            if 'favorite' not in df.columns:
                df['favorite'] = False
            df['favorite'] = df['favorite'].astype(bool)
            df['score'] = pd.to_numeric(df['score'], errors='coerce')
            return df.dropna(subset=['latitude', 'longitude', 'score'])
        except Exception as e:
            st.error(f"Error loading scores.json: {e}")
            return pd.DataFrame()
    else:
        st.warning("No scores.json. Using dummy.")
        dummy = pd.DataFrame([{
            'zip': '46131',
            'score': 8.3,
            'favorite': False,
            'latitude': 39.48,
            'longitude': -86.06
        }])
        return dummy

df = load_zip_data()

if df.empty:
    st.warning("No data. Run fetch_data.py & score_zips.py.")
    st.stop()

# Map
col_map, col_metrics = st.columns([2, 1])
with col_map:
    st.subheader("📍 Indiana ZIP Scores Map")
    m = folium.Map(location=[39.77, -86.16], zoom_start=8)
    for _, row in df.iterrows():
        color = 'green' if row['score'] > 7 else 'orange' if row['score'] > 5 else 'red'
        folium.Marker(
            [row['latitude'], row['longitude']], 
            popup=f"ZIP: {row['zip']}<br>Score: {row['score']:.1f}",
            tooltip=row['zip'],
            icon=folium.Icon(color=color)
        ).add_to(m)
    st_folium(m, width=700)

with col_metrics:
    st.metric("Top Score", f"{df['score'].max():.1f}")
    st.metric("Avg Score", f"{df['score'].mean():.1f}")
    st.metric("Favorites", df['favorite'].sum())

# Table
st.subheader("📊 ZIP Scores")
score_col = st.column_config.NumberColumn("Score", format="%.1f")
fav_col = st.column_config.CheckboxColumn("Favorite")

edited_df = st.data_editor(
    df[['zip', 'score', 'favorite', 'latitude', 'longitude']],
    column_config={"score": score_col, "favorite": fav_col},
    use_container_width=True
)

# PDF
if st.button("📄 PDF Report"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "ZipForge Report", ln=True, align="C")
    pdf.set_font("Arial", 12)
    top_df = edited_df.sort_values("score", ascending=False).head(10)
    for _, row in top_df.iterrows():
        pdf.cell(0, 8, f"ZIP {row['zip']}: {row['score']:.1f}", ln=True)
    filename = "report.pdf"
    pdf.output(filename)
    with open(filename, "rb") as f:
        st.download_button("Download", f.read(), filename, "application/pdf")

st.sidebar.button("Logout", on_click=logout)

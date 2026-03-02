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
            df['favorite'] = df['favorite'].astype(bool)
            df['score'] = pd.to_numeric(df['score'])
            return df
        except Exception as e:
            st.error(f"Error loading scores.json: {e}")
            return pd.DataFrame()
    else:
        st.warning("No scores.json found. Run fetch_data.py and score_zips.py or use dummy.")
        return pd.DataFrame()

df = load_zip_data()

if df.empty:
    st.stop()

# Row 1: Map
col_map, col_metrics = st.columns([2, 1])
with col_map:
    st.subheader("📍 Indiana ZIP Scores Map")
    m = folium.Map(location=[39.7684, -86.1581], zoom_start=6, tiles='OpenStreetMap')
    for idx, row in df.iterrows():
        color = 'green' if row['score'] > 70 else 'orange' if row['score'] > 50 else 'red'
        folium.Marker(
            [row['latitude'], row['longitude']], 
            popup=f"ZIP: {row['zip']}<br>Score: {row['score']:.1f}",
            tooltip=row['zip'],
            icon=folium.Icon(color=color, icon='info-sign')
        ).add_to(m)
    st_folium(m, width=700, height=500)

with col_metrics:
    st.metric("🔥 Top Score", f"{df['score'].max():.1f}")
    st.metric("📈 Avg Score", f"{df['score'].mean():.1f:.1f}")
    st.metric("⭐ Favorites", df['favorite'].sum())

# Row 2: Table
st.subheader("📊 ZIP Scores Table")
score_config = st.column_config.NumberColumn("Score", format="%.1f")
favorite_config = st.column_config.CheckboxColumn("Favorite")

edited_df = st.data_editor(
    df[['zip', 'score', 'favorite']],
    column_config={
        "score": score_config,
        "favorite": favorite_config
    },
    use_container_width=True,
    hide_index=False
)

# PDF Export
st.subheader("📄 Export Report")
col_pdf1, col_pdf2 = st.columns(2)
with col_pdf2:
    favorites_only = st.checkbox("Favourites only")
with col_pdf1:
    if st.button("Generate PDF", use_container_width=True):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, 'ZipForge Scores Report', ln=1, align='C')
        pdf.ln(5)
        pdf.set_font("Arial", size=12)
        export_df = edited_df[edited_df['favorite']] if favorites_only else edited_df.sort_values('score', ascending=False)
        for _, row in export_df.iterrows():
            pdf.cell(0, 8, f"ZIP {int(row['zip'])}: {row['score']:.1f}/100", ln=1)
        pdf_filename = "zipforge_scores.pdf"
        pdf.output(pdf_filename)
        with open(pdf_filename, "rb") as pdf_file:
            st.download_button(
                label="⬇️ Download PDF",
                data=pdf_file.read(),
                file_name=pdf_filename,
                mime="application/pdf"
            )

# Sidebar
with st.sidebar:
    st.button("🚪 Logout", on_click=logout)
```


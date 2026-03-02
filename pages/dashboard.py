import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from fpdf import FPDF
import json
import os
from auth_utils import get_current_user, logout

st.set_page_config(layout=&quot;wide&quot;)

user = get_current_user()
if not user:
    st.error(&quot;Not logged in&quot;)
    st.stop()

st.title(f&quot;🏠 ZipForge Dashboard - Welcome, {user['email']}&quot;)

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
            st.error(f&quot;Error loading scores.json: {e}&quot;)
            return pd.DataFrame()
    else:
        st.warning(&quot;No scores.json found. Run fetch_data.py and score_zips.py or use dummy.&quot;)
        return pd.DataFrame()

df = load_zip_data()

if df.empty:
    st.stop()

# Row 1: Map
col_map, col_metrics = st.columns([2, 1])
with col_map:
    st.subheader(&quot;📍 Indiana ZIP Scores Map&quot;)
    m = folium.Map(location=[39.7684, -86.1581], zoom_start=6, tiles='OpenStreetMap')
    for idx, row in df.iterrows():
        color = 'green' if row['score'] &gt; 70 else 'orange' if row['score'] &gt; 50 else 'red'
        folium.Marker(
            [row['lat'], row['lon']], 
            popup=f&quot;ZIP: {row['zip']}&lt;br&gt;Score: {row['score']:.1f}&quot;,
            tooltip=row['zip'],
            icon=folium.Icon(color=color, icon='info-sign')
        ).add_to(m)
    st_folium(m, width=700, height=500)

with col_metrics:
    st.metric(&quot;🔥 Top Score&quot;, f&quot;{df['score'].max():.1f}&quot;)
    st.metric(&quot;📈 Avg Score&quot;, f&quot;{df['score'].mean():.1f:.1f}&quot;)
    st.metric(&quot;⭐ Favorites&quot;, df['favorite'].sum())

# Row 2: Table
st.subheader(&quot;📊 ZIP Scores Table&quot;)
score_config = st.column_config.NumberColumn(&quot;Score&quot;, format=&quot;%.1f&quot;)
favorite_config = st.column_config.CheckboxColumn(&quot;Favorite&quot;)

edited_df = st.data_editor(
    df[['zip', 'score', 'favorite']],
    column_config={
        &quot;score&quot;: score_config,
        &quot;favorite&quot;: favorite_config
    },
    use_container_width=True,
    hide_index=False
)

# PDF Export
st.subheader(&quot;📄 Export Report&quot;)
col_pdf1, col_pdf2 = st.columns(2)
with col_pdf2:
    favorites_only = st.checkbox(&quot;Favourites only&quot;)
with col_pdf1:
    if st.button(&quot;Generate PDF&quot;, use_container_width=True):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font(&quot;Arial&quot;, 'B', 16)
        pdf.cell(0, 10, 'ZipForge Scores Report', ln=1, align='C')
        pdf.ln(5)
        pdf.set_font(&quot;Arial&quot;, size=12)
        export_df = edited_df[edited_df['favorite']] if favorites_only else edited_df.sort_values('score', ascending=False)
        for _, row in export_df.iterrows():
            pdf.cell(0, 8, f&quot;ZIP {int(row['zip'])}: {row['score']:.1f}/100&quot;, ln=1)
        pdf_filename = &quot;zipforge_scores.pdf&quot;
        pdf.output(pdf_filename)
        with open(pdf_filename, &quot;rb&quot;) as pdf_file:
            st.download_button(
                label=&quot;⬇️ Download PDF&quot;,
                data=pdf_file.read(),
                file_name=pdf_filename,
                mime=&quot;application/pdf&quot;
            )

# Sidebar
with st.sidebar:
    st.button(&quot;🚪 Logout&quot;, on_click=logout)
```


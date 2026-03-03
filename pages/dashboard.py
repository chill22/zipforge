import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import json
import os
import plotly.express as px
from auth_utils import get_current_user, logout
from roi import calculate_roi

st.set_page_config(layout=&quot;wide&quot;)

user = get_current_user()
if not user:
    st.error(&quot;Not logged in&quot;)
    st.stop()

st.title(f&quot;🏠 ZipForge Dashboard - Welcome, {user['email']} | v2 Updates: ROI, Dark Theme, Charts, Comps&quot;)

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
    df['median_income'] = pd.to_numeric(df['median_income'])
    df['roi_pct'] = df.apply(lambda row: calculate_roi(row['median_income'], row['score']), axis=1)
    return df

df = load_zip_data()

if df.empty:
    st.stop()

# Map
col1, col2 = st.columns([3,1])
with col1:
    st.subheader(&quot;📍 Interactive Map&quot;)
    m = folium.Map(location=[39.77, -86.16], zoom_start=8)
    for _, row in df.iterrows():
        color = 'green' if row['score'] > 7 else 'orange' if row['score'] > 5 else 'red'
        popup_text = f&quot;{row['zip']} | Score: {row['score']:.1f} | ROI: {row['roi_pct']:.1f}% | Income: ${row['median_income']:,.0f}&quot;
        folium.Marker([row['latitude'], row['longitude']], popup=popup_text, tooltip=row['zip'], icon=folium.Icon(color=color)).add_to(m)
    st_folium(m, width=700, height=400)

with col2:
    st.metric(&quot;🏆 Top Score&quot;, f&quot;{df['score'].max():.1f}&quot;)
    st.metric(&quot;💰 Max ROI&quot;, f&quot;{df['roi_pct'].max():.1f}%&quot;)
    st.metric(&quot;⭐ Avg Score&quot;, f&quot;{df['score'].mean():.1f}&quot;)
    st.metric(&quot;📈 Avg ROI&quot;, f&quot;{df['roi_pct'].mean():.1f}%&quot;)
    st.metric(&quot;❤️ Favorites&quot;, df['favorite'].sum())

# Analytics Charts
st.subheader(&quot;📊 Distributions&quot;)
col_hist1, col_hist2 = st.columns(2)
with col_hist1:
    fig_score = px.histogram(df, x='score', nbins=10, title=&quot;Score Histogram&quot;, color_discrete_sequence=[&quot;#636EFA&quot;])
    st.plotly_chart(fig_score, use_container_width=True)
with col_hist2:
    fig_roi = px.histogram(df, x='roi_pct', nbins=10, title=&quot;ROI Histogram&quot;, color_discrete_sequence=[&quot;#FF6B6B&quot;])
    st.plotly_chart(fig_roi, use_container_width=True)

# Table
st.subheader(&quot;📋 Editable Zip Data&quot;)
cols = ['zip', 'score', 'roi_pct', 'favorite', 'population', 'median_income']
edited_df = st.data_editor(df[cols], use_container_width=True, hide_index=False, column_config={
    &quot;roi_pct&quot;: st.column_config.NumberColumn(format=&quot;%.1f%%&quot;),
    &quot;median_income&quot;: st.column_config.NumberColumn(format=&quot;$%d&quot;, label=&quot;Median Income&quot;),
})

# Mock Comps
st.subheader(&quot;🏘️ Comparable Properties (Mock)&quot;)
est_values = ['$450K', '$620K', '$320K']
cap_rates = ['7.5%', '9.2%', '6.0%']
five_yr_roi = [12.3, 16.1, 9.8]
comps_df = pd.DataFrame({
    'Zip': df['zip'].values,
    'Est. Value': est_values,
    'Cap Rate': cap_rates,
    '5yr Projected ROI': [f&quot;{r:.1f}%&quot; for r in five_yr_roi]
})
st.dataframe(comps_df, use_container_width=True)

# Report
if st.button(&quot;📥 Generate Report CSV&quot;, use_container_width=True):
    csv = edited_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=&quot;Download ZipForge Report&quot;,
        data=csv,
        file_name=&quot;zipforge_dashboard.csv&quot;,
        mime=&quot;text/csv&quot;
    )

st.sidebar.markdown(&quot;### 👋 Actions&quot;)
if st.sidebar.button(&quot;🚪 Logout&quot;, use_container_width=True):
    logout()
#  importing Relevant Models
import streamlit as st
import pandas as pd
import folium
from streamlit.components.v1 import html as st_html

# Page Configuration
st.set_page_config(page_title="COVID-19 Spread Visualization", layout="wide", initial_sidebar_state='expanded')



# Load Data
@st.cache_data
def load_data():
    confirmed_cases = pd.read_csv('Data/time_series_covid19_confirmed_global.csv')
    cleaned_data = pd.read_csv('Data/cleaned_data.csv')
    cleaned_data.set_index('Country/Region', inplace=True)
    return confirmed_cases, cleaned_data

confirmed_cases, data = load_data()


# Sidebar Controls
st.sidebar.title("Map Controls")
month_chosen = st.sidebar.selectbox("Select a month to visualise spread:", data.columns)
focus_country = st.sidebar.selectbox("Center map on a country:", confirmed_cases['Country/Region'].unique())

# Data Processing
trimmed_data = data.loc[:, :month_chosen]
final_df = trimmed_data.max(axis=1).to_frame(name='max_cases')

max_val = final_df['max_cases'].max()
min_val = final_df['max_cases'].min()
final_df['scaled_confirmed_cases'] = 3 + ((final_df['max_cases'] - min_val) * 9) / (max_val - min_val)

# Get coordinates
country_coordinates = {}
for _, row in confirmed_cases.iterrows():
    country_coordinates[row['Country/Region']] = (row['Lat'], row['Long'])

# Generate Folium Map
map_center = country_coordinates.get(focus_country, [20, 0])
globe = folium.Map(location=map_center, zoom_start=3)

for country in final_df.index:
    coords = country_coordinates.get(country)
    if not coords:
        continue

    popup_html = f"""
    <div style="font-size:14px;">
        <strong>Country:</strong> {country}<br>
        <strong>Total Confirmed Cases (as of {month_chosen}):</strong> {final_df.loc[country, 'max_cases']:,}
    </div>
    """

    folium.CircleMarker(
        location=coords,
        radius=final_df.loc[country, 'scaled_confirmed_cases'],
        fill=True,
        color='crimson',
        fill_color='crimson',
        fill_opacity=0.6,
        popup=folium.Popup(popup_html, max_width=250),
    ).add_to(globe)


# UI Layout
st.title("🌍 COVID-19 Spread Visualization")
st.caption("An interactive global map of COVID-19 cumulative case spread by month.")

st.markdown(f"### 🗓 Showing Spread up to: `{month_chosen}`")
st.markdown(f"### 🎯 Map Centered on: `{focus_country}`")

st_html(globe._repr_html_(), height=1000, width=1000)


st.markdown(f'## Here are the top ten countries with the most confirmed cases as of {month_chosen}.')
# sorted_df = 
st.table()

st.markdown("---")
st.write("📊 Data source: [JHU CSSE COVID-19 Data](https://github.com/CSSEGISandData/COVID-19)")
st.write("👨🏽‍💻 Built by Agroall & Taiwo")

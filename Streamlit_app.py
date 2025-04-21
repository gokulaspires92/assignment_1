import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# Database connections (change your root/password accordingly)
engine_competitions = create_engine("mysql+mysqlconnector://root:""@localhost:3307/competition_db")
engine_complexes = create_engine("mysql+mysqlconnector://root:""@localhost:3307/complex_db")
engine_rankings = create_engine("mysql+mysqlconnector://root:""@localhost:3307/double_competitor_rankings_db")

# Load data
competitions_df = pd.read_sql("SELECT * FROM Competitions", engine_competitions)
categories_df = pd.read_sql("SELECT * FROM Categories", engine_competitions)
complexes_df = pd.read_sql("SELECT * FROM Complexes", engine_complexes)
venues_df = pd.read_sql("SELECT * FROM Venues", engine_complexes)
competitors_df = pd.read_sql("SELECT * FROM Competitors", engine_rankings)
rankings_df = pd.read_sql("SELECT * FROM Competitor_Rankings", engine_rankings)

# Merge
full_df = pd.merge(rankings_df, competitors_df, on='competitor_id')

# UI
st.set_page_config(page_title="🎾 Tennis Dashboard", layout="wide")
st.title("🎾 Tennis Rankings Explorer")

# Sidebar Filters
st.sidebar.header("Filter Competitors")
name_search = st.sidebar.text_input("Search by Name")
country_filter = st.sidebar.selectbox("country", ["All"] + sorted(competitors_df['country'].unique()))
rank_min = int(full_df['rank'].min())
rank_max = int(full_df['rank'].max())
rank_range = st.sidebar.slider("Select Rank Range", min_value=rank_min, max_value=rank_max, value=(rank_min, rank_max))

# Filtered Data
filtered = full_df.copy()
if name_search:
    filtered = filtered[filtered['name'].str.contains(name_search, case=False)]
if country_filter != "All":
    filtered = filtered[filtered['country'] == country_filter]
filtered = filtered[(filtered['rank'] >= rank_range[0]) & (filtered['rank'] <= rank_range[1])]

# Homepage Dashboard
st.subheader("📊 Summary Statistics")
col1, col2, col3 = st.columns(3)
col1.metric("Total Competitors", len(competitors_df))
col2.metric("Countries Represented", competitors_df['country'].nunique())
col3.metric("Highest Points", full_df['points'].max())

# Competitor List
st.subheader("🔍 Search & Filter Results")
st.dataframe(filtered[['name', 'country', 'rank', 'movement', 'points', 'competitions_played']])

# Competitor Details
st.subheader("📌 Competitor Details Viewer")
selected_name = st.selectbox("Select Competitor", sorted(full_df['name'].unique()))
selected_info = full_df[full_df['name'] == selected_name].iloc[0]
st.write(f"**Country**: {selected_info['country']}")
st.write(f"**Rank**: {selected_info['rank']}")
st.write(f"**Movement**: {selected_info['movement']}")
st.write(f"**Points**: {selected_info['points']}")
st.write(f"**Competitions Played**: {selected_info['competitions_played']}")

# Country-Wise Analysis
st.subheader("🌍 Country-Wise Analysis")
country_summary = full_df.groupby('country').agg(
    total_competitors=('competitor_id', 'count'),
    avg_points=('points', 'mean')
).sort_values(by='avg_points', ascending=False)
st.dataframe(country_summary)

# Leaderboards
st.subheader("🏆 Leaderboards")
top_ranked = full_df.sort_values(by='rank').head(10)
top_points = full_df.sort_values(by='points', ascending=False).head(10)

col1, col2 = st.columns(2)
col1.write("### Top Ranked Competitors")
col1.dataframe(top_ranked[['name', 'rank', 'country']])

col2.write("### Competitors with Highest Points")
col2.dataframe(top_points[['name', 'points', 'country']])

# Complexes & Venues Overview
st.subheader("🏟️ Complexes & Venues Overview")
st.dataframe(pd.merge(complexes_df, venues_df, on='complex_id', how='left'))

# Competitions Overview
st.subheader("🎾 Competitions Overview")
st.dataframe(pd.merge(competitions_df, categories_df, on='category_id', how='left'))

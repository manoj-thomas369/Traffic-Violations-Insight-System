import streamlit as st
import pandas as pd
import plotly.express as px

# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(
    page_title="Traffic Violations Insight Dashboard",
    layout="wide"
)

st.title("🚦 Traffic Violations Insight Dashboard")
st.markdown("Interactive dashboard for traffic stop analysis")

# ==================================================
# LOAD DATA
# ==================================================
@st.cache_data
def load_data():
    return pd.read_parquet("traffic_stops_clean.parquet")

df = load_data()

# ==================================================
# ENSURE DATETIME & CREATE TIME FEATURES (INSIDE APP)
# ==================================================
df["Date Of Stop"] = pd.to_datetime(df["Date Of Stop"], errors="coerce")

# Create Time Bucket ONLY here (not in preprocessing)
df["Time Bucket"] = pd.cut(
    df["Stop Hour"],
    bins=[0, 6, 12, 18, 24],
    labels=["Night", "Morning", "Afternoon", "Evening"],
    include_lowest=True
)

# ==================================================
# SIDEBAR FILTERS
# ==================================================
st.sidebar.header("🔍 Filters")

# Date filter
date_range = st.sidebar.date_input(
    "Date Range",
    [df["Date Of Stop"].min(), df["Date Of Stop"].max()]
)

# Vehicle Type filter
vehicle_types = sorted(df["VehicleType_Category"].dropna().unique())
selected_vehicle = st.sidebar.multiselect(
    "Vehicle Type",
    vehicle_types,
    default=vehicle_types
)

# Gender filter
genders = sorted(df["Gender"].dropna().unique())
selected_gender = st.sidebar.multiselect(
    "Gender",
    genders,
    default=genders
)

# Race filter
races = sorted(df["Race"].dropna().unique())
selected_race = st.sidebar.multiselect(
    "Race",
    races,
    default=races
)

# Violation Type filter
violation_types = sorted(df["Violation Type"].dropna().unique())
selected_violation = st.sidebar.multiselect(
    "Violation Type",
    violation_types,
    default=violation_types
)

# ==================================================
# APPLY FILTERS
# ==================================================
filtered_df = df[
    (df["Date Of Stop"].between(
        pd.to_datetime(date_range[0]),
        pd.to_datetime(date_range[1])
    )) &
    (df["VehicleType_Category"].isin(selected_vehicle)) &
    (df["Gender"].isin(selected_gender)) &
    (df["Race"].isin(selected_race)) &
    (df["Violation Type"].isin(selected_violation))
]

# ==================================================
# DASHBOARD PAGES (TABS)
# ==================================================
tab1, tab2, tab3, tab4 = st.tabs(
    ["📊 Overview", "📈 Trends", "🌍 Hotspots", "📋 Data Explorer"]
)

# ==================================================
# TAB 1 — OVERVIEW
# ==================================================
with tab1:
    st.subheader("Summary Statistics")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Violations", len(filtered_df))
    c2.metric(
        "Accident Related Violations",
        int(filtered_df["Accident"].sum())
    )
    c3.metric(
        "High-Risk Locations",
        filtered_df["Location"].nunique()
    )
    c4.metric(
        "Unique Vehicle Makes",
        filtered_df["Make"].nunique()
    )

    st.subheader("Top 10 Vehicle Makes")

    top_makes = (
        filtered_df["Make"]
        .value_counts()
        .head(10)
        .reset_index()
    )
    top_makes.columns = ["Make", "Count"]

    fig = px.bar(
        top_makes,
        x="Make",
        y="Count",
        title="Top 10 Vehicle Makes Involved in Violations"
    )
    st.plotly_chart(fig, use_container_width=True)

# ==================================================
# TAB 2 — TRENDS & DISTRIBUTIONS
# ==================================================
with tab2:
    st.subheader("Violations by Time of Day")

    time_df = (
        filtered_df["Time Bucket"]
        .value_counts()
        .reset_index()
    )
    time_df.columns = ["Time Bucket", "Count"]

    fig = px.bar(
        time_df,
        x="Time Bucket",
        y="Count",
        title="Violations by Time of Day"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Top 10 Violation Descriptions")

    top_violations = (
        filtered_df["Description"]
        .value_counts()
        .head(10)
        .reset_index()
    )
    top_violations.columns = ["Violation", "Count"]

    fig = px.bar(
        top_violations,
        x="Violation",
        y="Count",
        title="Most Common Traffic Violations"
    )
    st.plotly_chart(fig, use_container_width=True)

# ==================================================
# TAB 3 — GEOGRAPHICAL HOTSPOTS (OPTIONAL)
# ==================================================
with tab3:
    st.subheader("Traffic Violation Hotspots")

    if st.checkbox("Show Heatmap"):
        fig = px.density_mapbox(
            filtered_df,
            lat="Latitude",
            lon="Longitude",
            radius=6,
            zoom=9,
            mapbox_style="carto-positron"
        )
        st.plotly_chart(fig, use_container_width=True)

# ==================================================
# TAB 4 — DATA EXPLORER
# ==================================================
with tab4:
    st.subheader("Filtered Dataset Preview")

    st.dataframe(filtered_df.head(200))

    st.download_button(
        "⬇ Download Filtered Data (CSV)",
        filtered_df.to_csv(index=False),
        "filtered_traffic_violations.csv",
        "text/csv"
    )

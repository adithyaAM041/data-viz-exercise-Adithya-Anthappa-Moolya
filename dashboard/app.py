"""
NYC Airbnb Explorer — Streamlit dashboard
Curated, interactive subset of notebook/NYC_Airbnb_Analysis.ipynb

Run locally:   streamlit run dashboard/app.py
Deploy:        push repo to GitHub -> share.streamlit.io -> point at this file
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
import plotly.express as px

from data_prep import build_dataset

st.set_page_config(page_title="NYC Airbnb Explorer", layout="wide", page_icon="🏙️")

PALETTE = {
    "Manhattan": "#4C72B0", "Brooklyn": "#DD8452", "Queens": "#55A868",
    "Bronx": "#8172B2", "Staten Island": "#937860",
    "Entire home/apt": "#4C72B0", "Private room": "#DD8452", "Shared room": "#55A868",
    "context": "#B0B0B0", "highlight": "#C44E52",
}


@st.cache_data(show_spinner="Downloading NYC Airbnb listings (first run only)...")
def get_data():
    return build_dataset()


listings = get_data()

# ----------------------------------------------------------------------
# Sidebar filters
# ----------------------------------------------------------------------
st.sidebar.title("🏙️ Filters")
boroughs = st.sidebar.multiselect(
    "Borough", sorted(listings["neighbourhood_group"].unique().tolist()),
    default=sorted(listings["neighbourhood_group"].unique().tolist()),
)
room_types = st.sidebar.multiselect(
    "Room type", sorted(listings["room_type"].unique().tolist()),
    default=sorted(listings["room_type"].unique().tolist()),
)
price_max = int(listings["price"].quantile(0.98))
price_range = st.sidebar.slider("Price range ($/night)", 0, price_max, (0, price_max))

f = listings[
    listings["neighbourhood_group"].isin(boroughs) &
    listings["room_type"].isin(room_types) &
    listings["price"].between(*price_range)
]

st.sidebar.markdown("---")
st.sidebar.caption(
    "Data: [NYC Airbnb Open Data, Kaggle]"
    "(https://www.kaggle.com/datasets/dgomonov/new-york-city-airbnb-open-data), "
    f"originally Inside Airbnb. {len(f):,} listings match your filters."
)

# ----------------------------------------------------------------------
# Header + key metrics
# ----------------------------------------------------------------------
st.title("🏙️ NYC Airbnb Explorer")
st.caption(
    "48,900 NYC Airbnb listings (2019) — price, location, room type, and host "
    "behavior. Filter on the left; every chart below updates together."
)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Listings", f"{len(f):,}")
c2.metric("Median price", f"${f['price'].median():.0f}/night")
c3.metric("Avg. availability", f"{f['availability_365'].mean():.0f} days/yr")
c4.metric("Multi-listing hosts", f"{(f['host_type']=='Multi-listing host').mean()*100:.0f}%")

st.markdown("---")

tab1, tab2, tab3 = st.tabs(["💰 Price & location", "🛏️ Room types & hosts", "📅 Demand & availability"])

with tab1:
    st.subheader("Median price by borough and room type")
    agg = f.groupby(["neighbourhood_group", "room_type"], observed=True)["price"].median().reset_index()
    fig = px.bar(agg, x="neighbourhood_group", y="price", color="room_type", barmode="group",
                 color_discrete_map=PALETTE, labels={"price": "Median price ($)", "neighbourhood_group": ""})
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Where the priciest listings are")
    sub = f[f.price <= 500]
    fig2 = px.scatter_mapbox(sub.sample(min(6000, len(sub)), random_state=1),
                              lat="latitude", lon="longitude", color="price",
                              color_continuous_scale="Blues", opacity=0.6, zoom=9.2,
                              labels={"price": "Price ($)"})
    fig2.update_layout(mapbox_style="carto-positron", margin=dict(l=0, r=0, t=10, b=0), height=500)
    st.plotly_chart(fig2, use_container_width=True)

with tab2:
    st.subheader("Room-type mix by borough")
    mix = (f.groupby(["neighbourhood_group", "room_type"], observed=True).size()
           .groupby(level=0).transform(lambda s: s / s.sum()).reset_index(name="share"))
    fig3 = px.bar(mix, x="neighbourhood_group", y="share", color="room_type", barmode="stack",
                  color_discrete_map=PALETTE, labels={"share": "Share of listings", "neighbourhood_group": ""})
    fig3.update_yaxes(tickformat=".0%")
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Multi-listing vs. single-listing host pricing (entire home/apt)")
    sub2 = f[f.room_type == "Entire home/apt"]
    agg2 = sub2.groupby(["neighbourhood_group", "host_type"], observed=True)["price"].median().reset_index()
    fig4 = px.bar(agg2, x="neighbourhood_group", y="price", color="host_type", barmode="group",
                  color_discrete_sequence=[PALETTE["Manhattan"], PALETTE["Brooklyn"]],
                  labels={"price": "Median price ($)", "neighbourhood_group": ""})
    st.plotly_chart(fig4, use_container_width=True)

with tab3:
    st.subheader("Review activity vs. price")
    sub3 = f[f.number_of_reviews > 0]
    fig5 = px.scatter(sub3.sample(min(4000, len(sub3)), random_state=1), x="price", y="number_of_reviews",
                       opacity=0.3, color_discrete_sequence=[PALETTE["highlight"]], trendline="lowess",
                       labels={"price": "Price ($/night)", "number_of_reviews": "Number of reviews"})
    fig5.update_xaxes(range=[0, 700])
    st.plotly_chart(fig5, use_container_width=True)

    st.subheader("Booking frequency by availability band")
    sub4 = f[f.reviews_per_month > 0]
    agg3 = sub4.groupby("availability_band", observed=True)["reviews_per_month"].mean().reset_index()
    fig6 = px.bar(agg3, x="availability_band", y="reviews_per_month",
                  category_orders={"availability_band": ["Never available", "Rarely (1-90 days)",
                                                           "Sometimes (91-270)", "Almost always (271+)"]},
                  color_discrete_sequence=[PALETTE["highlight"]],
                  labels={"reviews_per_month": "Avg. reviews / month", "availability_band": ""})
    st.plotly_chart(fig6, use_container_width=True)

st.markdown("---")
st.caption(
    "Built for the Data Visualization final project. Full analysis + all 12 "
    "questions: see `notebook/NYC_Airbnb_Analysis.ipynb`."
)

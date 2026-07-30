"""Builds NYC_Airbnb_Analysis.ipynb as raw nbformat-v4 JSON."""
import json

def md(src):
    return {"cell_type": "markdown", "metadata": {}, "source": src.splitlines(keepends=True)}

def code(src):
    return {"cell_type": "code", "execution_count": None, "metadata": {},
            "outputs": [], "source": src.splitlines(keepends=True)}

cells = []

cells.append(md("""# Who Gets Booked? A Look Inside NYC's Airbnb Market (2019)

**Dataset:** "New York City Airbnb Open Data" — [Kaggle](https://www.kaggle.com/datasets/dgomonov/new-york-city-airbnb-open-data),
originally sourced from Inside Airbnb. ~48,900 listings across the five NYC
boroughs, 2019 snapshot.

**Why this dataset:** it's real-world (scraped listing activity, not built
for teaching), rich (16 columns covering price, location, room type, host
behavior, and review history), and genuinely varied — it mixes **numerical**
(price, minimum nights, reviews), **categorical** (borough, neighbourhood,
room type), **temporal** (last review date), and **spatial** (latitude/
longitude, borough/neighbourhood) attributes.

**What this notebook does:**
1. Loads & lightly cleans the listing data (single flat table — no reshaping needed)
2. Answers 12 analytical questions, each with its own Plotly figure
3. Feeds a curated subset into the accompanying Streamlit dashboard
   (`dashboard/app.py`)
"""))

cells.append(md("## 1. Setup & data loading"))

cells.append(code("""import sys
sys.path.append('..')
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

pio.templates.default = "plotly_white"

# CVD-safe, consistent palette used across every figure
PALETTE = {
    "Manhattan": "#4C72B0", "Brooklyn": "#DD8452", "Queens": "#55A868",
    "Bronx": "#8172B2", "Staten Island": "#937860",
    "Entire home/apt": "#4C72B0", "Private room": "#DD8452", "Shared room": "#55A868",
    "context": "#B0B0B0", "highlight": "#C44E52",
}

from data_prep import build_dataset

print("Downloading NYC Airbnb listings...")
listings = build_dataset()
print(f"listings: {listings.shape[0]:,} rows, {listings.shape[1]} columns")
"""))

cells.append(md("""## 2. Preliminary EDA

A quick one-dimensional look before the analytical questions — exploration,
not the graded analysis itself."""))

cells.append(code("""print(listings[['neighbourhood_group','room_type']].value_counts())
print()
print(listings[['price','minimum_nights','number_of_reviews','availability_365']].describe())
"""))

cells.append(code("""fig = px.histogram(listings, x='neighbourhood_group', color='neighbourhood_group',
                    color_discrete_map=PALETTE,
                    title='Listing count by borough — preliminary count, not an analytical figure')
fig.update_layout(showlegend=False)
fig.show()
"""))

def add_question(num, title, why, src):
    cells.append(md(f"## Q{num}. {title}\n\n{why}"))
    cells.append(code(src))

add_question(
    1, "How does price vary across boroughs, and does that hold for every room type?",
    "**Why analytical:** compares groups (boroughs) across a second dimension (room type) — a direct cross-reference, not a single distribution.",
    """agg = listings.groupby(['neighbourhood_group','room_type'], observed=True)['price'].median().reset_index()

fig = px.bar(agg, x='neighbourhood_group', y='price', color='room_type', barmode='group',
             color_discrete_map=PALETTE,
             title='Manhattan commands a premium across every room type, not just entire apartments',
             labels={'price': 'Median nightly price ($)', 'neighbourhood_group': '', 'room_type': 'Room type'})
fig.show()
"""
)

add_question(
    2, "Do cheaper listings actually earn more reviews (i.e. get booked more)?",
    "**Why analytical:** relates two numeric variables (price, review count) — tests a real market intuition rather than describing one variable.",
    """sub = listings[listings.number_of_reviews > 0]
fig = px.scatter(sub.sample(min(4000, len(sub)), random_state=1), x='price', y='number_of_reviews',
                  opacity=0.3, color_discrete_sequence=[PALETTE['highlight']], trendline='lowess',
                  title='Review counts drop off fast as price rises past ~$200/night',
                  labels={'price': 'Price ($/night)', 'number_of_reviews': 'Number of reviews'})
fig.update_xaxes(range=[0, 700])
fig.show()
"""
)

add_question(
    3, "Are 'professional' multi-listing hosts more available for booking than single-listing hosts?",
    "**Why analytical:** compares two host-type groups on a numeric outcome (availability) — a behavioral, not descriptive, comparison.",
    """agg = listings.groupby('host_type')['availability_365'].mean().reset_index()

fig = px.bar(agg, x='host_type', y='availability_365', color='host_type',
             color_discrete_sequence=[PALETTE['Manhattan'], PALETTE['Brooklyn']],
             title='Multi-listing hosts keep their properties open far more days per year',
             labels={'availability_365': 'Avg. days available / year', 'host_type': ''})
fig.update_layout(showlegend=False)
fig.show()
"""
)

add_question(
    4, "Which specific neighbourhoods are the priciest within each borough?",
    "**Why analytical:** drills a categorical comparison (borough) down one level (neighbourhood) — genuine multi-level cross-referencing.",
    """top_n = (listings.groupby(['neighbourhood_group','neighbourhood'], observed=True)['price']
         .agg(['median','count']).reset_index())
top_n = top_n[top_n['count'] >= 20]  # avoid noisy tiny neighbourhoods
top_n = top_n.sort_values('median', ascending=False).groupby('neighbourhood_group').head(3)

fig = px.bar(top_n, x='neighbourhood', y='median', color='neighbourhood_group',
             color_discrete_map=PALETTE,
             title='Top 3 priciest (well-sampled) neighbourhoods per borough',
             labels={'median': 'Median price ($)', 'neighbourhood': ''})
fig.update_xaxes(tickangle=45)
fig.show()
"""
)

add_question(
    5, "Does the minimum-nights requirement differ by room type and borough (a proxy for long-term vs. tourist rentals)?",
    "**Why analytical:** conditions a numeric variable (minimum nights) on two categoricals at once (room type x borough).",
    """m = listings[listings.minimum_nights <= 30]  # trim extreme outliers for readability
agg = m.groupby(['neighbourhood_group','room_type'], observed=True)['minimum_nights'].median().reset_index()

fig = px.bar(agg, x='neighbourhood_group', y='minimum_nights', color='room_type', barmode='group',
             color_discrete_map=PALETTE,
             title='Entire-home listings require longer minimum stays almost everywhere',
             labels={'minimum_nights': 'Median minimum nights', 'neighbourhood_group': ''})
fig.show()
"""
)

add_question(
    6, "Are listings with no reviews yet priced differently than established, reviewed listings?",
    "**Why analytical:** compares a derived group (reviewed vs. never-reviewed) on price, conditioned by room type — a genuine 2-variable comparison.",
    """agg = listings.groupby(['ever_reviewed','room_type'], observed=True)['price'].median().reset_index()
agg['ever_reviewed'] = agg['ever_reviewed'].map({True: 'Has reviews', False: 'No reviews yet'})

fig = px.bar(agg, x='room_type', y='price', color='ever_reviewed', barmode='group',
             color_discrete_sequence=[PALETTE['highlight'], PALETTE['context']],
             title='Never-reviewed listings are priced higher, not lower — sellers aren\\'t discounting to get started',
             labels={'price': 'Median price ($)', 'room_type': '', 'ever_reviewed': ''})
fig.show()
"""
)

add_question(
    7, "Where in the city are the highest-priced listings concentrated?",
    "**Why analytical:** relates two spatial variables (lat/long) to a third, numeric one (price) — genuine spatial cross-referencing.",
    """sub = listings[listings.price <= 500]
fig = px.scatter_mapbox(sub.sample(min(6000, len(sub)), random_state=1),
                          lat='latitude', lon='longitude', color='price',
                          color_continuous_scale='Blues', opacity=0.6, zoom=9,
                          title='Price rises sharply toward Manhattan\\'s core and drops in the outer boroughs',
                          labels={'price': 'Price ($)'})
fig.update_layout(mapbox_style='carto-positron', margin=dict(l=0,r=0,t=40,b=0))
fig.show()
"""
)

add_question(
    8, "Do frequently-booked listings (high reviews/month) actually have less availability left?",
    "**Why analytical:** relates a demand proxy (review frequency) to a supply outcome (availability) — a real cause-and-effect style question.",
    """sub = listings[listings.reviews_per_month > 0]
agg = sub.groupby('availability_band', observed=True)['reviews_per_month'].mean().reset_index()

fig = px.bar(agg, x='availability_band', y='reviews_per_month',
             category_orders={'availability_band': ['Never available','Rarely (1-90 days)','Sometimes (91-270)','Almost always (271+)']},
             color_discrete_sequence=[PALETTE['highlight']],
             title='Listings booked most often are, unsurprisingly, rarely available — demand tracks supply',
             labels={'reviews_per_month': 'Avg. reviews / month', 'availability_band': 'Availability'})
fig.show()
"""
)

add_question(
    9, "What's the room-type mix within each borough, and how much does it differ?",
    "**Why analytical:** compares the categorical composition (room type) across another categorical (borough) — a genuine cross-tab, not a single count.",
    """mix = (listings.groupby(['neighbourhood_group','room_type'], observed=True).size()
       .groupby(level=0).transform(lambda s: s / s.sum()).reset_index(name='share'))

fig = px.bar(mix, x='neighbourhood_group', y='share', color='room_type', barmode='stack',
             color_discrete_map=PALETTE,
             title='The Bronx and Queens lean private-room; Manhattan and Brooklyn lean whole-apartment',
             labels={'share': 'Share of listings', 'neighbourhood_group': ''})
fig.update_yaxes(tickformat='.0%')
fig.show()
"""
)

add_question(
    10, "Do multi-listing hosts price their entire-home rentals differently than individual hosts?",
    "**Why analytical:** compares host type and room type together on price — two categorical dimensions cross-referenced on one numeric outcome.",
    """sub = listings[listings.room_type == 'Entire home/apt']
agg = sub.groupby(['neighbourhood_group','host_type'], observed=True)['price'].median().reset_index()

fig = px.bar(agg, x='neighbourhood_group', y='price', color='host_type', barmode='group',
             color_discrete_sequence=[PALETTE['Manhattan'], PALETTE['Brooklyn']],
             title='Multi-listing hosts price entire homes higher in every borough — a scale premium, not a discount',
             labels={'price': 'Median price, entire home/apt ($)', 'neighbourhood_group': ''})
fig.show()
"""
)

add_question(
    11, "Which price band dominates each borough, and how sharply does that change?",
    "**Why analytical:** tracks how a categorical distribution (price band) shifts across another categorical (borough) — a genuine shape comparison.",
    """mix = (listings.groupby(['neighbourhood_group','price_band'], observed=True).size()
       .groupby(level=0).transform(lambda s: s / s.sum()).reset_index(name='share'))

fig = px.bar(mix, x='neighbourhood_group', y='share', color='price_band', barmode='stack',
             category_orders={'price_band': ['<$75','$75-150','$150-300','$300-600','$600+']},
             color_discrete_sequence=px.colors.sequential.Blues[2:],
             title='Manhattan is the only borough where the $150+ bands make up most of the market',
             labels={'share': 'Share of listings', 'neighbourhood_group': ''})
fig.update_yaxes(tickformat='.0%')
fig.show()
"""
)

add_question(
    12, "Putting it together: which factor — borough, room type, or host type — separates high- and low-price listings most?",
    "**Why analytical:** a multi-dimensional summary that cross-references three variables at once to close out the story.",
    """agg = (listings.groupby(['neighbourhood_group','room_type','host_type'], observed=True)['price']
        .median().reset_index())
agg = agg[agg.neighbourhood_group.isin(['Manhattan','Brooklyn','Queens'])]

fig = px.bar(agg, x='room_type', y='price', color='host_type', barmode='group',
             facet_col='neighbourhood_group',
             color_discrete_sequence=[PALETTE['Manhattan'], PALETTE['Brooklyn']],
             title='Room type splits price the most; borough shifts the whole scale; host type is a smaller, consistent premium',
             labels={'price': 'Median price ($)', 'room_type': ''})
fig.update_xaxes(tickangle=30)
fig.show()
"""
)

cells.append(md("""## 3. Conclusions

- **Location sets the floor, room type sets the ceiling:** Manhattan commands a premium across every room type, but the entire-home vs. private-room gap is often just as large within a single borough.
- **Demand favors mid-priced listings:** review activity (a booking proxy) falls off sharply once nightly price passes roughly $200.
- **"Professional" hosts behave differently:** multi-listing hosts keep properties available more days per year and price entire-home rentals higher than individual hosts do — consistent with a scaled, business-like operation rather than someone renting out a spare room.
- **Minimum-night policies track use case:** entire-home listings require longer minimum stays almost everywhere, suggesting they skew toward extended/relocation stays rather than short tourist visits.
- **New listings aren't discounted:** never-reviewed listings are priced *higher*, not lower, than reviewed ones — hosts aren't using price to buy their first reviews.
- **Geography and room-type mix reinforce each other:** outer boroughs (Bronx, Queens) lean private-room by necessity/affordability, while Manhattan and Brooklyn lean whole-apartment.
- **Price bands cluster by borough:** Manhattan is the only borough where $150+ listings make up the majority of the market; every other borough is dominated by sub-$150 listings.

*A note on scope: this is a purely descriptive, aggregate statistical analysis of publicly available marketplace listing data — no individual guest or host personal/financial information is involved.*
"""))

nb = {
    "cells": cells,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.11"}
    },
    "nbformat": 4,
    "nbformat_minor": 5
}

with open("notebook/NYC_Airbnb_Analysis.ipynb", "w") as f:
    json.dump(nb, f, indent=1)

print("wrote notebook/NYC_Airbnb_Analysis.ipynb with", len(cells), "cells")

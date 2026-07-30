# Who Gets Booked? A Look Inside NYC's Airbnb Market

Final individual project — Data Visualization, Summer 2026.

## Dataset

**New York City Airbnb Open Data** (2019 snapshot, ~48,900 listings) —
[Kaggle](https://www.kaggle.com/datasets/dgomonov/new-york-city-airbnb-open-data),
originally compiled from Inside Airbnb.

The data is **not bundled** in this repo — `data_prep.py` downloads the CSV
fresh from a public mirror the first time you run the notebook or dashboard.
To work offline, run `python data_prep.py` once to cache
`data/listings_clean.csv`.

**Why this dataset is an easy but strong pick:**
- **One flat table** — no reshaping, no merging multiple files. Every
  question is a `groupby` / `pivot` / scatter on the same 16 columns.
- **Real-world, rich, and varied** — numerical (price, reviews, minimum
  nights), categorical (borough, neighbourhood, room type), temporal (last
  review date), and spatial (latitude/longitude) attributes all in one place.
- **Intuitive** — everyone understands "price," "borough," and "room type"
  immediately, so you can focus your time on the analysis and visuals
  instead of understanding the data.

Columns: `id, name, host_id, host_name, neighbourhood_group, neighbourhood,
latitude, longitude, room_type, price, minimum_nights, number_of_reviews,
last_review, reviews_per_month, calculated_host_listings_count,
availability_365`.

## Repo structure

```
├── data_prep.py                        # shared data loading + feature engineering
├── requirements.txt
├── notebook/
│   └── NYC_Airbnb_Analysis.ipynb       # EDA + 12 analytical questions, each with a Plotly figure
├── dashboard/
│   └── app.py                          # Streamlit dashboard (deploy this file)
├── presentation/
│   └── NYC_Airbnb_Analysis.pptx        # slide deck summarizing insights
└── data/                                # (generated) cached CSV, gitignored
```

## Running locally

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Notebook
jupyter notebook notebook/NYC_Airbnb_Analysis.ipynb

# Dashboard
streamlit run dashboard/app.py
```

First run downloads the ~48,900-row CSV (a few seconds); after that it's
cached (`data/*.csv` locally, or `@st.cache_data` on Streamlit Cloud).

## Deploying the dashboard to Streamlit Community Cloud

1. Push this whole folder to a **new public GitHub repo**.
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**.
3. Point it at your repo, branch `main`, file path `dashboard/app.py`.
4. Deploy — Streamlit installs `requirements.txt` automatically.
5. Copy the live URL into your presentation and submission message.

## The 12 analytical questions (see notebook for full detail)

1. Does price vary by borough across every room type?
2. Do cheaper listings earn more reviews (booking proxy)?
3. Are multi-listing hosts more available than single-listing hosts?
4. Which neighbourhoods are priciest within each borough?
5. Does minimum-nights policy vary by room type × borough?
6. Are never-reviewed listings priced differently than reviewed ones?
7. Where geographically are the priciest listings concentrated?
8. Do frequently-booked listings have less availability left?
9. What's the room-type mix within each borough?
10. Do multi-listing hosts price entire homes differently?
11. Which price band dominates each borough?
12. Combined: borough × room type × host type on price.

## Design principles applied

- Plotly only, CVD-safe palette (blue/orange/green core, muted grey for
  context, one red accent for focus) used consistently across every figure
- Titles state the takeaway, not just the variable names
- Decluttered: no gridlines/chart-junk; direct annotation where useful
- Clean white background throughout, consistent across notebook and dashboard

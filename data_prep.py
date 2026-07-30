"""
NYC Airbnb Open Data — loading & feature engineering
Source: "New York City Airbnb Open Data" (Kaggle, originally from Inside Airbnb)
https://www.kaggle.com/datasets/dgomonov/new-york-city-airbnb-open-data

Downloads the single flat CSV (AB_NYC_2019.csv, ~48,900 listings, 16 columns)
directly from a public mirror and adds a handful of derived columns used
across the notebook and the dashboard.
"""

import pandas as pd
import numpy as np

# Public GitHub mirror of the Kaggle CSV (identical content, no login needed)
DATA_URL = "https://raw.githubusercontent.com/4GeeksAcademy/data-preprocessing-project-tutorial/main/AB_NYC_2019.csv"


def load_raw(url=DATA_URL):
    return pd.read_csv(url)


def add_features(df):
    """Clean + add a few simple derived columns. Nothing fancy on purpose —
    this is a single flat table, so no reshaping is needed."""
    df = df.copy()

    # basic cleaning
    df = df[df["price"] > 0]
    df["last_review"] = pd.to_datetime(df["last_review"], errors="coerce")
    df["reviews_per_month"] = df["reviews_per_month"].fillna(0)

    # is this host a "professional" (multi-listing) host?
    df["host_type"] = np.where(df["calculated_host_listings_count"] > 1,
                                "Multi-listing host", "Single-listing host")

    # has the listing ever been reviewed?
    df["ever_reviewed"] = df["number_of_reviews"] > 0

    # bucket price into readable bands for grouping
    price_bins = [0, 75, 150, 300, 600, 1e9]
    price_labels = ["<$75", "$75-150", "$150-300", "$300-600", "$600+"]
    df["price_band"] = pd.cut(df["price"], bins=price_bins, labels=price_labels)

    # bucket availability into a simple 0/occasional/most-of-year scale
    avail_bins = [-1, 0, 90, 270, 366]
    avail_labels = ["Never available", "Rarely (1-90 days)", "Sometimes (91-270)", "Almost always (271+)"]
    df["availability_band"] = pd.cut(df["availability_365"], bins=avail_bins, labels=avail_labels)

    return df


def build_dataset(url=DATA_URL):
    return add_features(load_raw(url))


if __name__ == "__main__":
    df = build_dataset()
    print("listings:", df.shape)
    df.to_csv("data/listings_clean.csv", index=False)

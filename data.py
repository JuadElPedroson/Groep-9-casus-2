"""
data.py - haalt de twee datasets op via de Kaggle API en voegt ze samen.

Gebruik in je notebook of app.py:

    from data import load_data
    df = load_data()

Iedereen in de groep gebruikt deze functie, zodat we allemaal met precies
dezelfde (schone, samengevoegde) tabel werken.
"""

import os
import glob
import pandas as pd
import streamlit as st
from kaggle.api.kaggle_api_extended import KaggleApi

# Kaggle-dataset-slugs (het stuk van de URL na "/datasets/").
# Check dit één keer zelf op kaggle.com als het niet lijkt te kloppen.
DATASET_SPOTIFY = "meeratif/spotify-most-streamed-artists-of-all-time"
DATASET_COUNTRIES = "fernandol/countries-of-the-world"

# Landnamen in de Spotify-data die anders geschreven zijn dan in de landendata
COUNTRY_NAME_MAPPING = {
    "South Korea": "Korea, South",
    "DR Congo": "Congo, Dem. Rep.",
    "Trinidad and Tobago": "Trinidad & Tobago",
    "Scotland": "United Kingdom",
}


def _download_and_read(dataset_slug, folder):
    """Download een Kaggle-dataset (alleen als dat nog niet is gebeurd)
    en lees het CSV-bestand dat erin staat in."""
    if not os.path.exists(folder):
        api = KaggleApi()
        api.authenticate()
        api.dataset_download_files(dataset_slug, path=folder, unzip=True)

    csv_bestanden = glob.glob(f"{folder}/*.csv")
    print(f"Gevonden in {folder}:", csv_bestanden)

    df = pd.read_csv(csv_bestanden[0])
    df.columns = [kolom.strip() for kolom in df.columns]
    return df


@st.cache_data
def load_data():
    spotify = _download_and_read(DATASET_SPOTIFY, "data/spotify")
    countries = _download_and_read(DATASET_COUNTRIES, "data/countries")

    spotify["Country of Origin"] = spotify["Country of Origin"].str.strip()
    countries["Country"] = countries["Country"].str.strip()

    # De landendata heeft komma's als decimaalteken (bv. "48,0" i.p.v. "48.0").
    # Dit probeert elke tekstkolom om te zetten naar een getal; lukt dat niet
    # (zoals bij "Country" of "Region"), dan blijft die kolom gewoon tekst.
    for kolom in countries.columns:
        if countries[kolom].dtype == "object":
            try:
                countries[kolom] = countries[kolom].str.replace(",", ".").astype(float)
            except (ValueError, AttributeError):
                pass

    # Landnamen gelijktrekken zodat de join goed werkt
    spotify["country_mapped"] = spotify["Country of Origin"].replace(COUNTRY_NAME_MAPPING)

    # Samenvoegen - noteer altijd hoeveel rijen je voor en na de join hebt
    print("Rijen vóór de join:", len(spotify))
    df = spotify.merge(countries, left_on="country_mapped", right_on="Country", how="left")
    print("Rijen na de join:", len(df))

    # Handige extra kolom voor de "rijkdom vs. roem"-grafieken
    df["streams_per_million_pop"] = df["Total Streams (in millions)"] / (df["Population"] / 1_000_000)

    return df


if __name__ == "__main__":
    # Los testen zonder Streamlit: python3 data.py
    df = load_data()
    print(df.shape)
    print(df.head())

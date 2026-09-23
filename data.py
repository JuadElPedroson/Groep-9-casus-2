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

# Kaggle-dataset-slugs (het stuk van de URL na "/datasets/") - geverifieerd
# tegen de originele bestanden, dit zijn de juiste.
DATASET_SPOTIFY = "rishavsvault/most-streamed-artists-on-spotify"
DATASET_COUNTRIES = "fernandol/countries-of-the-world"

# Landnamen in de landendata die anders geschreven zijn dan in de Spotify-data
NAAM_CORRECTIES = {
    "Korea, South": "South Korea",
    "Korea, North": "North Korea",
    "Congo, Dem. Rep.": "DR Congo",
    "Trinidad & Tobago": "Trinidad and Tobago",
}


def _zet_kaggle_token_klaar():
    """Lokaal (op je eigen Mac) staat je Kaggle-token al in ~/.kaggle/access_token,
    dat vindt de kaggle-library vanzelf. Op Streamlit Cloud bestaat dat bestand niet -
    daar zet je je token in de app-secrets, en die zetten we hier over naar een
    environment variable zodat authenticate() 'm alsnog vindt."""
    try:
        if "KAGGLE_API_TOKEN" in st.secrets:
            os.environ["KAGGLE_API_TOKEN"] = st.secrets["KAGGLE_API_TOKEN"]
    except Exception:
        # Geen secrets.toml lokaal aanwezig - heel normaal, lokaal gebruik je
        # toch gewoon ~/.kaggle/access_token. Niets aan de hand.
        pass


def _download_and_read(dataset_slug, folder):
    """Download een Kaggle-dataset (alleen als dat nog niet is gebeurd)
    en lees het CSV-bestand dat erin staat in."""
    if not os.path.exists(folder):
        _zet_kaggle_token_klaar()
        api = KaggleApi()
        api.authenticate()
        api.dataset_download_files(dataset_slug, path=folder, unzip=True)

    csv_bestanden = glob.glob(f"{folder}/*.csv")
    print(f"Gevonden in {folder}:", csv_bestanden)

    # Sommige Kaggle-datasets bevatten meerdere CSV's (bv. een uitgebreide en
    # een simpele versie). Kies de "V1.1"-versie als die bestaat - dat is de
    # rijkste variant, met alle kolommen die we nodig hebben.
    rijkste = [f for f in csv_bestanden if "v1.1" in f.lower()]
    gekozen = rijkste[0] if rijkste else csv_bestanden[0]
    print("Gebruikt bestand:", gekozen)

    df = pd.read_csv(gekozen)
    df.columns = [kolom.strip() for kolom in df.columns]
    return df


@st.cache_data
def load_data():
    spotify = _download_and_read(DATASET_SPOTIFY, "data/spotify")
    countries = _download_and_read(DATASET_COUNTRIES, "data/countries")

    # Spaties voor en achter de tekst weghalen
    spotify["Country of Origin"] = spotify["Country of Origin"].str.strip()
    countries["Country"] = countries["Country"].str.strip()
    countries["Region"] = countries["Region"].str.strip()

    # Dubbele rijen checken (we verwijderen ze niet automatisch, wel laten zien)
    print("Dubbele rijen in spotify-data:", spotify.duplicated().sum())
    print("Dubbele rijen in landendata:", countries.duplicated().sum())

    # De landendata heeft komma's als decimaalteken (bv. "48,0" i.p.v. "48.0").
    # Dit probeert elke tekstkolom om te zetten naar een getal; lukt dat niet
    # (zoals bij "Country" of "Region"), dan blijft die kolom gewoon tekst.
    for kolom in countries.columns:
        if countries[kolom].dtype == "object":
            try:
                countries[kolom] = countries[kolom].str.replace(",", ".").astype(float)
            except (ValueError, AttributeError):
                pass

    # Landnamen in de landendata gelijktrekken aan de schrijfwijze in de
    # Spotify-data, zodat de join hierna geen rijen verliest
    countries["Country"] = countries["Country"].replace(NAAM_CORRECTIES)

    # Schotland staat in de Spotify-data los vermeld, maar in de landendata
    # bestaat alleen "United Kingdom". Daarom koppelen we Schotse artiesten
    # apart aan United Kingdom.
    spotify["country_mapped"] = spotify["Country of Origin"].replace(
        {"Scotland": "United Kingdom"}
    )

    # Percentages afronden op 1 decimaal, netter voor grafieken
    spotify["% of Solo Streams"] = spotify["% of Solo Streams"].round(1)
    spotify["% of Collaborative Streams"] = spotify["% of Collaborative Streams"].round(1)

    # Samenvoegen - noteer altijd hoeveel rijen je voor en na de join hebt
    print("Rijen vóór de join:", len(spotify))
    df = spotify.merge(countries, left_on="country_mapped", right_on="Country", how="left")
    print("Rijen na de join:", len(df))
    print("Artiesten zonder gekoppeld land:", df["Country"].isna().sum())

    # Handige extra kolom voor de "rijkdom vs. roem"-grafieken
    df["streams_per_million_pop"] = df["Total Streams (in millions)"] / (df["Population"] / 1_000_000)

    return df


if __name__ == "__main__":
    # Los testen zonder Streamlit: python3 data.py
    df = load_data()
    print(df.shape)
    print(df.head())

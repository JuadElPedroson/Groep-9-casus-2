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
 
# Landnamen in de Spotify-data die anders geschreven zijn dan in de landendata
COUNTRY_NAME_MAPPING = {
    "South Korea": "Korea, South",
    "DR Congo": "Congo, Dem. Rep.",
    "Trinidad and Tobago": "Trinidad & Tobago",
    "Scotland": "United Kingdom",
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
 
    # countries opschonen
    countries.head()
    countries.dtypes
    countries.isnull().sum()
 
    # Spaties voor en achter de text weghalen
    countries['Country'] = countries['Country'].str.strip()
    countries['Region'] = countries['Region'].str.strip()
 
    countries[['Country', 'Region']].head()
 
    # de komma's in de cijferkolommen vervangen door een punt, zodat pandas ze als getal (float) inleest.
    komma_kolommen = [
       'Pop. Density (per sq. mi.)', 'Coastline (coast/area ratio)', 'Net migration',
       'Infant mortality (per 1000 births)', 'Literacy (%)', 'Phones (per 1000)',
       'Arable (%)', 'Crops (%)', 'Other (%)', 'Climate', 'Birthrate', 'Deathrate',
        'Agriculture', 'Industry', 'Service'
    ]
 
    for kolom in komma_kolommen:
        countries[kolom] = countries[kolom].str.replace(',', '.')
        countries[kolom] = pd.to_numeric(countries[kolom])
 
    countries.dtypes
 
    # checken op dubbele rijen
    countries.duplicated().sum()
 
    # Let op: in de Spotify-dataset komt ook "Scotland" voor als land van herkomst (bv. Calvin Harris).
    # Schotland staat niet los in de countries-dataset, want dat valt onder "United Kingdom".
    # Misschien Schotland bij United Kingdom optellen?
 
    # spotify opschonen
    spotify.head()
 
    print(spotify.columns.tolist())
    spotify.isnull().sum()
 
    # spaties weghalen
    spotify.columns = spotify.columns.str.strip()
 
    print(spotify.columns.tolist())
 
    # Checken op dubbele artiesten en dubbele rijen
    print('Dubbele artiestennamen:', spotify['Artist Name'].duplicated().sum())
    print('Volledig dubbele rijen:', spotify.duplicated().sum())
 
    # percentages afronden op 1 decimaal
    spotify['% of Solo Streams'] = spotify['% of Solo Streams'].round(1)
    spotify['% of Collaborative Streams'] = spotify['% of Collaborative Streams'].round(1)
 
    spotify[['Artist Name', '% of Solo Streams', '% of Collaborative Streams']].head()  
 
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
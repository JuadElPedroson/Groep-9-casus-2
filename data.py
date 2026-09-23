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
import time
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


WELVAARTSGROEPEN = ["Arm", "Laag-midden", "Hoog-midden", "Rijk"]


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
    if not glob.glob(f"{folder}/*.csv"):
        _zet_kaggle_token_klaar()
        api = KaggleApi()
        api.authenticate()
        # Tot 3 keer proberen, voor als de API even traag is of niet reageert
        for poging in range(3):
            try:
                api.dataset_download_files(dataset_slug, path=folder, unzip=True)
                break
            except Exception as fout:
                print(f"Download mislukt (poging {poging + 1}):", fout)
                time.sleep(2)
        else:
            st.error("De data kon niet worden opgehaald bij Kaggle, probeer het later opnieuw.")
            st.stop()

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
def load_landen():
    # Alle landen, ook zonder artiest (nodig voor de wereldbevolking)
    countries = _download_and_read(DATASET_COUNTRIES, "data/countries")
    countries["Country"] = countries["Country"].str.strip()
    countries["Region"] = countries["Region"].str.strip()
    print("Dubbele rijen in landendata:", countries.duplicated().sum())

    # De landendata heeft komma's als decimaalteken (bv. "48,0" i.p.v. "48.0").
    # Dit zet elke kolom om naar een getal, behalve Country en Region.
    # errors="coerce" zorgt dat een enkele rare waarde niet de hele kolom
    # laat mislukken - die ene waarde wordt dan NaN in plaats van tekst.
    tekst_kolommen = ["Country", "Region"]
    for kolom in countries.columns:
        if kolom in tekst_kolommen:
            continue
        schoon = countries[kolom].astype(str).str.replace(",", ".").str.strip()
        countries[kolom] = pd.to_numeric(schoon, errors="coerce")

    # Landnamen in de landendata gelijktrekken aan de schrijfwijze in de
    # Spotify-data, zodat de join hierna geen rijen verliest
    countries["Country"] = countries["Country"].replace(NAAM_CORRECTIES)

    # Alle landen in 4 even grote groepen op basis van GDP per inwoner
    countries["Welvaartsgroep"] = pd.qcut(
        countries["GDP ($ per capita)"], 4, labels=WELVAARTSGROEPEN
    )
    return countries


@st.cache_data
def load_data():
    spotify = _download_and_read(DATASET_SPOTIFY, "data/spotify")
    countries = load_landen()

    # Spaties voor en achter de tekst weghalen
    spotify["Country of Origin"] = spotify["Country of Origin"].str.strip()

    # Dubbele rijen checken (we verwijderen ze niet automatisch, wel laten zien)
    print("Dubbele rijen in spotify-data:", spotify.duplicated().sum())

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


def voeg_marge_toe():
    """Wat ruimte aan de zijkanten van de pagina, anders lopen grafieken
    helemaal tot de rand door en oogt het rommelig."""
    st.markdown(
        "<style>.block-container {max-width: 1100px; padding-left: 3rem; padding-right: 3rem;}</style>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    # Los testen zonder Streamlit: python3 data.py
    df = load_data()
    print(df.shape)
    print(df.head())

"""
app.py - de Streamlit-pagina zelf. Dit is het bestand dat je straks bij het
deployen aanwijst als "Main file path".

Start 'm lokaal met: streamlit run app.py
"""

import streamlit as st
from data import load_data

st.set_page_config(page_title="Spotify x Landendata", layout="wide")

st.title("Spotify's meest gestreamde artiesten x landendata")
st.write(
    "Basisversie - laat zien dat de data via de Kaggle API wordt opgehaald "
    "en samengevoegd. Hier komen straks onze grafieken bij."
)

df = load_data()

st.success(f"Data geladen: {df.shape[0]} artiesten, {df.shape[1]} kolommen.")
st.dataframe(df.head(20))

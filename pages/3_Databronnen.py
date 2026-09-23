import streamlit as st
from data import load_data

st.title("Databronnen")

st.write(
    "Twee bronnen zijn samengevoegd: de 500 meest gestreamde artiesten op "
    "Spotify en een tabel met landengegevens zoals bevolking en GDP per "
    "hoofd. Ze zijn gekoppeld op het land van herkomst van de artiest."
)

st.write("""
Countries of the World. (n.d.). Retrieved September 23, 2026, from https://www.kaggle.com/datasets/fernandol/countries-of-the-world
Most Streamed Artists on Spotify. (n.d.). Retrieved September 23, 2026, from https://www.kaggle.com/datasets/rishavsvault/most-streamed-artists-on-spotify

Streamlit • A faster way to build and share data apps. (2021, January 14). https://streamlit.io/

""")

df = load_data()
st.dataframe(df.head(20))

import streamlit as st
from data import load_data

st.title("Databronnen")

st.write(
    "we hebben tijdens deze casus AI vornamelijk gebruikt om data op te halen via de API van kaggel en als een ondersteunende tool voor onze coding skills "
)

st.write("""
Countries of the World. (n.d.). Retrieved September 23, 2026, from https://www.kaggle.com/datasets/fernandol/countries-of-the-world

Most Streamed Artists on Spotify. (n.d.). Retrieved September 23, 2026, from https://www.kaggle.com/datasets/rishavsvault/most-streamed-artists-on-spotify

Streamlit • A faster way to build and share data apps. (2021, January 14). https://streamlit.io/

""")

df = load_data()
st.dataframe(df.head(20))

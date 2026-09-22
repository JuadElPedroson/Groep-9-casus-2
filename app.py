import streamlit as st
from data import load_data

st.set_page_config(page_title="Spotify x Landendata", layout="wide")

st.title("Heeft welvaart invloed op het succes van artiesten?")

st.write(
    "Onderzoeksvraag: heeft de welvaart in het land van herkomst invloed op "
    "het aantal streams van een populaire artiest? We combineren de 500 "
    "meest gestreamde artiesten op Spotify met landengegevens zoals GDP per "
    "hoofd van de bevolking."
)

df = load_data()

st.write(f"Dataset geladen: {df.shape[0]} artiesten, gekoppeld aan hun land van herkomst.")

st.write("Gebruik het menu links om de analyses te bekijken.")

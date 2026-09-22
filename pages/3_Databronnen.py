import streamlit as st
from data import load_data

st.title("Databronnen")

st.write(
    "Twee bronnen zijn samengevoegd: de 500 meest gestreamde artiesten op "
    "Spotify en een tabel met landengegevens zoals bevolking en GDP per "
    "hoofd. Ze zijn gekoppeld op het land van herkomst van de artiest."
)

st.write("""
Wat hier nog moet gebeuren:
- Aantal rijen voor en na het samenvoegen laten zien
- Landen die niet gekoppeld konden worden apart benoemen
- Kolommen met ontbrekende waarden in beeld brengen
- De volledige tabel doorzoekbaar maken
""")

df = load_data()
st.dataframe(df.head(20))

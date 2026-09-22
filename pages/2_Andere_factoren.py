import streamlit as st
from data import load_data

st.title("Andere factoren")

st.write(
    "Welvaart is niet het enige dat een rol kan spelen. Hier verkennen we "
    "andere kenmerken van het land van herkomst, zoals bevolkingsomvang, "
    "regio en taal."
)

st.write("""
Wat hier nog moet gebeuren:
- Dropdown waarmee je kiest welk kenmerk je bekijkt (bevolking, regio, taal)
- Scatterplot of staafdiagram van het gekozen kenmerk tegen streams
- Slider om te filteren op debuutjaar van de artiest
- Checkbox om landen met maar 1 artiest uit te sluiten, want die vertekenen het beeld
""")

df = load_data()

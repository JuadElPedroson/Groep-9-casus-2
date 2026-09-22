import streamlit as st
from data import load_data

st.title("Rijkdom en streams")

st.write(
    "De kern van onze vraag: hangt het GDP per hoofd van de bevolking van "
    "het land van herkomst samen met het aantal streams van een artiest?"
)

st.write("""
Wat hier nog moet gebeuren:
- Artiesten zonder GDP-waarde (land kon niet gekoppeld worden) apart benoemen
- Een log-versie van streams maken, want een paar artiesten met extreem veel streams trekken de grafiek scheef
- Scatterplot: GDP per capita tegen streams per artiest, met een trendlijn
- Dezelfde vergelijking maar dan gemiddeld per land, zodat landen met veel artiesten niet te zwaar meetellen
- Boxplot: streams per welvaartscategorie (laag, midden, hoog GDP)
- Correlatiecoëfficiënt berekenen en tonen
""")

df = load_data()

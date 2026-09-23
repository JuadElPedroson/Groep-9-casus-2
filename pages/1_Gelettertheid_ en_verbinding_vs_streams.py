import streamlit as st
from data import load_data
import plotly.express as px
 
df = load_data()
 
st.title("Gelettertheid/verbinding vs streams")
 
fig2 = px.scatter(
    df,
    x="Literacy (%)",
    y="Phones (per 1000)",
    size="Total Streams (in millions)",
    color="Region",
    hover_name="Artist Name",
    title="Geletterdheid en telefoonbezit van het thuisland vs. streamingsucces",
    labels={
        "Literacy (%)": "Geletterdheid (%)",
        "Phones (per 1000)": "Telefoons per 1000 inwoners"
    }
)
st.plotly_chart(fig2, use_container_width=True)


st.write(
    "Onze onderzoeksvraag draait om GDP per hoofd van de bevolking en het "
    "aantal streams van een artiest. We gebruiken hiervoor de kolom GDP per "
    "capita uit de landendata en de kolom Total Streams uit de Spotify data, "
    "gekoppeld via het land van herkomst van de artiest."
)

st.write(
    "Niet elk land uit de Spotify data kon gekoppeld worden aan de "
    "landendata, bijvoorbeeld door verschillen in schrijfwijze. Artiesten "
    "zonder GDP waarde moeten we apart benoemen of uit de analyse halen, "
    "anders vertekent dat de resultaten."
)

st.write(
    "Het aantal streams is erg scheef verdeeld omdat een paar artiesten "
    "extreem veel meer streams hebben dan de rest. Daarom maken we een log "
    "versie van de streams kolom, zodat de grafiek beter leesbaar wordt."
)

st.write(
    "We maken een scatterplot met GDP per capita op de x as en het aantal "
    "streams op de y as, met een trendlijn erdoorheen. Zo zien we in een "
    "oogopslag of er een verband is."
)

st.write(
    "Omdat sommige landen veel meer artiesten hebben dan andere, maken we "
    "ook een versie waarbij we eerst het gemiddelde aantal streams per land "
    "berekenen. Zo telt een land met tien artiesten niet harder mee dan een "
    "land met een artiest."
)

st.write(
    "Daarnaast verdelen we de landen in drie groepen op basis van GDP, laag, "
    "midden en hoog, en zetten we die naast elkaar in een boxplot. Dat laat "
    "zien of rijkere landen over het algemeen artiesten met meer streams "
    "hebben."
)

st.write(
    "Tot slot berekenen we de correlatiecoefficient tussen GDP en streams. "
    "Dat is een getal tussen min een en een dat aangeeft hoe sterk het "
    "verband is."
)

df = load_data()

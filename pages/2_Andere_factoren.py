import streamlit as st
from data import load_data

df = load_data()

st.title("Andere factoren")

# Bar chart incl. dropdown + multiselect
weergave = st.selectbox("Kies weergave", ["Landen", "Genres"])

if weergave == "Landen":
    opties = sorted(df["Country of Origin"].unique())
    kolom = "Country of Origin"
    enkelvoud = "land"
else:
    opties = sorted(df["Primary Genre"].unique())
    kolom = "Primary Genre"
    enkelvoud = "genre"

geselecteerd = st.sidebar.multiselect(f"Selecteer {weergave.lower()}", opties, default=opties)

gefilterd_df = df[df[kolom].isin(geselecteerd)]

st.subheader(f"Totale streams per {enkelvoud}")

totaal_df = (
    gefilterd_df.groupby([kolom, "Region"])["Total Streams (in millions)"]
    .sum()
    .reset_index()
)

st.bar_chart(data=totaal_df, x=kolom, y="Total Streams (in millions)", color="Region")

st.write(
    "Welvaart is niet het enige dat een rol kan spelen bij het succes van "
    "een artiest. In de gekoppelde data hebben we ook informatie over "
    "bevolkingsomvang, regio, taal, geletterdheid en het jaar waarin een "
    "artiest debuteerde."
)

st.write(
    "De bevolking van een land is net als streams erg scheef verdeeld, een "
    "paar landen zijn extreem groot. Daarom gebruiken we ook hier een log "
    "versie voordat we het vergelijken met streams."
)

st.write(
    "Bij regio moeten we de schrijfwijze controleren, soms staat dezelfde "
    "regio net iets anders geschreven met spaties of hoofdletters, en dat "
    "moeten we gelijktrekken voordat we kunnen groeperen."
)

st.write(
    "Bij de taal van een artiest komen sommige talen maar bij een of twee "
    "artiesten voor. Die groeperen we samen onder Overig, anders wordt de "
    "grafiek onoverzichtelijk met heel veel kleine staafjes."
)

st.write(
    "Bij geletterdheid en debuutjaar checken we of er ontbrekende of rare "
    "waarden tussen zitten, bijvoorbeeld een debuutjaar van nul, en die "
    "halen we eruit."
)

st.write(
    "Voor bevolking maken we een scatterplot tegen streams, ook weer met "
    "beide assen op log schaal. Voor regio en taal maken we een "
    "staafdiagram met het gemiddelde aantal streams per groep, zo zie je "
    "snel welke regio of taal gemiddeld beter scoort. Voor geletterdheid "
    "maken we een scatterplot tegen streams, en voor debuutjaar een lijn of "
    "scatterplot om te zien of oudere of juist nieuwere artiesten gemiddeld "
    "meer streams hebben."
)

st.write(
    "Ook hier berekenen we telkens de correlatiecoefficient, zodat we het "
    "verband ook in een getal kunnen laten zien."
)

df = load_data()

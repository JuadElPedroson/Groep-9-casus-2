import streamlit as st
from data import load_data
import plotly.express as px

st.set_page_config(page_title="Spotify x Landendata", layout="wide")

df = load_data()

st.write(f"Dataset geladen: {df.shape[0]} artiesten, gekoppeld aan hun land van herkomst.")

st.title("Heeft welvaart in het land van herkomst invloed op het succes van artiesten?")

st.write(
    "Onderzoeksvraag: heeft de welvaart in het land van herkomst invloed op "
    "het aantal streams van een populaire artiest? We combineren de 500 "
    "meest gestreamde artiesten op Spotify met landengegevens zoals GDP per "
    "hoofd van de bevolking."
)

st.write("Scatterplot: snel beantwoorden van de hoofdvraag")

st.sidebar.header("Filters")

aantal_artiesten = st.sidebar.slider(
    "Top x artiesten",
    min_value=10, max_value=len(df), value=100, step=10
)

min_streams = st.sidebar.slider(
    "Minimaal aantal streams (miljoen)",
    0, int(df["Total Streams (in millions)"].max()), 0
)

gefilterd = df[
    (df["Total Streams (in millions)"] >= min_streams)
]
gefilterd = gefilterd.sort_values("Total Streams (in millions)", ascending=False).head(aantal_artiesten)

fig = px.scatter(gefilterd, x="GDP ($ per capita)", y="Total Streams (in millions)", color="Region", hover_name="Artist Name", log_y=True, title="Welvaart van het land van herkomst vs. streamingsucces van de artiest",
                 labels={"GDP ($ per capita)": "GDP per capita ($)", "Total Streams (in millions)": "Totaal streams (miljoen)"})

st.plotly_chart(fig, use_container_width=True)

st.caption("""
De grafiek laat een lichte opwaartse trend zien: artiesten uit landen met een hogere
GDP per capita halen vaker hoge streamcijfers. De hoogste uitschieters (rond de
120 tot 140 miljard streams) komen allemaal uit Noord-Amerika, een van de rijkere
regio's in deze dataset. Toch is het verband niet perfect: ook uit Noord-Amerika komen
veel artiesten met relatief weinig streams, en artiesten uit armere regio's (zoals
Latijns-Amerika) kunnen soms hoger scoren dan verwacht. Welvaart lijkt dus kansen te
vergroten, maar garandeert geen succes.
""")

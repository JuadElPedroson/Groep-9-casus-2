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

if weergave == "Landen":
    st.caption("""
    Deze grafiek laat zien hoeveel streams artiesten uit elk land bij elkaar optellen.
    Grote landen met veel bekende artiesten (zoals de Verenigde Staten) domineren van
    nature deze grafiek, daarom is de multiselect hierboven handig om landen uit te
    zetten en kleinere landen beter met elkaar te vergelijken.
    """)
else:
    st.caption("""
    Deze grafiek laat zien hoeveel streams er per genre bij elkaar zijn opgeteld.
    Populaire genres zoals Hip-Hop en Pop domineren van nature deze grafiek, daarom
    is de multiselect hierboven handig om genres uit te zetten en kleinere genres
    beter met elkaar te vergelijken.
    """)

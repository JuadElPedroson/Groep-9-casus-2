import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from data import load_data

st.title("Rijkdom en streams")

st.write(
    "De kern van onze vraag: hangt het GDP per hoofd van de bevolking van "
    "het land van herkomst samen met het aantal streams van een artiest?"
)

df = load_data()

df_schoon = df.dropna(subset=["GDP ($ per capita)"]).copy()
aantal_zonder_land = df["GDP ($ per capita)"].isna().sum()

st.write(
    f"{aantal_zonder_land} van de {len(df)} artiesten konden niet gekoppeld "
    "worden aan een land met GDP-gegevens en laten we hier buiten "
    "beschouwing."
)

df_schoon["streams_log"] = np.log10(df_schoon["Total Streams (in millions)"])

correlatie = df_schoon["GDP ($ per capita)"].corr(df_schoon["Total Streams (in millions)"])
st.metric("Correlatie GDP per capita en streams", round(correlatie, 2))

st.subheader("GDP per capita tegen streams, per artiest")
fig1 = px.scatter(
    df_schoon,
    x="GDP ($ per capita)",
    y="streams_log",
    hover_name="Artist Name",
    trendline="ols",
    labels={"streams_log": "streams (log schaal)"},
)
st.plotly_chart(fig1, use_container_width=True)

st.subheader("GDP per capita tegen gemiddeld aantal streams, per land")
per_land = df_schoon.groupby("Country of Origin").agg(
    gdp=("GDP ($ per capita)", "mean"),
    gemiddelde_streams=("Total Streams (in millions)", "mean"),
    aantal_artiesten=("Artist Name", "count"),
).reset_index()

fig2 = px.scatter(
    per_land,
    x="gdp",
    y="gemiddelde_streams",
    size="aantal_artiesten",
    hover_name="Country of Origin",
    labels={"gdp": "GDP per capita", "gemiddelde_streams": "gemiddelde streams"},
)
st.plotly_chart(fig2, use_container_width=True)

st.subheader("Streams per welvaartscategorie")
df_schoon["welvaart"] = pd.qcut(
    df_schoon["GDP ($ per capita)"], q=3, labels=["laag", "midden", "hoog"]
)

fig3 = px.box(
    df_schoon,
    x="welvaart",
    y="streams_log",
    labels={"welvaart": "welvaartscategorie", "streams_log": "streams (log schaal)"},
)
st.plotly_chart(fig3, use_container_width=True)

import pandas as pd
import streamlit as st
from data import load_data, load_landen, voeg_marge_toe

st.title("Databronnen")
voeg_marge_toe()

df = load_data()
landen = load_landen()

st.subheader("Waar komt de data vandaan?")
st.markdown(
    "We halen twee openbare datasets op via de Kaggle API (zie `data.py`):\n"
    "- Most Streamed Artists on Spotify (`rishavsvault/most-streamed-artists-on-spotify`, "
    "stand 17-07-2026): de 500 meest gestreamde artiesten. We gebruiken land "
    "van herkomst, taal, debuutjaar en totaal aantal streams.\n"
    "- Countries of the World (`fernandol/countries-of-the-world`): per land "
    "onder andere inwoners, regio en GDP per inwoner. Deze cijfers zijn van rond 2006.\n\n"
    "De data wordt één keer gedownload en daarna gecachet, zodat het dashboard snel blijft."
)

st.subheader("Hoe zijn ze gekoppeld?")
gekoppeld = df["Country"].notna().sum()
st.write(
    f"We koppelen op land van herkomst (Spotify) aan landnaam (landendata), "
    f"met een left join. Voor de join: {len(df)} artiesten, na de join: "
    f"{len(df)} artiesten, waarvan {gekoppeld} met een gekoppeld land. Om dat "
    f"te halen hebben we een paar landnamen gelijkgetrokken (zoals 'Korea, "
    f"South' naar 'South Korea') en Schotse artiesten gekoppeld aan het "
    f"Verenigd Koninkrijk."
)

st.subheader("Welke checks hebben we gedaan?")
KOLOMMEN = ["Total Streams (in millions)", "Debut Year", "GDP ($ per capita)", "Population"]
checks = pd.DataFrame({
    "ontbrekend": df[KOLOMMEN].isna().sum(),
    "minimum": [df[k].min() for k in KOLOMMEN],
    "maximum": [df[k].max() for k in KOLOMMEN],
})
st.dataframe(checks)
zonder_gdp = landen.loc[landen["GDP ($ per capita)"].isna(), "Country"].tolist()
st.write(
    f"Dit zijn de kolommen waar ons verhaal op draait. Er zijn "
    f"{df.duplicated().sum()} dubbele rijen bij de artiesten en "
    f"{landen.duplicated().sum()} bij de landen. In de landendata mist bij "
    f"{', '.join(zonder_gdp)} de GDP. Daar komt geen artiest vandaan, dus we "
    f"verliezen daardoor geen artiesten."
)
st.write(
    "Wat we hebben aangepast: de landendata gebruikt komma's als "
    "decimaalteken, die hebben we omgezet naar getallen. Wat we bewust niet "
    "hebben aangepast: de superstreamers (zoals Drake) laten we staan, omdat "
    "het echte artiesten zijn en geen fouten. We gebruiken daarom de mediaan "
    "in plaats van het gemiddelde."
)

st.subheader("De data")
st.dataframe(df.head(20))

st.subheader("Bronnen voor de code")
st.markdown(
    "- Kaggle API: https://github.com/Kaggle/kaggle-api\n"
    "- Streamlit pagina's en caching: https://docs.streamlit.io/develop/api-reference/navigation/st.navigation "
    "en https://docs.streamlit.io/develop/api-reference/caching-and-state/st.cache_data\n"
    "- Plotly grafieken: https://plotly.com/python/bubble-charts/, "
    "https://plotly.com/python/horizontal-bar-charts/, https://plotly.com/python/linear-fits/, "
    "https://plotly.com/python/patterns/ en https://plotly.com/python/horizontal-vertical-shapes/\n"
    "- Welvaartsgroepen met pandas.qcut: https://pandas.pydata.org/docs/reference/api/pandas.qcut.html"
)

import streamlit as st
from data import load_data, voeg_marge_toe

st.set_page_config(page_title="Spotify x Landendata", layout="wide")


def toon_home():
    st.title("Heeft welvaart invloed op het succes van artiesten?")
    st.caption("Groep 9 casus 2 · Silvi, Seif, Mohammed en Jade")
    voeg_marge_toe()

    df = load_data()
    df_gdp = df.dropna(subset=["GDP ($ per capita)"])
    correlatie = df_gdp["GDP ($ per capita)"].corr(df_gdp["Total Streams (in millions)"])

    st.metric("Correlatie GDP per capita en streams", round(correlatie, 2))
    st.caption("Tussen -1 en 1, hoe dichter bij 0 hoe zwakker het verband.")

    if correlatie > 0.3:
        eindconclusie = "Onze conclusie: welvaart in het land van herkomst hangt duidelijk samen met het succes van een artiest."
    elif correlatie > 0.1:
        eindconclusie = "Onze conclusie: welvaart speelt een klein rolletje mee in het succes van een artiest, maar verklaart het lang niet alles."
    elif correlatie < -0.1:
        eindconclusie = "Onze conclusie: artiesten uit armere landen doen het juist beter, welvaart alleen verklaart succes dus niet."
    else:
        eindconclusie = "Onze conclusie: welvaart in het land van herkomst lijkt geen duidelijke invloed te hebben op het succes van een artiest."

    st.write(eindconclusie)

    st.write(
        "Van K-pop uit Zuid-Korea tot afrobeats uit Nigeria: wij combineren de "
        "500 meest gestreamde Spotify-artiesten met landengegevens om te zien "
        "of welvaart een rol speelt in wie de wereld beluistert."
    )

    st.write(
        "Op de pagina Rijkdom en streams laten we zien hoe we tot deze "
        "conclusie zijn gekomen. Op de pagina Andere factoren kijken we ook "
        "naar andere kenmerken van het land van herkomst, zoals bevolking, "
        "taal en regio, om te checken of welvaart wel de belangrijkste "
        "verklaring is."
    )


home = st.Page(toon_home, title="Home", default=True)
rijkdom = st.Page("pages/1_Rijkdom_en_streams.py", title="Rijkdom en streams")
factoren = st.Page("pages/2_Andere_factoren.py", title="Andere factoren")
bronnen = st.Page("pages/3_Databronnen.py", title="Databronnen")

navigatie = st.navigation([home, rijkdom, factoren, bronnen])
navigatie.run()

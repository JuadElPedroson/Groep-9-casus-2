import plotly.express as px
import streamlit as st
from data import load_data, voeg_marge_toe

st.title("Andere factoren")
voeg_marge_toe()
px.defaults.template = "plotly_white"

BLAUW = "#2a78d6"
STREAMS = "Total Streams (in millions)"

st.write(
    "Hier kun je zelf kijken of andere kenmerken samenhangen met het aantal "
    "streams. We gebruiken de mediaan, zodat uitschieters het beeld niet bepalen."
)

df = load_data().copy()

KENMERKEN = {
    "Taal": "Primary Language",
    "Genre": "Primary Genre",
    "Regio": "Region",
    "Debuutjaar": "Debut Year",
    "Inwoners van het land": "Population",
    "Geletterdheid (%)": "Literacy (%)",
}
keuze = st.selectbox("Kies een kenmerk", list(KENMERKEN))
factor = KENMERKEN[keuze]

if factor in ["Population", "Literacy (%)"]:
    st.write(
        "Elke stip is een artiest. Staat de lijn schuin, dan is er een "
        "verband. Loopt hij vlak, dan maakt het kenmerk weinig uit."
    )
    data = df.dropna(subset=[factor])
    fig = px.scatter(
        data, x=factor, y=STREAMS, hover_name="Artist Name",
        trendline="ols", trendline_color_override="black",
        log_x=(factor == "Population"), log_y=True,
        color_discrete_sequence=[BLAUW], opacity=0.5,
        labels={factor: keuze, STREAMS: "streams (miljoen, log schaal)"},
    )
    r = data[factor].corr(data[STREAMS])
    sterkte = "nauwelijks" if abs(r) < 0.1 else "een zwak" if abs(r) < 0.3 else "een duidelijk"
    conclusie = f"Er is {sterkte} verband tussen {keuze.lower()} en streams (r = {r:.2f})."
    if sterkte == "nauwelijks":
        conclusie = f"Er is nauwelijks een verband tussen {keuze.lower()} en streams (r = {r:.2f})."

elif factor == "Debut Year":
    st.write("Per periode van vijf jaar: hoeveel streams haalt de middelste artiest?")
    data = df.assign(periode=(df[factor] // 5) * 5)
    per = data.groupby("periode").agg(mediaan=(STREAMS, "median"), n=(STREAMS, "size")).reset_index()
    per = per[per["n"] >= 5]  # periodes met heel weinig artiesten zijn niet betrouwbaar
    fig = px.bar(
        per, x="periode", y="mediaan", text_auto=".0f", hover_data=["n"],
        color_discrete_sequence=[BLAUW],
        labels={"periode": "debuut (periode van 5 jaar)", "mediaan": "mediane streams (miljoen)", "n": "artiesten"},
    )
    hoogste = per.loc[per["mediaan"].idxmax()]
    conclusie = (
        f"Artiesten die tussen {int(hoogste['periode'])} en {int(hoogste['periode']) + 4} "
        f"debuteerden hebben de hoogste mediaan. Kijk wel naar het aantal artiesten "
        f"per periode (zie de hover): recente artiesten hebben nog minder tijd gehad "
        f"om streams op te bouwen."
    )

else:
    st.write(
        "De balken zijn gesorteerd van hoog naar laag. Alleen groepen met "
        "minstens 5 artiesten tellen mee, anders bepaalt één artiest de hele balk."
    )
    per = (
        df.groupby(factor)
        .agg(mediaan=(STREAMS, "median"), n=(STREAMS, "size"))
        .query("n >= 5")
        .sort_values("mediaan")
        .reset_index()
    )
    fig = px.bar(
        per, x="mediaan", y=factor, orientation="h", text_auto=".0f",
        hover_data=["n"], color_discrete_sequence=[BLAUW],
        labels={"mediaan": "mediane streams (miljoen)", factor: "", "n": "artiesten"},
    )
    verschil = per["mediaan"].max() / per["mediaan"].min()
    conclusie = (
        f"{per.iloc[-1][factor]} scoort het hoogst en {per.iloc[0][factor]} het "
        f"laagst. De hoogste mediaan is {verschil:.1f} keer zo hoog als de laagste."
    )

st.plotly_chart(fig, width="stretch")
st.write(conclusie)

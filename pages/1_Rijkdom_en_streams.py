import numpy as np
import plotly.express as px
import streamlit as st
from data import load_data, load_landen, voeg_marge_toe, WELVAARTSGROEPEN

st.title("Rijkdom en streams")
voeg_marge_toe()
px.defaults.template = "plotly_white"

# Vaste kleuren: blauw = artiesten, grijs = ter vergelijking
BLAUW = "#2a78d6"
ORANJE = "#eb6834"
GRIJS = "#b4b2aa"
STREAMS = "Total Streams (in millions)"
GDP = "GDP ($ per capita)"

alle_artiesten = load_data().dropna(subset=[GDP]).copy()
landen = load_landen().dropna(subset=[GDP])

st.write(
    "We onderzoeken of artiesten uit rijkere landen meer succes hebben. "
    "Welvaart meten we met GDP per inwoner: hoeveel een land gemiddeld per "
    "persoon verdient. We hebben alle landen ter wereld daarop in vier even "
    "grote groepen verdeeld: arm, laag-midden, hoog-midden en rijk. Elke "
    "artiest krijgt de groep van zijn land van herkomst."
)
st.write(
    "Succes kun je op twee manieren bekijken: of je überhaupt in de top 500 "
    "komt, en hoeveel streams je daarna haalt. Die twee bekijken we apart, en "
    "daarna kijken we hoe artiesten uit armere landen de top toch halen. Met "
    "de filters hieronder kun je alle grafieken aanpassen."
)

# Filters: werken door in alle grafieken op deze pagina
kolom1, kolom2 = st.columns([2, 1])
min_jaar = int(alle_artiesten["Debut Year"].min())
max_jaar = int(alle_artiesten["Debut Year"].max())
jaren = kolom1.slider("Debuutjaar van de artiest", min_jaar, max_jaar, (min_jaar, max_jaar))
zonder_vs = kolom2.checkbox("Artiesten uit de VS weglaten")

df = alle_artiesten[alle_artiesten["Debut Year"].between(*jaren)]
if zonder_vs:
    df = df[df["country_mapped"] != "United States"]
if len(df) < 20:
    st.warning("Te weinig artiesten binnen deze filters, kies een groter bereik.")
    st.stop()
st.caption(f"{len(df)} van de {len(alle_artiesten)} artiesten geselecteerd.")

# ---------------------------------------------------------------------------
st.subheader("Uit welke landen komen de artiesten?")
st.write(
    "Eerst onderzoeken we of artiesten uit rijke landen vaker in de top 500 "
    "komen. Als welvaart niet uitmaakt, verwacht je dat de artiesten ongeveer "
    "net zo verdeeld zijn als de wereldbevolking. Daarom zetten we die twee "
    "per welvaartsgroep naast elkaar."
)
st.caption(
    "Zo lees je de grafiek: grijs is het deel van de wereldbevolking dat in "
    "die groep woont, blauw het deel van de artiesten dat er vandaan komt. "
    "Is blauw langer dan grijs, dan komen er meer artiesten uit die groep "
    "dan je zou verwachten."
)

bevolking = landen.groupby("Welvaartsgroep", observed=True)["Population"].sum()
artiesten = df["Welvaartsgroep"].value_counts()
verdeling = (
    (bevolking / bevolking.sum() * 100).rename("Wereldbevolking").to_frame()
    .join((artiesten / artiesten.sum() * 100).rename("Artiesten in top 500"))
    .reindex(WELVAARTSGROEPEN)
    .fillna(0)
    .reset_index()
    .melt(id_vars="Welvaartsgroep", var_name="Aandeel", value_name="procent")
)

fig1 = px.bar(
    verdeling,
    x="procent",
    y="Welvaartsgroep",
    color="Aandeel",
    barmode="group",
    orientation="h",
    text_auto=".0f",
    color_discrete_map={"Wereldbevolking": GRIJS, "Artiesten in top 500": BLAUW},
    category_orders={"Welvaartsgroep": WELVAARTSGROEPEN[::-1]},
    labels={"procent": "% van het totaal", "Welvaartsgroep": "", "Aandeel": ""},
)
fig1.update_traces(texttemplate="%{x:.0f}%", textposition="outside")
# Patroon op de bevolkingsbalken, zodat het ook zonder kleur te lezen is
fig1.for_each_trace(lambda t: t.update(marker_pattern_shape="/") if t.name == "Wereldbevolking" else None)
fig1.update_xaxes(ticksuffix="%")
fig1.update_layout(legend=dict(orientation="h", y=1.1, x=0), xaxis_range=[0, 100])

# Verhouding: hoeveel keer zo vaak komen artiesten uit rijke landen dan je
# op basis van de bevolking zou verwachten
rijk = verdeling.set_index(["Welvaartsgroep", "Aandeel"])["procent"]
verhouding = rijk["Rijk", "Artiesten in top 500"] / rijk["Rijk", "Wereldbevolking"]
fig1.add_annotation(
    x=30, y="Rijk", yshift=-14, xanchor="left", showarrow=False,
    text=f"{verhouding:.1f}x zoveel artiesten als je naar bevolking verwacht",
)
st.plotly_chart(fig1, width="stretch")

st.write(
    f"Je ziet hier dus dat de verdeling heel scheef is. In de rijkste groep "
    f"woont {rijk['Rijk', 'Wereldbevolking']:.0f}% van de wereldbevolking, "
    f"maar er komt {rijk['Rijk', 'Artiesten in top 500']:.0f}% van de artiesten "
    f"vandaan: {verhouding:.1f} keer zoveel als je zou verwachten. Bij de "
    f"armere groepen is het andersom. Conclusie: artiesten uit rijke landen "
    f"halen veel vaker de top 500."
)

# ---------------------------------------------------------------------------
st.subheader("Halen artiesten uit rijke landen ook meer streams?")
st.write(
    "Rijke landen leveren dus meer artiesten. Maar halen die artiesten ook "
    "meer streams dan artiesten uit armere landen? Dat onderzoeken we met een "
    "bellengrafiek, omdat je daarin per land tegelijk de welvaart, het aantal "
    "artiesten en het aantal streams ziet."
)
st.caption(
    "Zo lees je de grafiek: elke bol is een land. Hoe verder naar rechts, hoe "
    "rijker het land. Hoe groter de bol, hoe meer artiesten. De hoogte is de "
    "mediaan van de streams: de middelste artiest van dat land. We gebruiken "
    "de mediaan zodat uitschieters zoals Drake het beeld niet bepalen. De "
    "stippellijn is de mediaan van alle artiesten."
)

per_land = (
    df.groupby("country_mapped")
    .agg(
        gdp=(GDP, "first"),
        mediaan=(STREAMS, "median"),
        artiesten=("Artist Name", "size"),
    )
    .reset_index()
)
algemene_mediaan = df[STREAMS].median()
# Alleen een paar landen een naam geven, anders wordt het onleesbaar
MET_NAAM = {
    "United States": "VS", "United Kingdom": "VK", "Mexico": "Mexico",
    "Colombia": "Colombia", "India": "India", "South Korea": "Zuid-Korea",
    "Barbados": "Barbados (Rihanna)", "Trinidad and Tobago": "Trinidad (Nicki Minaj)",
}
per_land["label"] = per_land["country_mapped"].map(MET_NAAM).fillna("")

fig2 = px.scatter(
    per_land,
    x="gdp",
    y="mediaan",
    size="artiesten",
    size_max=45,
    text="label",
    hover_name="country_mapped",
    hover_data={"artiesten": True, "gdp": ":,.0f", "mediaan": ":,.0f", "label": False},
    color_discrete_sequence=[BLAUW],
    labels={
        "gdp": "GDP per inwoner ($)",
        "mediaan": "mediane streams per artiest (miljoen)",
        "artiesten": "aantal artiesten",
    },
)
fig2.update_traces(textposition="top center", marker=dict(opacity=0.6, line=dict(width=1, color="white")))
# Log-schaal, anders drukken Rihanna en Nicki Minaj de rest plat
fig2.update_yaxes(
    type="log",
    tickvals=[7000, 10000, 15000, 20000, 30000, 50000],
    ticktext=["7.000", "10.000", "15.000", "20.000", "30.000", "50.000"],
)
fig2.add_hline(
    y=algemene_mediaan,
    line_dash="dot",
    line_color="grey",
    annotation_text=f"mediaan alle artiesten ({algemene_mediaan:,.0f} mln)",
    annotation_position="top right",
)
st.plotly_chart(fig2, width="stretch")

r = df[GDP].corr(df[STREAMS])
q1, q3 = df[STREAMS].quantile([0.25, 0.75])
zonder = df[df[STREAMS] <= q3 + 1.5 * (q3 - q1)]
r_zonder = zonder[GDP].corr(zonder[STREAMS])
st.write(
    f"Je ziet hier dus dat arme en rijke landen ongeveer even hoog liggen, "
    f"rond de stippellijn. De hoogste bollen zijn zelfs Barbados (Rihanna) en "
    f"Trinidad (Nicki Minaj). De correlatie tussen GDP en streams is "
    f"r = {r:.2f}. r loopt van -1 tot 1, en rond 0 betekent geen verband. "
    f"Zonder de superstreamers is het r = {r_zonder:.2f}, het ligt dus niet "
    f"aan hen. Conclusie: eenmaal in de top 500 maakt welvaart nauwelijks uit "
    f"voor het aantal streams."
)

# ---------------------------------------------------------------------------
st.subheader("Hoe komen artiesten uit armere landen dan de top in?")
st.write(
    "Toch komt een deel van de artiesten uit armere landen. Hoe halen zij "
    "de top 500? Ons idee was dat taal een rol speelt: wie in een grote taal "
    "zingt, heeft een groot publiek. Daarom kijken we per welvaartsgroep in "
    "welke taal de artiesten zingen."
)
st.caption(
    "Zo lees je de grafiek: elke balk is een welvaartsgroep en telt op tot "
    "100%. De kleuren laten zien welk deel Engels, Spaans of een andere taal "
    "zingt. De twee armste groepen zijn samengevoegd omdat daar weinig "
    "artiesten in zitten."
)

taal = df.copy()
taal["groep"] = taal["Welvaartsgroep"].astype(str).replace({"Arm": "Arm + laag-midden", "Laag-midden": "Arm + laag-midden"})
taal["taal"] = taal["Primary Language"].where(taal["Primary Language"].isin(["English", "Spanish"]), "Overig")
taal["taal"] = taal["taal"].replace({"English": "Engels", "Spanish": "Spaans"})
aandeel = (
    taal.groupby(["groep", "taal"]).size()
    .groupby(level=0).transform(lambda s: s / s.sum() * 100)
    .rename("procent").reset_index()
)
aantal = taal["groep"].value_counts()
aandeel["groep_label"] = aandeel["groep"] + " (" + aandeel["groep"].map(aantal).astype(str) + " artiesten)"
volgorde = [f"{g} ({aantal[g]} artiesten)" for g in ["Rijk", "Hoog-midden", "Arm + laag-midden"] if g in aantal]

fig3 = px.bar(
    aandeel,
    x="procent",
    y="groep_label",
    color="taal",
    orientation="h",
    text_auto=".0f",
    color_discrete_map={"Engels": BLAUW, "Spaans": ORANJE, "Overig": GRIJS},
    category_orders={"groep_label": volgorde, "taal": ["Engels", "Spaans", "Overig"]},
    labels={"procent": "% van de artiesten in deze groep", "groep_label": "", "taal": ""},
)
fig3.update_traces(texttemplate="%{x:.0f}%", textposition="inside")
# Patroon op Spaans, zodat het ook zonder kleur te onderscheiden is
fig3.for_each_trace(lambda t: t.update(marker_pattern_shape="/") if t.name == "Spaans" else None)
fig3.update_layout(legend=dict(orientation="h", y=1.12, x=0), bargap=0.35)
st.plotly_chart(fig3, width="stretch")

spaans = aandeel.query("groep == 'Hoog-midden' and taal == 'Spaans'")["procent"]
spaans_midden = spaans.iloc[0] if len(spaans) > 0 else 0
st.write(
    f"Je ziet hier dus dat artiesten uit rijke landen vooral in het Engels "
    f"zingen. In de hoog-middengroep zingt {spaans_midden:.0f}% Spaans "
    f"(Mexico, Colombia, Argentinië) en in de armste groepen gaat het vooral "
    f"om Indiase artiesten (Hindi, Tamil, Punjabi). Conclusie: artiesten uit "
    f"armere landen komen de top vooral in via een grote eigen taalmarkt."
)

# ---------------------------------------------------------------------------
st.subheader("Conclusie")

# Alternatieve verklaringen checken op alle artiesten (los van de filters)
def aandeel_rijk(data):
    return (data["Welvaartsgroep"] == "Rijk").mean() * 100

rijk_zonder_vs = aandeel_rijk(alle_artiesten[alle_artiesten["country_mapped"] != "United States"])
rijk_na_2010 = aandeel_rijk(alle_artiesten[alle_artiesten["Debut Year"] >= 2010])

st.write(
    f"Onze vraag was of welvaart invloed heeft op het succes van artiesten. "
    f"Het antwoord is ja, maar vooral op wie de top 500 haalt: "
    f"{rijk['Rijk', 'Artiesten in top 500']:.0f}% van de artiesten komt uit het "
    f"rijkste kwart van de landen. Eenmaal in de top 500 maakt het nauwelijks "
    f"uit (r = {r:.2f}). Artiesten uit armere landen komen er vooral in via "
    f"Spaanstalige of Indiase muziek."
)
st.write(
    f"Komt dit alleen door de VS? Nee, zonder de VS komt nog steeds "
    f"{rijk_zonder_vs:.0f}% uit een rijk land. En bij artiesten die na 2010 "
    f"debuteerden, in de tijd van streaming, is dat {rijk_na_2010:.0f}%. Het "
    f"patroon blijft dus staan."
)
st.write(
    "Kanttekeningen: we zien alleen artiesten die de top al gehaald hebben, "
    "de landendata is van rond 2006, en het land van herkomst zegt niets "
    "over waar de luisteraars wonen."
)

import streamlit as st
from data import load_data
import plotly.express as px
 
df = load_data()
 
st.title("Gelettertheid en verbinding vs streams")
 
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




df = load_data()

st.caption("""
Geletterdheid en telefoonbezit hangen sterk samen: landen met hoge geletterdheid 
(rechts in de grafiek) hebben vrijwel altijd ook veel telefoons per 1000 inwoners. 
De grootste bubbel (Noord-Amerika, rechtsboven) combineert de hoogste score op beide 
indicatoren mét de meeste streams. Landen met lage geletterdheid en weinig telefoons 
(linksonder, vooral Sub-Sahara Afrika) hebben zichtbaar kleinere bubbels, dit 
ondersteunt het beeld dat welvaart/ontwikkeling en streamingsucces samenhangen.
""")
import streamlit as st
from data import load_data

st.title("Databronnen")

st.write("Hieronder staan de bronnen die we voor dit dashboard hebben gebruikt.")

st.write("""
Anthropic. (2026). Claude (Sonnet 5) [Large language model]. https://claude.ai. Gebruikt voor de koppeling met de Kaggle API om de data op te halen en als ondersteuning bij de rest van de code.

Countries of the World. (n.d.). Retrieved September 23, 2026, from https://www.kaggle.com/datasets/fernandol/countries-of-the-world

Most Streamed Artists on Spotify. (n.d.). Retrieved September 23, 2026, from https://www.kaggle.com/datasets/rishavsvault/most-streamed-artists-on-spotify

Streamlit • A faster way to build and share data apps. (2021, January 14). https://streamlit.io/

""")

df = load_data()
st.dataframe(df.head(20))

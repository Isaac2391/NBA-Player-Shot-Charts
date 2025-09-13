import streamlit as st 
import script
import matplotlib.pyplot as plt

st.title("NBA Shot Graphs and Metrics")

player_name = st.text_input("Player Name")
season = st.text_input("Season (e.g. 2023-24)")

if player_name and season:
    if st.button("Generate Shot Chart"):
        script.renderGraph(player_name, season)
        st.pyplot(plt)
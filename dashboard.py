import streamlit as st 
import script
import matplotlib.pyplot as plt

st.title("NBA Shot Graphs and Metrics")

player_name = st.text_input("Player Name")
season = st.text_input("Season, formated as YYYY/YY (e.g. 2023-24)")

try:
    if player_name and season:
        if st.button("Generate Shot Chart"):
         script.renderGraph(player_name, season)
         st.pyplot(plt)
except(IndexError):
    st.header("Couldnt Find Player Name (mispelled or nickname instead of actual name?)")

EFGPerc,TrueShootingPerc,FreeThrowRate,HollingerAstRatio,TurnoverPerc = script.renderStats(player_name)

st.header("Career Stats")

st.header("Effective Field Goal Percentage (eFG%)")
st.text("Adjusts a player’s or team’s FG% for the fact that a 3 pointer is worth 1.5 times a standard FG")
st.text(f"{EFGPerc}")

st.header("True Shooting Percentage (TS%)")
st.text("Adjusts a player’s or team’s FG% for the fact that a 3 pointer is worth 1.5 times a standard FG")
st.text(f"{TrueShootingPerc}")

st.header("Free Throw Rate (FTR)")
st.text("A measure of both how often a player/team gets to the line, as well as how often they make their free throws")
st.text(f"{FreeThrowRate}")

st.header("Hollinger Assist Ratio")
st.text("Think of Carmelo Anthony for this statistic, it is a “ball stopper” stat. This divides the number of assists a player has by the number of offensive possessions that end in that player’s hands.")
st.text(f"{HollingerAstRatio}")

st.header("Turnover Percentage (TOV%)")
st.text("Percent of a player’s possessions that ends in turnovers, essentially the same as the hAST% equation, but for turnovers rather than assists")
st.text(f"{TurnoverPerc}")
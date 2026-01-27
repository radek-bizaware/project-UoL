import streamlit as st
import pypokedex
import pandas as pd
st.set_page_config(page_title="Pokemon Guessing Game")
st.title("Welcome to the most amazing Pokemon Guessing Game")
st.write("The rules are simple: guess as many as you can!")

Guessed_Pokemons = []
Leaderboard = pd.read_csv('Scoreboard.csv')
top20 = Leaderboard.sort_values('Score', ascending=False).head(20)
st.dataframe(top20)
Player_Name = name = st.text_input("Name", placeholder="Type your name here")
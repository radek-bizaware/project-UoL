import streamlit as st
import pypokedex
st.set_page_config(page_title="Pokemon Guessing Game")
st.title("Welcome to the most amazing Pokemon Guessing Game")
st.write("streamlit is working")

Guessed_Pokemons = []
Leaderboard = []
Player_Name = name = st.text_input("Name", placeholder="Type your name here")
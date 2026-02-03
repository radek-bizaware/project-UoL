import streamlit as st
import pypokedex
import pandas as pd

st.set_page_config(page_title="Pokemon Guessing Game")
st.title("Welcome to the most amazing Pokemon Guessing Game")
st.write("The rules are simple: guess as many as you can!")

# initialise first
if "Guessed_Pokemons" not in st.session_state:
    st.session_state["Guessed_Pokemons"] = []

Game_Guesses = st.session_state["Guessed_Pokemons"]

Leaderboard = pd.read_csv('Scoreboard.csv')
top20 = Leaderboard.sort_values('Score', ascending=False).head(20)
st.table(top20)

Player_Name = st.text_input("Name", placeholder="Type your name here")
show_panel = bool(Player_Name.strip())

if show_panel:
    st.markdown("---")
    st.subheader("🎮 Game Panel")

    st.write(f"Welcome, **{Player_Name}**. Start guessing!")

    with st.form("guess_form", clear_on_submit=True):
        guess = st.text_input("Can you guess any Pokémon?")
        submitted = st.form_submit_button("Add (or press Enter)")

        if submitted and guess.strip():
            st.session_state["Guessed_Pokemons"].append(guess.strip().lower())

    st.write("Your guesses:", st.session_state["Guessed_Pokemons"])







import streamlit as st
import pypokedex
import pandas as pd
st.set_page_config(page_title="Pokemon Guessing Game")
st.title("Welcome to the most amazing Pokemon Guessing Game")
st.write("The rules are simple: guess as many as you can!")

Guessed_Pokemons = []
Leaderboard = pd.read_csv('Scoreboard.csv')
top20 = Leaderboard.sort_values('Score', ascending=False).head(20)
st.table(top20)
Player_Name = name = st.text_input("Name", placeholder="Type your name here")
if "show_section" not in st.session_state:
    st.session_state["show_section"] = False

if st.button("Start New Game"):
    st.session_state["show_section"] = True


# ---- FORM ----
with st.form("guess_form", clear_on_submit=True):
    guess = st.text_input("Can you guess any Pokémon?")
    submitted = st.form_submit_button("Add (or press Enter)")

    if submitted and guess:
        st.session_state.Guessed_Pokemons.append(guess.strip().lower())

# ---- DISPLAY LIST ----
st.subheader("Your guesses")
st.write(st.session_state.Guessed_Pokemons)

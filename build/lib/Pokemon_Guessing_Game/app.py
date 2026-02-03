import streamlit as st
import pypokedex
import pandas as pd
import time


st.set_page_config(page_title="Pokemon Guessing Game")
st.title("Can you guess em all")
st.write("The rules are simple: guess as many as you can!")

df = pd.read_csv("Scoreboard.csv")
top = df.sort_values("Score", ascending=False).head(5).reset_index(drop=True)

c1, c2, c3 = st.columns(3)
c1.metric("🥇 1st", top.loc[0, "Player"], int(top.loc[0, "Score"]))
c2.metric("🥈 2nd", top.loc[1, "Player"], int(top.loc[1, "Score"]))
c3.metric("🥉 3rd", top.loc[2, "Player"], int(top.loc[2, "Score"]))

# initialise first
if "Guessed_Pokemons" not in st.session_state:
    st.session_state["Guessed_Pokemons"] = []

Game_Guesses = st.session_state["Guessed_Pokemons"]




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







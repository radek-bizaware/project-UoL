import streamlit as st
import pypokedex
import pandas as pd
import time


st.set_page_config(page_title="Pokemon Guessing Game")
st.title("Can you guess em all")
st.write("The rules are simple: guess as many as you can!")


def leaderboard(pathway_to_csv="Scoreboard.csv", title="Pokemon Guessing Game"):
    st.subheader(f"🏆 {title} Leaderboard")

    try:
        df = pd.read_csv(pathway_to_csv)

        if df.empty:
            st.info("No scores recorded yet.")
            return

        top = (
            df.sort_values("Score", ascending=False)
              .head(5)
              .reset_index(drop=True)
        )

        # --- Top 3 Podium ---
        if len(top) >= 3:
            c1, c2, c3 = st.columns(3)

            c1.metric(
                "🥇 1st",
                top.loc[0, "Player"],
                int(top.loc[0, "Score"])
            )

            c2.metric(
                "🥈 2nd",
                top.loc[1, "Player"],
                int(top.loc[1, "Score"])
            )

            c3.metric(
                "🥉 3rd",
                top.loc[2, "Player"],
                int(top.loc[2, "Score"])
            )

        # --- Remaining Top 5 Table ---
        if len(top) > 3:
            st.markdown("### Other Top Players")
            st.table(top.iloc[3:])

    except FileNotFoundError:
        st.warning("Scoreboard file not found.")
    except Exception as e:
        st.error(f"Something went wrong: {e}")

 # --- Remaining Top 5 Table ---
        if len(top) > 3:
            st.markdown("### Other Top Players")
            st.table(top.iloc[3:])

    except FileNotFoundError:
        st.warning("Scoreboard file not found.")
    except Exception as e:
        st.error(f"Something went wrong: {e}")

leaderboard()


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







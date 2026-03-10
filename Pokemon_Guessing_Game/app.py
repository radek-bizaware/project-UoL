import difflib
import re
import time
from datetime import datetime, timezone

import pandas as pd
import pypokedex
import streamlit as st

st.set_page_config(page_title="Pokemon Guessing Game")
st.title("Can you guess 'em all?")
st.write("The rules are simple: pick a time limit, type Pokémon names, submit — get scored!")

SCOREBOARD_PATH = "Scoreboard.csv"


def leaderboard(pathway_to_csv: str = SCOREBOARD_PATH, title: str = "Pokemon Guessing Game") -> None:
    st.subheader(f"🏆 {title} Leaderboard")

    # ensure file exists with header
    try:
        df = pd.read_csv(pathway_to_csv)
    except FileNotFoundError:
        # create an empty leaderboard file so subsequent writes persist
        pd.DataFrame(columns=["Player", "Score", "When"]).to_csv(pathway_to_csv, index=False)
        st.info("No scores recorded yet.")
        return
    except Exception as e:
        st.error(f"Couldn't read scoreboard: {e}")
        return

    if df.empty:
        st.info("No scores recorded yet.")
        return

    top = df.sort_values("Score", ascending=False).head(5).reset_index(drop=True)

    cols = st.columns(3)
    for i in range(3):
        if i < len(top):
            cols[i].metric(f"{['🥇', '🥈', '🥉'][i]} {i + 1}th", top.loc[i, "Player"], int(top.loc[i, "Score"]))

    if len(top) > 3:
        st.markdown("### Other Top Players")
        st.table(top.iloc[3:])


def save_score(player: str, score: int, pathway_to_csv: str = SCOREBOARD_PATH):
    now = datetime.now(timezone.utc).isoformat()
    row = {"Player": player, "Score": score, "When": now}
    # read existing data, append, and persist immediately
    try:
        df = pd.read_csv(pathway_to_csv)
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    except FileNotFoundError:
        # if somehow file disappeared, rebuild header and row
        df = pd.DataFrame([row])
    df.to_csv(pathway_to_csv, index=False)


# --- Initialize session state ---
if "guessed_correct" not in st.session_state:
    st.session_state.guessed_correct = []  # list of dicts: name, types, generation, score
if "tried" not in st.session_state:
    st.session_state.tried = set()
if "game_active" not in st.session_state:
    st.session_state.game_active = False


with st.sidebar:
    st.header("Game Settings")
    duration = st.selectbox("Duration (seconds)", options=[30, 60, 120], index=1)
    difficulty = st.selectbox("Difficulty", options=["Easy", "Normal", "Hard"], index=1)
    gen_choice = st.selectbox("Generation", options=["All", "1", "2", "3", "4", "5", "6", "7", "8"], index=0)
    show_missed = st.checkbox("Show missed suggestions after game", value=True)
    allow_hints = st.checkbox("Enable spelling hints", value=True)

leaderboard()
st.markdown("---")
Player_Name = st.text_input("Name", placeholder="Type your name here")
start_button = st.button("Start Game")


def _get_generation_number(pokemon_obj):
    gen = getattr(pokemon_obj, "generation", None)
    if gen is None:
        return None
    try:
        if hasattr(gen, "name"):
            s = str(gen.name)
        else:
            s = str(gen)
        m = re.search(r"(\d+)", s)
        if m:
            return int(m.group(1))
    except Exception:
        return None
    return None


def try_validate_guess(raw_guess: str, gen_choice: str, difficulty: str):
    guess = raw_guess.strip().lower()
    if not guess or guess in st.session_state.tried:
        return None, "duplicate-or-empty"

    st.session_state.tried.add(guess)

    # try to fetch pokemon
    p = None
    try:
        p = pypokedex.get(name=guess)
    except Exception:
        try:
            p = pypokedex.get(name=guess.capitalize())
        except Exception:
            # not found — consider spelling hints
            return None, "not-found"

    # filter by generation if selected
    sel_gen = gen_choice
    gen_num = _get_generation_number(p)
    if sel_gen != "All" and gen_num is not None and int(sel_gen) != int(gen_num):
        return None, "wrong-gen"

    # build details safely
    name = getattr(p, "name", None) or guess
    types = getattr(p, "types", None)
    if types is None:
        types = getattr(p, "type", [])
    try:
        types_list = [t.name if hasattr(t, "name") else str(t) for t in types]
    except Exception:
        types_list = [str(types)] if types else []

    generation = getattr(p, "generation", None)
    pokedex_number = getattr(p, "dex", None) or getattr(p, "pokedex_number", None) or getattr(p, "national_id", None)

    details = {
        "name": name,
        "types": types_list,
        "generation": generation,
        "dex": pokedex_number,
    }

    # compute score for this pokemon based on difficulty and rarity
    base = 1
    rarity_bonus = 0
    try:
        if getattr(p, "is_legendary", False):
            rarity_bonus += 5
    except Exception:
        pass
    try:
        dex_val = int(pokedex_number) if pokedex_number else 0
    except Exception:
        dex_val = 0
    if dex_val >= 800:
        rarity_bonus += 3
    elif dex_val >= 700:
        rarity_bonus += 2
    elif dex_val >= 500:
        rarity_bonus += 1

    multiplier = {"Easy": 0.8, "Normal": 1.0, "Hard": 1.2}.get(difficulty, 1.0)
    score_for_pokemon = int(round((base + rarity_bonus) * multiplier))
    details["score"] = score_for_pokemon

    # avoid duplicates in correct list
    if any(d["name"].lower() == name.lower() for d in st.session_state.guessed_correct):
        return None, "already-correct"

    st.session_state.guessed_correct.append(details)
    return details, "ok"


def _build_name_list_for_gen(gen):
    # return list of lowercase pokemon names for a generation; cached in session
    gen_ranges = {
        "1": (1, 151),
        "2": (152, 251),
        "3": (252, 386),
        "4": (387, 493),
        "5": (494, 649),
        "6": (650, 721),
        "7": (722, 809),
        "8": (810, 898),
    }
    key = gen or "All"
    if "pokemon_names_cache" not in st.session_state:
        st.session_state.pokemon_names_cache = {}

    if key in st.session_state.pokemon_names_cache:
        return st.session_state.pokemon_names_cache[key]

    names = []
    if gen == "All":
        ranges = [(1, 898)]
    else:
        ranges = [gen_ranges.get(gen, (1, 151))]

    for r in ranges:
        for i in range(r[0], r[1] + 1):
            try:
                p = pypokedex.get(dex=i)
                n = getattr(p, "name", None)
                if n:
                    names.append(n.lower())
            except Exception:
                continue

    st.session_state.pokemon_names_cache[key] = names
    return names


st.header("🎮 Game Panel")
if not Player_Name.strip():
    st.info("Enter your name in the box above to enable the game.")
else:
    if start_button and Player_Name.strip():
        st.session_state.game_active = True
        st.session_state.end_time = time.time() + int(duration)
        st.session_state.guessed_correct = []
        st.session_state.tried = set()

    if st.session_state.get("game_active") and time.time() < st.session_state.get("end_time", 0):
        remaining = int(st.session_state.end_time - time.time())
        st.metric("Time remaining (s)", remaining)

        with st.form("guess_form", clear_on_submit=True):
            guess = st.text_input("Enter a Pokémon name:")
            submitted = st.form_submit_button("Submit")
            if submitted and guess:
                details, status = try_validate_guess(guess, gen_choice, difficulty)
                if status == "ok":
                    st.success(f"Correct — {details['name'].title()}! (+{details['score']} pts)")
                elif status == "duplicate-or-empty":
                    st.warning("Empty guess or already tried this name.")
                elif status == "already-correct":
                    st.info("You already guessed that Pokémon correctly.")
                elif status == "wrong-gen":
                    st.warning("That Pokémon is not in the selected generation.")
                else:
                    # not found — give spelling hints if enabled
                    st.error("Not a valid Pokémon name.")
                    if allow_hints:
                        names = _build_name_list_for_gen(gen_choice)
                        if not names:
                            st.warning(
                                "Hint list empty (generation filter may be too restrictive). Try 'All' or restart the app."
                            )
                        # use a slightly lower cutoff to improve coverage
                        suggestions = difflib.get_close_matches(guess.lower(), names, n=5, cutoff=0.6)
                        if suggestions:
                            st.info("Did you mean: " + ", ".join([s.title() for s in suggestions]))
                        else:
                            st.info("No close matches found. Check your spelling or try a different generation.")

        st.write("Correct guesses:", [d["name"].title() for d in st.session_state.guessed_correct])
        st.write("Tried (including incorrect):", sorted(list(st.session_state.tried)))

        # countdown should tick even if user doesn't submit; pause then rerun
        time.sleep(1)
        try:
            st.experimental_rerun()
        except AttributeError:
            pass
    else:
        # game not active or finished
        if st.session_state.get("game_active"):
            # game just finished
            total_score = sum(d.get("score", 1) for d in st.session_state.guessed_correct)
            st.success(f"Time's up! You scored {total_score} points.")

            if Player_Name.strip():
                save_score(Player_Name.strip(), total_score)

            if st.session_state.guessed_correct:
                df_results = pd.DataFrame(st.session_state.guessed_correct)
                df_results_display = df_results.copy()
                df_results_display["types"] = df_results_display["types"].apply(
                    lambda x: ", ".join(x) if isinstance(x, (list, tuple)) else x
                )
                st.markdown("### Your Correct Guesses")
                st.table(df_results_display)

                csv = df_results_display.to_csv(index=False)
                st.download_button("Download your results", csv, file_name=f"{Player_Name}_pokemon_results.csv")

            if show_missed:
                st.markdown("### Missed and Hints")
                st.info("Try again with a different generation or use hints to help with spelling.")

        # reset flags so next run is clean
        st.session_state.game_active = False
        st.session_state.end_time = 0


st.markdown("---")
st.markdown("### Leaderboard")
leaderboard()

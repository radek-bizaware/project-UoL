import os
import pandas as pd
from Pokemon_Guessing_Game import app

def test_leaderboard():
    # create a temporary csv path
    tmp = "tmp_scores.csv"
    if os.path.exists(tmp):
        os.remove(tmp)

    # calling leaderboard on missing file should create one and return gracefully
    app.leaderboard(pathway_to_csv=tmp, title="Test")
    assert os.path.exists(tmp)
    df = pd.read_csv(tmp)
    assert list(df.columns) == ["Player","Score","When"]

    # saving a score should append a row
    app.save_score("foo", 10, pathway_to_csv=tmp)
    df2 = pd.read_csv(tmp)
    assert len(df2) == 1
    assert df2.loc[0, "Player"] == "foo"
    assert df2.loc[0, "Score"] == 10

    # cleanup
    os.remove(tmp)



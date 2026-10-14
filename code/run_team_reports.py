"""Build the team reports outside the notebook, one team per fresh Python process.

The team look-ups (team_id -> team, team_id -> league) are built here from the StatsBomb match details,
the same way as in the notebook, so nothing has to be saved from the notebook first.
Each team is built in its own process that ends when the team is done, so memory goes back to zero
between teams and can never pile up.

Close VS Code (or at least shut down the notebook kernel). Open a terminal (e.g. Anaconda Prompt),
go to the SAME folder as the notebook (so the relative figure paths still point to your plots), then:

    python run_team_reports.py 746             -> one team first, to check it works
    python run_team_reports.py 746 749 968     -> only these team ids (e.g. the teams for the write-up)
    python run_team_reports.py                 -> every team
"""
import os
import subprocess
import sys
os.chdir(os.path.dirname(os.path.abspath(__file__)))   # notebook's folder, before anything else loads

import matplotlib
matplotlib.use("Agg")                                  # must come before functions_analysis loads pyplot
import pandas as pd
from statsbombpy import sb

from functions_analysis import export_team_reports

# ---- edit these lines ----------------------------------------------------------------------------------------------
season_2324 = "2023/2024"             # same as `season_id_2324` in your notebook
season_id_2324 = 281
leagues = [
    ("England", "FA Women's Super League", 37),
    ("Spain", "Liga F", 182),
    ("Germany", "Frauen Bundesliga", 135),
    ("Italy", "Serie A Women", 131),
]
report_options = {}            # e.g. {"ks": (2, 3), "exclude": (r"_raw",)} for the compact report
# ---------------------------------------------------------------------------------------------------------------------

def team_maps():
    """team_id -> team and team_id -> league, from the match details of every league."""
    match_details = {}
    for country, competition_name, competition_id in leagues:
        match_details_league = sb.matches(competition_id=competition_id, season_id=season_id_2324)
        match_details[competition_name] = match_details_league
    all_match_details = pd.concat(match_details.values(), ignore_index=True)
 
    team_id_to_team = (all_match_details[['home_team_id', 'home_team']]
                       .drop_duplicates()
                       .set_index('home_team_id')['home_team']
                       .to_dict())
    team_id_to_league = (all_match_details[['home_team_id', 'competition_name']]
                         .drop_duplicates()
                         .set_index('home_team_id')['competition_name']
                         .to_dict())
    return team_id_to_team, team_id_to_league

def main(args):
    try:
        sys.stdout.reconfigure(errors="replace")                     # team names with accents in any console
    except Exception:
        pass 
    if args[:1] == ["--one"]:                                        # child: --one <team_id> <team> <league>
        team_id = int(args[1])
        export_team_reports({team_id: args[2]}, {team_id: args[3]}, **report_options)
        return
 
    team_id_to_team, team_id_to_league = team_maps()
    print(f"{len(team_id_to_team)} teams in {len(set(team_id_to_league.values()))} leagues", flush=True)
    ids = [int(a) for a in args] or list(team_id_to_team)
    missing = [t for t in ids if t not in team_id_to_team]
    if missing:
        print(f"not in the match details, skipped: {', '.join(map(str, missing))}", flush=True)
    ids = sorted((t for t in ids if t in team_id_to_team), key=lambda t: (str(team_id_to_league.get(t, "")), t))
 
    failed = []
    for i, t in enumerate(ids, 1):
        team, league = str(team_id_to_team[t]), str(team_id_to_league.get(t, ""))
        print(f"[{i}/{len(ids)}] {team}", flush=True)
        r = subprocess.run([sys.executable, os.path.abspath(__file__), "--one", str(t), team, league])
        if r.returncode != 0:
            failed.append(team)
            print(f"  -> stopped with code {r.returncode}, moving on", flush=True)
    print(f"Done: {len(ids) - len(failed)} of {len(ids)} teams ran"
          + (f"; failed: {', '.join(failed)}" if failed else ""))
 
if __name__ == "__main__":
    main(sys.argv[1:])
import os

import pandas as pd 
import numpy as np

from math import pi
from scipy import stats, spatial, optimize

import re
import gc
import glob
import io

import textwrap

import warnings

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrow, PathPatch, Rectangle, Arc, Circle, Patch, Polygon
from matplotlib.path import Path
from matplotlib.transforms import blended_transform_factory
from matplotlib.colors import to_rgba
from matplotlib.backends.backend_pdf import PdfPages
from mplsoccer import Radar, grid as mplgrid

from pypdf import PdfReader, PdfWriter
from pypdf.annotations import Link
from pypdf.generic import ArrayObject, NumberObject, NameObject

from PIL import Image

from itertools import combinations

from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression, HuberRegressor
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, silhouette_samples, davies_bouldin_score, adjusted_rand_score

from IPython.display import display

keys = ["player_id", "team_id", "position_group"]

qualifying_play_patterns = ["From Kick Off", "From Keeper", "From Free Kick", "From Throw In", "From Goal Kick"]

aerial_won_cols = ["clearance_aerial_won", "miscontrol_aerial_won", "pass_aerial_won", "shot_aerial_won"]

_action_cols = ["match_id", "team_id", "possession", "elapsed_min"]

suffix_labels = {'': 'raw', '_adj': 'adj', '_subcluster_adj': 'subcluster_adj'}

value_labels = {'': 'raw values', '_adj': 'adjusted values', '_subcluster_adj': 'sub-cluster adjusted values'}

def safe_name(division):
    return division.replace(' ', '_')  # matches what you originally saved with

def time_to_minutes(t):
    if pd.isna(t):
        return np.nan
    mm, ss = t.split(':')
    return int(mm) + int(ss) / 60

def build_match_time_anchors(events_dfs):
    events_all = pd.concat(
        [df[['match_id', 'period', 'minute', 'second', 'type']] for df in events_dfs],
        ignore_index=True
    )
    events_all['clock_min'] = events_all['minute'] + events_all['second'] / 60

    half_end = events_all[events_all['type'] == 'Half End']

    period1_end = (half_end[half_end['period'] == 1]
                   .groupby('match_id')['clock_min'].first())
    period2_offset = period1_end - 45

    match_end_raw = (half_end[half_end['period'] == 2]
                     .groupby('match_id')['clock_min'].first())
    match_end = match_end_raw + match_end_raw.index.map(period2_offset).fillna(0)
    match_end = match_end.dropna()

    return period1_end, match_end, match_end_raw, period2_offset

def add_elapsed_time(df, period2_offset_map):
    df = df.copy()
    raw_time = df['minute'] + df['second'] / 60
    offset = df['match_id'].map(period2_offset_map).fillna(0)
    df['elapsed_min'] = np.where(df['period'] == 2, raw_time + offset, raw_time)
    return df

# --------------------------------------------------------------------------- #
# 1. Timeline + stints (your code, with the NEW lines)
# --------------------------------------------------------------------------- #
def build_formation_timeline(match_id, team_id, events_df, all_position_slots):
    team_events = events_df[
        (events_df["match_id"] == match_id) & (events_df["team_id"] == team_id)
    ].sort_values("index")
 
    timeline_rows = []
    current_state = {slot: None for slot in all_position_slots}
    current_formation = None                                                    # NEW
 
    for _, row in team_events.iterrows():
        if row["type"] in ["Starting XI", "Tactical Shift"]:
            lineup = row["tactics"]["lineup"]
            current_formation = row["tactics"]["formation"]                     # NEW
            current_state = {slot: None for slot in all_position_slots}
            sent_off_ids = team_events[
                (team_events["type"] == "Red Card") & (team_events["elapsed_min"] <= row["elapsed_min"])
            ]["player_id"].tolist()
 
            for entry in lineup:
                if entry["player"]["id"] not in sent_off_ids:
                    current_state[entry["position"]["name"]] = entry["player"]["id"]
 
        elif row["type"] == "Substitution":
            outgoing_id = row["player_id"]
            incoming_id = row["substitution_replacement_id"]
            for slot, occupant in current_state.items():
                if occupant == outgoing_id:
                    current_state[slot] = incoming_id
                    break
 
        elif row["type"] in ["Player Off", "Red Card"]:  # both remove a player from the pitch
            for slot, occupant in current_state.items():
                if occupant == row["player_id"]:
                    current_state[slot] = None
                    break
 
        elif row["type"] == "Player On":
            current_state[row["position"]] = row["player_id"]
 
        snapshot = current_state.copy()
        snapshot["timestamp"] = row["elapsed_min"]
        snapshot["event_type"] = row["type"]
        snapshot["formation"] = current_formation                               # NEW
        timeline_rows.append(snapshot)
 
    return pd.DataFrame(timeline_rows)

def build_final_stints(formation_timeline, all_position_slots, match_end):
    """Your stint code, wrapped. Returns (final_stints, formation_timeline_with_checkpoints)."""
    ft = formation_timeline.sort_values(["match_id", "team_id", "timestamp"]).reset_index(drop=True)
    ft["checkpoint_id"] = ft.groupby(["match_id", "team_id"]).cumcount() + 1
    ft["end_time"] = ft.groupby(["match_id", "team_id"])["timestamp"].shift(-1)
    ft["end_time"] = ft["end_time"].fillna(ft["match_id"].map(match_end))
    # NEW: groupby silently drops NaN keys, so check formation here, before melt/groupby
    assert ft["formation"].notna().all(), "checkpoints without a formation (team-match with no Starting XI?)"
    ft["formation"] = ft["formation"].astype(int)
 
    formation_long = ft.melt(
        id_vars=["match_id", "team_id", "checkpoint_id", "timestamp", "end_time", "event_type",
                 "formation"],                                                  # NEW: formation
        value_vars=all_position_slots,
        var_name="position_name", value_name="player_id",
    ).dropna(subset=["player_id"])
    formation_long = formation_long.sort_values(["match_id", "team_id", "player_id", "checkpoint_id"])
    grp = ["match_id", "team_id", "player_id"]
    formation_long["prev_position"] = formation_long.groupby(grp)["position_name"].shift(1)
    formation_long["prev_checkpoint"] = formation_long.groupby(grp)["checkpoint_id"].shift(1)
    formation_long["prev_formation"] = formation_long.groupby(grp)["formation"].shift(1)   # NEW
    formation_long["new_stint"] = (
        formation_long["prev_checkpoint"].isna()
        | (formation_long["position_name"] != formation_long["prev_position"])
        | (formation_long["checkpoint_id"] != formation_long["prev_checkpoint"] + 1)
        | (formation_long["formation"] != formation_long["prev_formation"])                # NEW
    )
    formation_long["stint_id"] = formation_long.groupby(grp)["new_stint"].cumsum()
 
    final_stints = (formation_long
                    .groupby(["match_id", "team_id", "player_id", "position_name", "formation", "stint_id"])  # NEW: formation
                    .agg(from_min=("timestamp", "min"), to_min=("end_time", "max"))
                    .reset_index())
    final_stints["duration"] = final_stints["to_min"] - final_stints["from_min"]
 
    return final_stints, ft

def position_group_minutes_by_formation(final_stints: pd.DataFrame) -> pd.DataFrame:
    """One row per (player, team, position_group, formation): her minutes in that position group
    while her team played that formation. Unlike player_slot_by_formation (grain: player x formation
    x exact slot), this collapses slots, so a player who rotated RCB/LCB within one formation gets ONE
    row per formation - the grain team_position_shares_by_formation (team_profile.py) needs."""
    fs = final_stints[final_stints["duration"] > 0]
    return (fs.groupby(keys + ["formation"], as_index=False)["duration"].sum()
              .rename(columns={"duration": "minutes"}))

# --------------------------------------------------------------------------- #
# 2. Team formation usage (clock time, counted once per team-match)
# --------------------------------------------------------------------------- #
def team_formation_minutes(formation_timeline: pd.DataFrame, regular_share: float = 0.10) -> pd.DataFrame:
    """Team clock-minutes per formation. Needs the timeline returned by build_final_stints
    (checkpoint durations = end_time - timestamp, so a formation is counted once per team-match,
    not once per player). `regular_share` flags formations used for >= that share of team minutes."""
    ft = formation_timeline.copy()
    ft["minutes"] = ft["end_time"] - ft["timestamp"]
    out = ft.groupby(["team_id", "formation"], as_index=False).agg(
        minutes=("minutes", "sum"), n_matches=("match_id", "nunique"))
    out["share"] = out["minutes"] / out.groupby("team_id")["minutes"].transform("sum")
    out["is_regular"] = out["share"] >= regular_share
    return out.sort_values(["team_id", "minutes"], ascending=[True, False]).reset_index(drop=True)
 
 
# --------------------------------------------------------------------------- #
# 3. Player slot profiles (overall and per formation)
# --------------------------------------------------------------------------- #
def player_slot_profile(final_stints: pd.DataFrame, league_map=None):
    """Overall slot split within each (player, team, position_group).
    Returns (long, wide). Shares sum to 1 per (player, team, position_group)."""
    fs = final_stints[final_stints["duration"] > 0]
    slot = (fs.groupby(keys + ["position_name"])["duration"].sum()
              .reset_index(name="minutes_at_slot"))
    slot["minutes_at_position"] = slot.groupby(keys)["minutes_at_slot"].transform("sum")
    slot["slot_share"] = slot["minutes_at_slot"] / slot["minutes_at_position"]
 
    wide = slot.pivot_table(index=keys, columns="position_name", values="slot_share", fill_value=0.0)
    wide.columns = [f"slot_share_{c}" for c in wide.columns]
    assert np.allclose(wide.sum(axis=1), 1.0)
 
    top = (slot.sort_values("minutes_at_slot", ascending=False, kind="mergesort")
               .drop_duplicates(keys).set_index(keys)[["position_name", "slot_share"]]
               .rename(columns={"position_name": "dominant_slot", "slot_share": "dominant_slot_share"}))
    base = slot.groupby(keys).agg(minutes_at_position=("minutes_at_slot", "sum"),
                                  n_slots=("position_name", "nunique"))
    out = base.join(top).join(wide).reset_index()
    if league_map is not None:
        out["league"] = out["team_id"].map(league_map)
    return slot, out
 
def player_slot_by_formation(final_stints: pd.DataFrame, min_formation_minutes: float = 180.0):
    """Long table, one row per (player, team, position_group, formation, position_name).
      slot_share_in_formation = minutes at this slot / her position-group minutes in this formation
      formation_share         = her position-group minutes in this formation / all her group minutes
    `reliable` flags cells with enough minutes in the formation to read the slot split."""
    fs = final_stints[final_stints["duration"] > 0]
    kf = keys + ["formation"]
    g = (fs.groupby(kf + ["position_name"])["duration"].sum().reset_index(name="minutes_at_slot"))
    g["minutes_in_formation"] = g.groupby(kf)["minutes_at_slot"].transform("sum")
    g["slot_share_in_formation"] = g["minutes_at_slot"] / g["minutes_in_formation"]
    g["minutes_at_position"] = g.groupby(keys)["minutes_at_slot"].transform("sum")
    g["formation_share"] = g["minutes_in_formation"] / g["minutes_at_position"]
    g["reliable"] = g["minutes_in_formation"] >= min_formation_minutes
    return g
 
def team_slot_occupancy(final_stints: pd.DataFrame) -> pd.DataFrame:
    """Team-centric view: for each team x formation x slot, who played there.
    share_of_slot = player's minutes / all minutes at that slot in that formation."""
    fs = final_stints[final_stints["duration"] > 0]
    k = ["team_id", "formation", "position_group", "position_name"]
    occ = fs.groupby(k + ["player_id"])["duration"].sum().reset_index(name="minutes")
    occ["slot_minutes"] = occ.groupby(k)["minutes"].transform("sum")
    occ["share_of_slot"] = occ["minutes"] / occ["slot_minutes"]
    occ["rank_in_slot"] = occ.groupby(k)["minutes"].rank(method="first", ascending=False).astype(int)
    return occ.sort_values(k + ["rank_in_slot"]).reset_index(drop=True)
 
def cluster_slot_mix(profile_wide: pd.DataFrame, cluster_col: str, position_group: str) -> pd.DataFrame:
    """Minutes-weighted mean slot shares per cluster: which roles each archetype occupies."""
    p = profile_wide[(profile_wide["position_group"] == position_group) & profile_wide[cluster_col].notna()]
    cols = [c for c in p.columns if c.startswith("slot_share_")]
    cols = [c for c in cols if p[c].abs().sum() > 0]
    w = p["minutes_at_position"]
    num = p[cols].mul(w, axis=0).groupby(p[cluster_col]).sum()
    return num.div(w.groupby(p[cluster_col]).sum(), axis=0)

def has_overlap(group):
    group = group.sort_values(['from_min', 'to_min']).reset_index(drop=True)
    for i in range(len(group) - 1):
        if group.loc[i, 'to_min'] > group.loc[i+1, 'from_min']:
            return True
    return False

def build_eligible_pool(position_group, minutes_by_position):
    return minutes_by_position[
        (minutes_by_position['position_group'] == position_group) &
        (minutes_by_position['position_eligible'])
    ].copy()

x_scale = 105 / 120
y_scale = 68 / 80
goal_x, goal_y = 120, 40

def in_own_box(x, y):
    return (x <= 18) & (y >= 18) & (y <= 62)

def in_opposition_box(x, y):
    return (x >= 102) & (y >= 18) & (y <= 62)

def distance_to_goal(x, y):
    dx = goal_x - x
    dy = goal_y - y
    return np.sqrt(dx**2 + dy**2)

def distance_to_goal_meter(x, y):
    dx = (goal_x - x) * x_scale
    dy = (goal_y - y) * y_scale
    return np.sqrt(dx**2 + dy**2)

def distance(x1, y1, x2, y2):
    dx = x1 - x2
    dy = y1 - y2
    return np.sqrt(dx**2 + dy**2)

def distance_meter(x1, y1, x2, y2):
    dx = (x1 - x2) * x_scale
    dy = (y1 - y2) * y_scale
    return np.sqrt(dx**2 + dy**2)

def is_left_side(y):
    return y < 26.6

def is_right_side(y):
    return y > 53.3

def is_central(y):
    return (y >= 26.6) & (y <= 53.3)

post_y_top, post_y_bottom = 36, 44

def compute_shot_angle(x, y):
    x_m = 120 - x 
    y_top_m = post_y_top - y 
    y_bottom_m = post_y_bottom - y 
    angle = np.abs(np.arctan2(y_top_m, x_m) - np.arctan2(y_bottom_m, x_m))
    return angle  # in radians; convert to degrees with np.degrees() if preferred

def in_opposing_half(x):
    return x >= 60

def simplify_body_part(bp, position_group):
    if bp in ['Right Foot', 'Left Foot']:
        return bp
    elif bp == 'Head':
        return 'Head'
    elif position_group == 'Goalkeeper' and bp in ['Keeper Arm', 'Drop Kick']:
        return bp
    else:
        return 'Other/Unknown'

def build_subtype_completion_rate(events_df, stat_name, group_keys=['player_id', 'team_id', 'position_group']):
    return (events_df[events_df[stat_name]]
        .groupby(group_keys)
        .agg(**{f'{stat_name}_completion_pct': ('pass_completed', 'mean')})
        .reset_index())

def build_category_completion_rate(events_df, cat_col, cat_value, stat_name, group_keys=['player_id', 'team_id', 'position_group']):
    subset = events_df[events_df[cat_col] == cat_value]
    return (subset
        .groupby(group_keys)
        .agg(**{f'{stat_name}_completion_pct': ('pass_completed', 'mean')})
        .reset_index())

def windowed_possession_frac(match_id, team_id, from_min, to_min, poss_seq):
    match_chains = poss_seq[poss_seq['match_id'] == match_id]

    overlapping = match_chains[
        (match_chains['start_time'] < to_min) & (match_chains['chain_end'] > from_min)
    ].copy()

    if len(overlapping) == 0:
        return np.nan

    overlapping['overlap_start'] = overlapping['start_time'].clip(lower=from_min)
    overlapping['overlap_end'] = overlapping['chain_end'].clip(upper=to_min)
    overlapping['overlap_duration'] = overlapping['overlap_end'] - overlapping['overlap_start']

    total = overlapping['overlap_duration'].sum()
    if total <= 0:
        return np.nan

    team_total = overlapping.loc[overlapping['possession_team_id'] == team_id, 'overlap_duration'].sum()
    return team_total / total

def get_possession_frac_final(row, poss_seq, team_duration):
    # try the windowed calculation first (correct for both partial and full appearances)
    windowed = windowed_possession_frac(row['match_id'], row['team_id'], row['from_min'], row['to_min'], poss_seq)
    if pd.notna(windowed):
        return windowed

    # fallback: whole-match possession for this team
    match = team_duration[(team_duration['match_id'] == row['match_id']) & (team_duration['possession_team_id'] == row['team_id'])]
    if len(match):
        return match['possession_frac'].iloc[0]

    # final fallback: no data available at all for this match/team — assume neutral 0.5
    return 0.5

def assign_stint(row, stints_df):
    candidates = stints_df[
        (stints_df['player_id'] == row['player_id']) &
        (stints_df['match_id'] == row['match_id']) &
        (stints_df['from_min'] <= row['elapsed_min']) &
        (row['elapsed_min'] < stints_df['to_min'])
    ]
    return candidates.index[0] if len(candidates) else np.nan

def build_padj_feature(events_subset, stat_name, final_stints, minutes_by_position):
    # mark each player's final stint (the one with no successor) so we can treat its end as inclusive
    final_stints = final_stints.copy()
    last_stint_end = final_stints.groupby(
        ['player_id', 'match_id', 'team_id', 'league', 'position_group']
    )['to_min'].transform('max')
    final_stints['is_last_stint'] = final_stints['to_min'] == last_stint_end

    events_with_stint = events_subset.merge(
        final_stints[['player_id', 'match_id', 'team_id', 'league', 'position_group',
                      'from_min', 'to_min', 'is_last_stint', 'padj_factor']],
        on=['player_id', 'match_id', 'team_id', 'league', 'position_group'],
        how='left'
    )

    within_window = (
        (events_with_stint['elapsed_min'] >= events_with_stint['from_min']) &
        (
            (events_with_stint['elapsed_min'] < events_with_stint['to_min']) |
            (events_with_stint['is_last_stint'] & (events_with_stint['elapsed_min'] <= events_with_stint['to_min']))
        )
    )
    events_with_stint = events_with_stint[within_window]

    # --- validation: every original event should be matched to exactly one stint ---
    match_counts = events_with_stint.groupby(events_with_stint.index).size()
    n_matched = events_with_stint.index.nunique()
    n_original = len(events_subset)
    n_duplicated = (match_counts > 1).sum()
    print(f"{stat_name}: {n_original} raw events, {n_matched} matched to exactly one stint, "
          f"{n_original - n_matched} unmatched, {n_duplicated} matched to more than one stint")

    events_with_stint[f'{stat_name}_padj'] = events_with_stint['padj_factor']

    season = (events_with_stint.groupby(['player_id', 'team_id', 'league', 'position_group'])
              .agg(**{
                  f'{stat_name}_total': (f'{stat_name}_padj', 'size'),
                  f'{stat_name}_total_padj': (f'{stat_name}_padj', 'sum'),
              }).reset_index())

    season = season.merge(
        minutes_by_position[['player_id', 'team_id', 'league', 'position_group', 'minutes_at_position']],
        on=['player_id', 'team_id', 'league', 'position_group'],
        how='left'
    )
    season[f'{stat_name}_per_90'] = season[f'{stat_name}_total'] / season['minutes_at_position'] * 90
    season[f'{stat_name}_padj_per_90'] = season[f'{stat_name}_total_padj'] / season['minutes_at_position'] * 90

    return season

def find_unmatched_events(events_subset, final_stints):
    events_subset = events_subset.copy()
    events_subset['_original_idx'] = events_subset.index  # explicitly carry the original index as a real column

    events_with_stint = events_subset.merge(
        final_stints[['player_id', 'match_id', 'team_id', 'league', 'position_group',
                      'from_min', 'to_min', 'padj_factor']],
        on=['player_id', 'match_id', 'team_id', 'league', 'position_group'],
        how='left'
    )

    events_with_stint['is_last_stint'] = events_with_stint.groupby(
        ['player_id', 'match_id', 'team_id', 'league', 'position_group']
    )['to_min'].transform('max') == events_with_stint['to_min']

    within_window = (
        (events_with_stint['elapsed_min'] >= events_with_stint['from_min']) &
        (
            (events_with_stint['elapsed_min'] < events_with_stint['to_min']) |
            (events_with_stint['is_last_stint'] & (events_with_stint['elapsed_min'] <= events_with_stint['to_min']))
        )
    )

    matched_original_indices = set(events_with_stint.loc[within_window, '_original_idx'])
    unmatched = events_subset[~events_subset['_original_idx'].isin(matched_original_indices)]
    return unmatched.drop(columns='_original_idx')

def compare_raw_counts(new_feature_df, new_count_col, original_feature_df, original_count_col, stat_name):
    comparison = new_feature_df[['player_id', 'team_id', 'position_group', new_count_col]].merge(
        original_feature_df[['player_id', 'team_id', 'position_group', original_count_col]],
        on=['player_id', 'team_id', 'position_group'], how='outer', indicator=True
    )
    comparison['diff'] = comparison[new_count_col] - comparison[original_count_col]
    comparison['stat'] = stat_name
    return comparison

def get_fill_strategy(feat, feature_tags, form_to_fill_strategy):
    form = feature_tags[feat].get("form")
    return form_to_fill_strategy.get(form, "group_mean")  # default to the safer option if form is missing

def fill_feature_nans(df, feature_cols, feature_tags, form_to_fill_strategy, group_cols=('league', 'position_group')):
    df = df.copy()
    for feat in feature_cols:
        strategy = get_fill_strategy(feat, feature_tags, form_to_fill_strategy)
        if strategy == 'zero':
            df[feat] = df[feat].fillna(0)
        else:
            group_means = df.groupby(list(group_cols))[feat].transform('mean')
            df[feat] = df[feat].fillna(group_means).fillna(0)
    return df

def _is_aerial(df: pd.DataFrame) -> pd.Series:
    """Your aerial definition, applied row by row: the losing side of an aerial duel (duel_type ==
    'Aerial Lost') OR an event flagged as winning one (any of AERIAL_WON_COLS is True). Columns that are not
    present in this data pull are skipped, so check which *_aerial_won columns you actually have."""
    out = pd.Series(False, index=df.index)
    if "duel_type" in df.columns:
        out = out | df["duel_type"].eq("Aerial Lost")
    for c in aerial_won_cols:
        if c in df.columns:
            out = out | df[c].eq(True)
    return out

def _first_events(events: pd.DataFrame) -> pd.DataFrame:
    """The TRUE first event of every possession (one row per match_id + possession), with the five
    start-conditions from the regains definition evaluated on it. drop_duplicates(keep='first') is used
    rather than groupby().first(), because groupby().first() returns the first NON-NULL value of each column
    separately - it can mix values from different events (a Pass row carrying a later event's aerial flag).
    Possession owner = StatsBomb's possession_team_id (falls back to the first event's team_id if absent):
    the first event can belong to the OTHER team (e.g. the loser's 'Aerial Lost' duel logged first)."""
    first = (events.sort_values(["match_id", "index"])
                   .drop_duplicates(["match_id", "possession"], keep="first").copy())
    if "possession_team_id" in first.columns:
        first["poss_team_id"] = first["possession_team_id"].fillna(first["team_id"])
    else:
        first["poss_team_id"] = first["team_id"]
 
    first["is_recovery"] = first["type"].eq("Ball Recovery")
    first["is_interception"] = first["type"].eq("Interception")
    first["is_tackle"] = first["type"].eq("Duel") & first["duel_type"].eq("Tackle")
    first["is_aerial"] = _is_aerial(first)
    first["is_restart"] = first["play_pattern"].isin(qualifying_play_patterns)
    first["qualifies"] = first[["is_recovery", "is_interception", "is_tackle", "is_aerial", "is_restart"]].any(axis=1)
    first["is_kickoff"] = first["play_pattern"].eq("From Kick Off")     # possession begins with a kick-off (start of half / after a goal)
    first["start_t"] = first["elapsed_min"]                       # minutes
    return first

def start_reason_counts(events: pd.DataFrame) -> pd.DataFrame:
    """Diagnostic: how many possessions start for each reason (a possession can satisfy several, so the rows
    do not sum to the total). The last row shows how often an aerial start's first event was logged by the
    team that does NOT own the possession - i.e. how often owning by the first event's team would have been wrong."""
    f = _first_events(events)
    out = f[["is_recovery", "is_interception", "is_tackle", "is_aerial", "is_restart"]].sum().to_frame("possessions")
    out.loc["none (does not qualify)"] = int((~f["qualifies"]).sum())
    out.loc["total possessions"] = len(f)
    out.loc["aerial start, 1st event by non-owner"] = int((f["is_aerial"] & (f["team_id"] != f["poss_team_id"])).sum())
    return out

def _possession_boundaries(events: pd.DataFrame) -> pd.DataFrame:
    """One row per (match_id, possession): its owner, and - via shift(-1) - who owns the FOLLOWING possession,
    when it starts, and whether it qualifies. 'next_start_t' is the moment this possession ends."""
    first = _first_events(events).sort_values(["match_id", "possession"]).reset_index(drop=True)
    g = first.groupby("match_id")
    first["next_team_id"] = g["poss_team_id"].shift(-1)
    first["next_start_t"] = g["start_t"].shift(-1)
    first["next_qualifies"] = g["qualifies"].shift(-1)
    first["next_kickoff"] = g["is_kickoff"].shift(-1)
    first["next_type"] = g["type"].shift(-1)
    return first[["match_id", "possession", "poss_team_id", "next_team_id", "next_start_t",
                  "next_qualifies", "next_kickoff", "next_type"]]

def _check_actions(actions, bounds: pd.DataFrame) -> None:
    """`actions` must be the qualifying action events as a DataFrame that is a SUBSET of `events`' rows.
    Three cheap checks, each failing loudly rather than returning quietly wrong counts."""
    if not isinstance(actions, pd.DataFrame):
        raise TypeError(f"actions must be a DataFrame of the qualifying action events (a subset of the rows of "
                        f"`events`), but got {type(actions).__name__}. If you have a boolean mask, pass "
                        f"events[mask].")
    missing = [c for c in _action_cols if c not in actions.columns]
    if missing:
        raise KeyError(f"actions is missing required column(s) {missing}; it needs {_action_cols}.")
    known = pd.MultiIndex.from_frame(bounds[["match_id", "possession"]])
    have = pd.MultiIndex.from_frame(actions[["match_id", "possession"]])
    n_unknown = int((~have.isin(known)).sum())
    if n_unknown:
        raise ValueError(f"{n_unknown} action row(s) belong to a (match_id, possession) that does not exist in "
                         f"`events` - actions must be filtered from the SAME events table that is passed in.")

def _action_regains(events: pd.DataFrame, actions: pd.DataFrame, window_s: float = 5.0,
                    require_qualifying_start: bool = False, exclude_kickoff: bool = True,
                    exclude_saves: bool = True) -> pd.DataFrame:
    """One row per (match_id, team_id).
    events  = the FULL event table (needed to see where every possession starts and ends).
    actions = DataFrame of the qualifying action events, a subset of events' rows, e.g.
              events[events['type'].eq('Pressure')]. Needs match_id, team_id, possession, elapsed_min.
    n_actions = every qualifying action the team made.
    n_regains = number of TURNOVERS where at least one qualifying action by the receiving team fell in the
    final window_s seconds of the possession it won - each turnover counted ONCE.
 
    Two switches decide which definition is applied (they are independent):
      require_qualifying_start=True   FULL definition: the possession that follows must ALSO start with a
                                      recovery / interception / tackle / aerial, or a restart pattern.
      require_qualifying_start=False  SIMPLE definition: only 'first action in the last window_s seconds of a
                                      possession, and the following possession belongs to the acting team'.
      exclude_kickoff=True            the following possession must NOT start with a kick-off (play_pattern
                                      'From Kick Off'). Applied under BOTH definitions, so comparing them
                                      isolates the effect of the start-type test alone.
      exclude_saves=True              (only matters under the SIMPLE definition) drop turnovers whose new
                                      possession opens with a Goal Keeper event and does not already qualify -
                                      in the data 93% of these follow an opponent shot, i.e. they are saves, not
                                      regains won by pressing. Removes only turnovers the full definition already
                                      rejects, so simple-minus-saves is still a superset of the full definition."""
    bounds = _possession_boundaries(events)
    _check_actions(actions, bounds)
    transitions = bounds.dropna(subset=["next_team_id"])
    transitions = transitions[transitions["next_team_id"] != transitions["poss_team_id"]]
 
    m = actions[_action_cols].merge(transitions, on=["match_id", "possession"], how="inner")
    m = m[m["team_id"] == m["next_team_id"]]                          # only the team about to win the ball
    if require_qualifying_start:
        m = m[m["next_qualifies"].fillna(False).astype(bool)]          # FULL definition: the new possession must qualify
    if exclude_kickoff:
        m = m[~m["next_kickoff"].fillna(False).astype(bool)]           # never a possession that begins with a kick-off
    if exclude_saves and not require_qualifying_start:
        is_save = (m["next_type"] == "Goal Keeper") & ~m["next_qualifies"].fillna(False).astype(bool)
        m = m[~is_save]                                                # a shot saved is not a regain won by pressing
    gap_s = ((m["next_start_t"] - m["elapsed_min"]) * 60).round(3)     # minutes -> seconds, ms-rounded
    m = m[(gap_s >= 0) & (gap_s <= window_s)]                          # within the final window_s seconds
 
    first_per_turnover = m.sort_values("elapsed_min").drop_duplicates(["match_id", "possession"], keep="first")
    n_regains = first_per_turnover.groupby(["match_id", "team_id"]).size().rename("n_regains")
    n_actions = actions.groupby(["match_id", "team_id"]).size().rename("n_actions")
 
    counts = pd.concat([n_actions, n_regains], axis=1).fillna({"n_regains": 0})
    counts["n_regains"] = counts["n_regains"].astype(int)
    counts["regain_rate"] = counts["n_regains"] / counts["n_actions"]
    return counts

def _pressure_mask(events: pd.DataFrame) -> pd.Series:
    return events["type"].eq("Pressure")

def _defensive_mask(events: pd.DataFrame) -> pd.Series:
    """Tackle (a Duel with duel_type 'Tackle'), Pressure, Interception, Dribbled Past, Block. Built ON TOP of
    _pressure_mask, so every pressure is a defensive action by construction."""
    t = events["type"]
    return (_pressure_mask(events) | t.eq("Interception") | t.eq("Dribbled Past") | t.eq("Block")
            | (t.eq("Duel") & events["duel_type"].eq("Tackle")))
 
def pressure_regains(events: pd.DataFrame, window_s: float = 5.0, require_qualifying_start: bool = True,
                     exclude_kickoff: bool = True, exclude_saves: bool = False) -> pd.DataFrame:
    """Per (match_id, team_id): n_pressures, n_pressure_regains, regain_rate. See _action_regains for the switches."""
    return _action_regains(events, events[_pressure_mask(events)], window_s,
                           require_qualifying_start, exclude_kickoff, exclude_saves).rename(
        columns={"n_actions": "n_pressures", "n_regains": "n_pressure_regains"})
 
def defensive_regains(events: pd.DataFrame, window_s: float = 5.0, require_qualifying_start: bool = True,
                      exclude_kickoff: bool = True, exclude_saves: bool = False) -> pd.DataFrame:
    """Per (match_id, team_id): n_defensive_actions, n_defensive_regains, regain_rate. See _action_regains for the switches."""
    return _action_regains(events, events[_defensive_mask(events)], window_s,
                           require_qualifying_start, exclude_kickoff, exclude_saves).rename(
        columns={"n_actions": "n_defensive_actions", "n_regains": "n_defensive_regains"})

def regain_features(events: pd.DataFrame, kind: str = "pressure", window_s: float = 5.0) -> pd.DataFrame:
    """The recommended regain features, one row per (match_id, team_id):
      n_actions                every qualifying action (pressures, or defensive actions) the team made
      <kind>_regains           turnovers won within window_s of one of those actions - SIMPLE definition,
                               kick-offs excluded, saves excluded
      <kind>_regains_active    the subset that also passes the FULL definition's start test (the new possession
                               opens with a recovery / interception / tackle / aerial win or a restart) - the ball
                               was actively won
      <kind>_regains_forced    the rest: the opponent's own failed action (incomplete pass, miscontrol, ...) after
                               the press handed the ball over
    active + forced = regains, by construction (the full definition is a subset of simple-minus-saves)."""
    fn = {"pressure": pressure_regains, "defensive": defensive_regains}[kind]
    allr = fn(events, window_s, require_qualifying_start=False, exclude_kickoff=True, exclude_saves=True)
    act = fn(events, window_s, require_qualifying_start=True, exclude_kickoff=True)
    out = pd.DataFrame({"n_actions": allr.iloc[:, 0], f"{kind}_regains": allr.iloc[:, 1],
                        f"{kind}_regains_active": act.iloc[:, 1]}).fillna(0).astype(int)
    out[f"{kind}_regains_forced"] = out[f"{kind}_regains"] - out[f"{kind}_regains_active"]
    assert (out[f"{kind}_regains_forced"] >= 0).all(), "full definition must be a subset of simple-minus-saves"
    return out

def regain_funnel(events: pd.DataFrame, actions: pd.DataFrame, window_s: float = 5.0):
    """Where do turnovers drop out on the way to being counted? Returns two tables.
 
    1) funnel - one row per (match_id, team_id), counting every possession the team WON from the opponent:
         turnovers_won     all possessions the team took over from the opponent
         kickoff_starts    ...whose first event begins a kick-off (excluded under both definitions)
         start_qualifies   ...whose first event passes the FULL definition's start test
         action_in_window  ...where the team made >=1 of `actions` in the last window_s seconds of the
                           possession it won (before any start or kick-off rule)
         regains_simple    timely and not a kick-off              = SIMPLE definition
         regains_full      timely, start qualifies, not a kick-off = FULL definition
       regains_simple equals _action_regains(require_qualifying_start=False)['n_regains'] and regains_full
       equals _action_regains(require_qualifying_start=True)['n_regains'] (kick-off excluded in both).
    2) added_by_simple - the turnovers the SIMPLE definition counts but the FULL one does not, grouped by the
       first-event type and play pattern of the possession that follows. Shows what the simple definition adds."""
    bounds = _possession_boundaries(events)
    _check_actions(actions, bounds)
 
    first = _first_events(events).sort_values(["match_id", "possession"]).reset_index(drop=True)
    g = first.groupby("match_id")
    first["next_pattern"] = g["play_pattern"].shift(-1)          # next_type already comes with the boundary table
 
    t = bounds.dropna(subset=["next_team_id"])
    t = t[t["next_team_id"] != t["poss_team_id"]]
    t = t.merge(first[["match_id", "possession", "next_pattern"]], on=["match_id", "possession"], how="left")
    t["winner"] = t["next_team_id"].astype(actions["team_id"].dtype)
    t["start_ok"] = t["next_qualifies"].fillna(False).astype(bool)
    t["kickoff"] = t["next_kickoff"].fillna(False).astype(bool)
 
    m = actions[_action_cols].merge(t[["match_id", "possession", "winner", "next_start_t"]],
                                    on=["match_id", "possession"], how="inner")
    m = m[m["team_id"] == m["winner"]]
    gap_s = ((m["next_start_t"] - m["elapsed_min"]) * 60).round(3)
    m = m[(gap_s >= 0) & (gap_s <= window_s)]
    timely = m[["match_id", "possession"]].drop_duplicates().assign(timely=True)
    t = t.merge(timely, on=["match_id", "possession"], how="left")
    t["timely"] = t["timely"].fillna(False).astype(bool)
    t["simple"] = t["timely"] & ~t["kickoff"]
    t["full"] = t["simple"] & t["start_ok"]
 
    funnel = (t.groupby(["match_id", "winner"])
                .agg(turnovers_won=("simple", "size"), kickoff_starts=("kickoff", "sum"),
                     start_qualifies=("start_ok", "sum"), action_in_window=("timely", "sum"),
                     regains_simple=("simple", "sum"), regains_full=("full", "sum")).astype(int))
    funnel.index.names = ["match_id", "team_id"]
    added = (t[t["simple"] & ~t["full"]].groupby(["next_type", "next_pattern"]).size()
               .rename("turnovers").sort_values(ascending=False).reset_index())
    return funnel, added

def added_turnover_context(events: pd.DataFrame, actions: pd.DataFrame, window_s: float = 5.0) -> pd.DataFrame:
    """One row per turnover that the SIMPLE definition counts but the FULL one does not (exactly the set that
    regain_funnel summarises as `added_by_simple`), with the context needed to judge whether it is a genuine regain:
      match_id, possession   the possession that ENDS (the one the acting team took the ball from)
      team_id                the team that won the ball
      next_type, next_pattern   first event and play pattern of the possession that follows
      last_type_old          type of the last event logged in the ending possession
      last_by_winner         whether the winning team logged that last event
      ballwin_in_old_tail    the winning team has a Ball Recovery / Interception / Tackle / aerial win INSIDE the
                             ending possession, within its last window_s seconds. True means the ball-win event
                             exists but is filed in the OLD possession, so the full definition's 'the new possession
                             starts with X' test cannot see it.
      trigger_type           type of the first qualifying action in the window (only if `actions` has a `type` column)"""
    bounds = _possession_boundaries(events)
    _check_actions(actions, bounds)
 
    first = _first_events(events).sort_values(["match_id", "possession"]).reset_index(drop=True)
    g = first.groupby("match_id")
    first["next_pattern"] = g["play_pattern"].shift(-1)          # next_type already comes with the boundary table
 
    t = bounds.dropna(subset=["next_team_id"])
    t = t[t["next_team_id"] != t["poss_team_id"]]
    t = t.merge(first[["match_id", "possession", "next_pattern"]], on=["match_id", "possession"], how="left")
    t["team_id"] = t["next_team_id"].astype(actions["team_id"].dtype)
    t["start_ok"] = t["next_qualifies"].fillna(False).astype(bool)
    t["kickoff"] = t["next_kickoff"].fillna(False).astype(bool)
 
    # the first qualifying action by the winner inside the window, per turnover
    cols = _action_cols + (["type"] if "type" in actions.columns else [])
    m = actions[cols].merge(t[["match_id", "possession", "team_id", "next_start_t"]].rename(columns={"team_id": "winner"}),
                            on=["match_id", "possession"], how="inner")
    m = m[m["team_id"] == m["winner"]]
    gap_s = ((m["next_start_t"] - m["elapsed_min"]) * 60).round(3)
    m = m[(gap_s >= 0) & (gap_s <= window_s)]
    trig = m.sort_values("elapsed_min").drop_duplicates(["match_id", "possession"], keep="first")
    keep = ["match_id", "possession"] + (["type"] if "type" in trig.columns else [])
    trig = trig[keep].rename(columns={"type": "trigger_type"}).assign(timely=True)
 
    t = t.merge(trig, on=["match_id", "possession"], how="left")
    t["timely"] = t["timely"].fillna(False).astype(bool)
    added = t[t["timely"] & ~t["kickoff"] & ~t["start_ok"]].copy()
 
    # last event logged in the ending possession, and who logged it
    last = (events.sort_values(["match_id", "index"]).drop_duplicates(["match_id", "possession"], keep="last")
                  [["match_id", "possession", "type", "team_id"]]
                  .rename(columns={"type": "last_type_old", "team_id": "last_team_old"}))
    added = added.merge(last, on=["match_id", "possession"], how="left")
    added["last_by_winner"] = added["last_team_old"] == added["team_id"]
 
    # does the winner have a ball-win event filed INSIDE the ending possession, in its last window_s seconds?
    won_flag = pd.Series(False, index=events.index)
    for c in aerial_won_cols:
        if c in events.columns:
            won_flag = won_flag | events[c].eq(True)
    is_ballwin = (events["type"].isin(["Ball Recovery", "Interception"])
                  | (events["type"].eq("Duel") & events["duel_type"].eq("Tackle")) | won_flag)
    bw = events.loc[is_ballwin.to_numpy(), ["match_id", "possession", "team_id", "elapsed_min"]]
    j = bw.merge(added[["match_id", "possession", "team_id", "next_start_t"]].rename(columns={"team_id": "winner"}),
                 on=["match_id", "possession"], how="inner")
    j = j[j["team_id"] == j["winner"]]
    gj = ((j["next_start_t"] - j["elapsed_min"]) * 60).round(3)
    j = j[(gj >= 0) & (gj <= window_s)][["match_id", "possession"]].drop_duplicates().assign(ballwin_in_old_tail=True)
    added = added.merge(j, on=["match_id", "possession"], how="left")
    added["ballwin_in_old_tail"] = added["ballwin_in_old_tail"].fillna(False).astype(bool)
 
    out = ["match_id", "possession", "team_id", "next_type", "next_pattern", "last_type_old", "last_by_winner",
           "ballwin_in_old_tail"] + (["trigger_type"] if "trigger_type" in added.columns else [])
    return added[out].sort_values(["match_id", "possession"]).reset_index(drop=True)

def safe_standardize(x):
    std = x.std(ddof=0)
    if std == 0 or pd.isna(std):
        return x - x.mean()  # every value already equals the mean here, so this is 0 for the whole group
    return (x - x.mean()) / std

def residualize(df, feature_cols, covariate_col, group_cols, robust=False):
    df = df.copy()
    cov = [covariate_col] if isinstance(covariate_col, str) else list(covariate_col)   # new
    for feat in feature_cols:
        resid_col = feat + '_adj'
        df[resid_col] = np.nan
        for _, idx in df.groupby(group_cols).groups.items():
            sub = df.loc[idx]
            X = sub[cov].to_numpy(dtype="float64")                                    # was: sub[[covariate_col]]
            y = sub[feat].to_numpy(dtype="float64")
            model = HuberRegressor() if robust else LinearRegression()
            model.fit(X, y)
            df.loc[idx, resid_col] = y - model.predict(X)
        df[resid_col] = df.groupby(["league"] + list(group_cols))[resid_col].transform(safe_standardize)
    return df

def pc1_context_correlation(df, feature_cols, context_col="context_score"):
    sub = df[feature_cols + [context_col]].dropna()
    pc1 = PCA(n_components=1).fit_transform(sub[feature_cols])
    r, _ = stats.pearsonr(pc1.ravel(), sub[context_col])
    return r

def select_position(df, position_group, level='position_group'):
    return df.xs(position_group, level=level, drop_level=False)

def plot_histogram_grid(df, cols, n_cols=6):
    n_rows = -(-len(cols) // n_cols)
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(n_cols*3, n_rows*2.5))
    for ax, col in zip(axes.flatten(), cols):
        df[col].hist(ax=ax, bins=30)
        ax.set_title(col, fontsize=8)
    plt.tight_layout()
    plt.show()

def detect_outliers_zscore(df, feature_cols, player_id_to_player, team_id_to_team, z_thresh=3):
    outlier_report = {}
    for col in feature_cols:
        z = np.abs(stats.zscore(df[col], nan_policy='omit'))
        outlier_idx = df.index[z > z_thresh]
        if len(outlier_idx) > 0:
            outlier_report[col] = df.loc[outlier_idx, ['league', col]].copy()
            outlier_report[col]['player_id'] = outlier_report[col].index.get_level_values('player_id')
            outlier_report[col]['team_id'] = outlier_report[col].index.get_level_values('team_id')
            outlier_report[col]['z_score'] = z[z > z_thresh]
            outlier_report[col]['player'] = outlier_report[col]['player_id'].map(player_id_to_player)
            outlier_report[col]['team'] = outlier_report[col]['team_id'].map(team_id_to_team)
    return outlier_report

def detect_outliers_iqr(df, feature_cols, player_id_to_player, team_id_to_team, k=1.5):
    outlier_report = {}
    for col in feature_cols:
        q1, q3 = df[col].quantile([0.25, 0.75])
        iqr = q3 - q1
        lower, upper = q1 - k*iqr, q3 + k*iqr
        mask = (df[col] < lower) | (df[col] > upper)
        if mask.sum() > 0:
            rows = df.loc[mask, ['league', col]].copy()
            rows['player_id'] = rows.index.get_level_values('player_id')
            rows['team_id'] = rows.index.get_level_values('team_id')
            rows['player'] = rows['player_id'].map(player_id_to_player)
            rows['team'] = rows['team_id'].map(team_id_to_team)
            # add a signed "how far outside the bound" measure, analogous to z_score
            rows['bound_distance'] = np.where(
                rows[col] > upper,
                rows[col] - upper,
                lower - rows[col]
            )
            outlier_report[col] = rows.sort_values('bound_distance', ascending=False)
    return outlier_report

def winsorize(series, lower=0.01, upper=0.99):
    lo, hi = series.quantile([lower, upper])
    return series.clip(lo, hi)

def winsorize_partial_group(df, cols, lower=0.01, upper=0.99):
    # store original sum of just these members, per row, before winsorizing
    original_sum = df[cols].sum(axis=1)

    for col in cols:
        df[col] = winsorize(df[col], lower, upper)

    # rescale so the winsorized pair preserves the SAME total the row originally had
    # (not 1.0, but whatever this player's forward+sideway share actually was)
    new_sum = df[cols].sum(axis=1)
    scale_factor = (original_sum / new_sum).replace([np.inf, -np.inf], np.nan).fillna(1.0)
    for col in cols:
        df[col] = df[col] * scale_factor

    return df

def impute_unreliable_rate_stat(
    all_players_stats, target_df, position_group, pct_col,
    attempted_col=None, derive_from=None, min_quantile=None, min_count=None,
):
    pos_df = all_players_stats.xs(position_group, level='position_group', drop_level=False)

    if derive_from is not None:
        total_col, rate_col = derive_from
        raw_count = pos_df[total_col] * pos_df[rate_col]
    elif attempted_col is not None:
        raw_count = pos_df[attempted_col]
    else:
        raise ValueError("Provide attempted_col or derive_from")

    threshold = raw_count.quantile(min_quantile) if min_quantile is not None else min_count
    eligible = pos_df[raw_count >= threshold]
    ineligible = pos_df[raw_count < threshold]

    league_means = eligible.groupby('league')[pct_col].mean()
    imputed = ineligible['league'].map(league_means).rename('imputed_value')

    target_df = target_df.join(imputed, how='left')  # aligns on the shared index automatically
    mask = target_df['imputed_value'].notna()
    target_df.loc[mask, pct_col] = target_df.loc[mask, 'imputed_value']
    return target_df.drop(columns='imputed_value')

def run_seed_stability_test(X, k, n_seeds=10, algorithm='kmeans', random_state_base=42):
    np.random.seed(random_state_base)
    seeds = np.random.randint(0, 100000, size=n_seeds).tolist()

    all_labels = {}
    for seed in seeds:
        model = KMeans(n_clusters=k, random_state=seed, n_init=10)
        labels = model.fit_predict(X)
        all_labels[seed] = labels

    return all_labels, seeds

def compute_pairwise_stability(all_labels):
    seeds = list(all_labels.keys())
    results = []
    for s1, s2 in combinations(seeds, 2):
        ari = adjusted_rand_score(all_labels[s1], all_labels[s2])
        results.append({'seed_1': s1, 'seed_2': s2, 'ari': ari})
    return pd.DataFrame(results)

def get_mean_stability(all_labels):
    seeds = list(all_labels.keys())
    aris = [adjusted_rand_score(all_labels[s1], all_labels[s2]) for s1, s2 in combinations(seeds, 2)]
    return np.mean(aris)

def to_percentile(df, cols, group_cols=("league", "position_group")):
    df = df.copy()
    for col in cols:
        df[col + "_pctile"] = df.groupby(list(group_cols))[col].rank(pct=True) * 100
    return df

def _series_for(source, features, suffix):  # no default, no special-casing — forces an explicit, literal value
    pct_cols = [f + suffix + '_pctile' for f in features]
    raw_cols = [f + suffix for f in features]
    if isinstance(source, pd.Series):
        pct_vals, raw_vals = source[pct_cols], source[raw_cols]
    else:
        pct_vals, raw_vals = source[pct_cols].mean(), source[raw_cols].mean()
    pct_vals.index = features
    raw_vals.index = features
    return pct_vals, raw_vals

def suffix_label(suffix):
    return suffix_labels.get(suffix, suffix.lstrip('_'))

def value_label_for(suffix):
    return value_labels.get(suffix, suffix.lstrip('_').replace('_', ' ') + ' values')

def pca_top_features(pca, feature_names, n_top=8):
    """Top n_top raw features per retained component, by |loading|, sign preserved."""
    loadings = pca.components_
    out = {}
    for i, comp in enumerate(loadings):
        idx = np.argsort(-np.abs(comp))[:n_top]
        out[f'PC{i+1}'] = pd.DataFrame({
            'feature': [feature_names[j] for j in idx],
            'loading': comp[idx],
            'explained_var_ratio': pca.explained_variance_ratio_[i]
        })
    return out

def pca_feature_importance_overall(pca, feature_names):
    """Overall contribution of each feature across all retained PCs (sums to 1)."""
    sq = pca.components_ ** 2
    weighted = (sq.T * pca.explained_variance_ratio_).T
    importance = weighted.sum(axis=0)
    importance /= importance.sum()
    return (pd.DataFrame({'feature': feature_names, 'importance': importance})
            .sort_values('importance', ascending=False)
            .reset_index(drop=True))

def compute_f_stats_with_p(df, feature_list, cluster_col='cluster', method='welch'):
    """
    F-oneway stat/p-value per feature, or Welch-type ANOVA (alexandergovern)
    if method='welch' -- recommended given your clusters have unequal sizes
    (e.g. n=7 vs n=31), which violates standard ANOVA's equal-variance assumption.
    """
    rows = []
    for col in feature_list:
        groups = [g[col].dropna() for _, g in df.groupby(cluster_col)]
        if method == 'welch':
            try:
                res = stats.alexandergovern(*groups)
                stat, p_val = res.statistic, res.pvalue
            except AttributeError:
                # scipy < 1.7 fallback
                stat, p_val = stats.f_oneway(*groups)
        else:
            stat, p_val = stats.f_oneway(*groups)
        rows.append({'feature': col, 'f_stat': stat, 'f_pvalue': p_val})
    return pd.DataFrame(rows).set_index('feature')

def backproject_cluster_centroids(pca, cluster_centers_pca, feature_names):
    """
    Reconstruct cluster centroids in standardized raw-feature space,
    using only retained components. Works for kmeans.cluster_centers_
    or gmm.means_.
    """
    reconstructed = cluster_centers_pca @ pca.components_
    df = pd.DataFrame(reconstructed, columns=feature_names)
    df.index = [f'Cluster_{i}' for i in range(len(df))]
    return df

def rank_cluster_driving_features(centroid_df, n_top=50):
    """Rank features by spread across cluster centroids (higher = more separating)."""
    spread = centroid_df.std(axis=0)
    ranked = spread.sort_values(ascending=False).head(n_top)
    return pd.DataFrame({'feature': ranked.index, 'cross_cluster_std': ranked.values})

def pairwise_cluster_deltas(centroid_df, cluster_a, cluster_b, n_top=50):
    """For a specific pair (most useful at your k=2/k=3), rank by signed difference."""
    delta = centroid_df.loc[cluster_a] - centroid_df.loc[cluster_b]
    ranked = delta.reindex(delta.abs().sort_values(ascending=False).index).head(n_top)
    return pd.DataFrame({
        'feature': ranked.index,
        'delta': ranked.values,
        'higher_in': np.where(ranked.values > 0, cluster_a, cluster_b)
    })

def select_top_features_per_category_pca(centroid_df, category_pools, n_per_category,
                                           method='spread', cluster_a=None, cluster_b=None):
    """
    Select top N differentiating features per category from PCA-backprojected
    cluster centroids, instead of raw F-oneway stats.

    method='spread'   -> cross-cluster std per feature (same logic as
                          rank_cluster_driving_features). Works for any k;
                          use this as the default, especially for k>2.
    method='pairwise' -> signed delta between two specific clusters (same logic
                          as pairwise_cluster_deltas). Requires cluster_a/cluster_b
                          (e.g. 'Cluster_0', 'Cluster_1'). Useful when you want to
                          isolate one specific split within k=3 (e.g. the small
                          cluster vs. the rest) rather than overall 3-way spread.
    """
    selected = {}
    for category, pool in category_pools.items():
        valid_pool = [c for c in pool if c in centroid_df.columns]
        sub = centroid_df[valid_pool]

        if method == 'spread':
            ranked = sub.std(axis=0).sort_values(ascending=False)
        elif method == 'pairwise':
            if cluster_a is None or cluster_b is None:
                raise ValueError("cluster_a and cluster_b required for method='pairwise'")
            delta = sub.loc[cluster_a] - sub.loc[cluster_b]
            ranked = delta.reindex(delta.abs().sort_values(ascending=False).index)
        else:
            raise ValueError("method must be 'spread' or 'pairwise'")

        n = n_per_category.get(category, 2)
        selected[category] = ranked.head(n).index.tolist()

    return selected

def select_features_combined(df, centroid_df, category_pools, n_per_category,
                               cluster_col='cluster', alpha=0.05,
                               weight_f=0.5, weight_pca=0.5,
                               require_significant=True, anova_method='welch'):
    """
    Select radar features per category using a blended rank of:
      - F-oneway/Welch statistic (raw-value group separation, variance-aware)
      - PCA-backprojected cross-cluster std (mechanistic driver of the actual
        clustering, computed in the same reduced space KMeans/GMM used)

    Combined via percentile rank averaging so the two incompatible scales
    don't need manual normalization.

    require_significant=True: only features with p < alpha are eligible.
    If fewer than n_per_category pass, backfills from the combined ranking
    and prints a warning -- so you're never silently short a feature, but
    you can see when that happened.

    No redundancy pruning -- intentionally correlated features you want to
    keep (e.g. multiple pass-completion variants) are left untouched.
    """
    selected = {}
    diagnostics = {}

    for category, pool in category_pools.items():
        valid_pool = [c for c in pool if c in df.columns and c in centroid_df.columns]
        if not valid_pool:
            selected[category] = []
            continue

        f_df = compute_f_stats_with_p(df, valid_pool, cluster_col, method=anova_method)
        pca_spread = centroid_df[valid_pool].std(axis=0).rename('pca_spread')

        combo = f_df.join(pca_spread)
        combo['f_rank_pct'] = combo['f_stat'].rank(pct=True)
        combo['pca_rank_pct'] = combo['pca_spread'].rank(pct=True)
        combo['combined_score'] = (weight_f * combo['f_rank_pct']
                                    + weight_pca * combo['pca_rank_pct'])
        combo['significant'] = combo['f_pvalue'] < alpha
        combo = combo.sort_values('combined_score', ascending=False)

        n = n_per_category.get(category, 2)

        if require_significant:
            sig_pool = combo[combo['significant']]
            chosen = sig_pool.head(n).index.tolist()
            if len(chosen) < n:
                backfill = combo[~combo.index.isin(chosen)].head(n - len(chosen)).index.tolist()
                if backfill:
                    print(f"[{category}] only {len(chosen)}/{n} features significant "
                          f"(p<{alpha}); backfilled: {backfill}")
                chosen += backfill
        else:
            chosen = combo.head(n).index.tolist()

        selected[category] = chosen
        diagnostics[category] = combo

    return selected, diagnostics

def get_display_name(player_id, team_id, player_id_to_player, team_id_to_team):
    name = player_id_to_player.get(player_id, f"Unknown ({player_id})")
    team = team_id_to_team.get(team_id, f"Unknown ({team_id})")
    return f"{name} ({team})"

def get_folder_name(player_id, team_id, player_id_to_player, team_id_to_team):
    name = player_id_to_player.get(player_id, f"Unknown_{player_id}")
    team = team_id_to_team.get(team_id, f"Unknown_{team_id}")
    # strip parentheses, replace spaces and slashes with underscores
    safe_name = name.replace('/', '-').replace(' ', '_')
    safe_team = team.replace('/', '-').replace(' ', '_').replace("'", "")
    return f"{safe_name}_{safe_team}"

def chunk_features(feature_list, max_features_per_plot, radar_sets=None, prefix=None):
    """
    Split feature_list into consecutive chunks of at most max_features_per_plot,
    preserving order. Last chunk may be smaller.

    If radar_sets and prefix are given, each chunk is also registered into
    radar_sets under a generated key (f'{prefix}_1', f'{prefix}_2', ...), and
    the function returns those keys instead of the raw chunks — so they can be
    fed straight into the existing chart_name-based functions with no changes
    to those functions.
    """
    chunks = [
        feature_list[i:i + max_features_per_plot]
        for i in range(0, len(feature_list), max_features_per_plot)
    ]

    if radar_sets is None or prefix is None:
        return chunks

    chart_names = []
    for i, chunk in enumerate(chunks, start=1):
        key = f'{prefix}_{i}'
        radar_sets[key] = chunk
        chart_names.append(key)
    return chart_names

surface, ink, ink2, muted, grid_colour, axis_colour = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
slots = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
player_fig_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "plots")

def _text_on(colour):
    """ink or surface, whichever reads better on this fill colour."""
    r, g, b = [c / 255 for c in bytes.fromhex(colour.lstrip("#"))]
    lin = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    lum = 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)
    return surface if (1.05 / (lum + 0.05)) >= ((lum + 0.05) / 0.05) else ink

# def save_radar_chart(fig, position, n_clusters, folder_name, chart_name, base_dir='radar_charts'):
#     folder = os.path.join(base_dir, position, f'k{n_clusters}', folder_name)
#     os.makedirs(folder, exist_ok=True)

#     filepath = os.path.join(folder, f'{chart_name}.png')
#     fig.savefig(filepath, dpi=150, bbox_inches='tight')
#     plt.close(fig)
#     return filepath

def save_radar_chart(fig, position, n_clusters, folder_name, chart_name, base_dir=player_fig_dir):
    """Same as your previous version; only the default folder changed (main/radar_plots)."""
    folder = os.path.join(base_dir, str(position), f"k{n_clusters}", folder_name or "")
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, f"{chart_name}.png")
    fig.savefig(filepath, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return filepath

# def _draw_similarity_strip(fig, similarity_scores, highlight_label=None, label_threshold=0.06):
#     labels = list(similarity_scores.keys())
#     values = list(similarity_scores.values())
#     strip_colors = plt.cm.Set2.colors

#     strip_ax = fig.add_axes([0.12, 0.83, 0.76, 0.08])  # slightly taller than before, for the callouts
#     strip_ax.set_xlim(0, 1)
#     strip_ax.set_ylim(-1.6, 1.6)  # extra vertical room above/below the bar itself
#     strip_ax.axis('off')

#     left = 0
#     callout_side = 1  # alternates above (+1) / below (-1) for consecutive narrow segments
#     for i, (label, val) in enumerate(zip(labels, values)):
#         color = strip_colors[i % len(strip_colors)]
#         is_hers = (label == highlight_label)
#         center = left + val / 2

#         strip_ax.barh(0.5, val, left=left, height=1.0, color=color,
#                       edgecolor='black' if is_hers else 'white',
#                       linewidth=2.0 if is_hers else 0.5)

#         text = f"{label}\n{val:.0%}"
#         if val >= label_threshold:
#             strip_ax.text(center, 0.5, text, ha='center', va='center', fontsize=6,
#                           fontweight='bold' if is_hers else 'normal')
#         else:
#             y_edge = 1.0 if callout_side > 0 else 0.0
#             y_label = 1.45 if callout_side > 0 else -0.45
#             strip_ax.plot([center, center], [y_edge, y_label], color='gray', linewidth=0.6, zorder=1)
#             strip_ax.text(center, y_label + (0.1 if callout_side > 0 else -0.1), text,
#                           ha='center', va='bottom' if callout_side > 0 else 'top',
#                           fontsize=6, fontweight='bold' if is_hers else 'normal')
#             callout_side *= -1  # next narrow segment goes the opposite direction

#         left += val

def _draw_similarity_strip(fig, similarity_scores, highlight_label=None, label_threshold=0.15,
                           rect=(0.12, 0.83, 0.76, 0.08), colors=None):
    labels, values = list(similarity_scores.keys()), list(similarity_scores.values())
    colors = colors or slots
    strip_ax = fig.add_axes(list(rect))
    strip_ax.set_xlim(0, 1); strip_ax.set_ylim(-1.6, 1.6); strip_ax.axis("off")
    left, callout_side = 0.0, 1
    for i, (label, val) in enumerate(zip(labels, values)):
        is_hers = (label == highlight_label)
        center = left + val / 2
        fill = colors[i % len(colors)]
        strip_ax.barh(0.5, val, left=left, height=1.0, color=fill,
                      edgecolor=ink if is_hers else surface, linewidth=2.0 if is_hers else 0.8)
        text = f"{label} · {val:.0%}"                                   # one line, fits inside the bar
        if val >= label_threshold:
            strip_ax.text(center, 0.5, text, ha="center", va="center", fontsize=7.5, color=_text_on(fill),
                          fontweight="bold" if is_hers else "normal")
        else:
            y_edge = 1.0 if callout_side > 0 else 0.0
            y_label = 1.45 if callout_side > 0 else -0.45
            strip_ax.plot([center, center], [y_edge, y_label], color=muted, linewidth=0.6, zorder=1)
            strip_ax.text(center, y_label + (0.1 if callout_side > 0 else -0.1), text, ha="center",
                          va="bottom" if callout_side > 0 else "top", fontsize=6.5, color=ink,
                          fontweight="bold" if is_hers else "normal")
            callout_side *= -1
        left += val
    return strip_ax

# def build_radar_chart(feature_list, pct_series_dict, title, raw_series_dict=None, fmt='.2f',
#                        save=False, position=None, n_clusters=None, folder_name=None, chart_name=None,
#                        similarity_scores=None, highlight_label=None):
#     N = len(feature_list)
#     angles = [n / float(N) * 2 * pi for n in range(N)]
#     angles += angles[:1]

#     has_strip = similarity_scores is not None
#     fig = plt.figure(figsize=(7, 8.2 if has_strip else 7.4))  # extra height for the legend now, too
#     polar_rect = [0.1, 0.12, 0.8, 0.69] if has_strip else [0.1, 0.12, 0.8, 0.78]
#     ax = fig.add_axes(polar_rect, projection='polar')

#     colors = plt.cm.tab10.colors
#     lw = 1.5

#     for i, (label, pct_vals) in enumerate(pct_series_dict.items()):
#         norm_vals = [pct_vals[f] / 100 for f in feature_list]
#         norm_vals += norm_vals[:1]

#         is_baseline = (i == 0)
#         color = 'gray' if is_baseline else colors[(i - 1) % len(colors)]

#         ax.plot(angles, norm_vals, label=label, linewidth=lw, color=color)
#         if is_baseline:
#             ax.fill(angles, norm_vals, alpha=0.08, color=color)

#         annotate_vals = raw_series_dict[label] if raw_series_dict else pct_vals
#         for angle, norm_val, feat in zip(angles[:-1], norm_vals[:-1], feature_list):
#             ax.annotate(f"{annotate_vals[feat]:{fmt}}", xy=(angle, norm_val),
#                         fontsize=7, color=color, ha='center', va='bottom')

#     ax.set_xticks(angles[:-1])
#     ax.set_xticklabels(feature_list, fontsize=8)
#     ax.set_yticklabels([])

#     # below the plot now, not above-right -- guaranteed clear of the strip regardless of
#     # how many series or how long the labels are, since nothing else occupies this space
#     ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.08), fontsize=9)

#     fig.suptitle(title, y=0.97, fontsize=13)
#     if has_strip:
#         _draw_similarity_strip(fig, similarity_scores, highlight_label)

#     if save:
#         return save_radar_chart(fig, position, n_clusters, folder_name, chart_name)
#     plt.show()

def build_radar_chart(feature_list, pct_series_dict, title, raw_series_dict=None, fmt='.3f',
                      save=False, position=None, n_clusters=None, folder_name=None, chart_name=None,
                      similarity_scores=None, highlight_label=None, annotate='auto', value_label=None):
    N = len(feature_list)
    params = [str(f).replace("_per_game", "").replace("_", " ") for f in feature_list]
    radar = Radar(params, [0] * N, [100] * N, round_int=[True] * N, num_rings=4, ring_width=1,
                  center_circle_radius=1)
    has_strip = similarity_scores is not None
    fig, axs = mplgrid(figheight=9.6, grid_height=0.74 if has_strip else 0.80,
                       title_height=0.16 if has_strip else 0.08, endnote_height=0.06,
                       title_space=0, endnote_space=0, grid_key="radar", axis=False)
    fig.set_facecolor(surface)
    ax = axs["radar"]
    radar.setup_axis(ax=ax, facecolor=surface)
    radar.draw_circles(ax=ax, facecolor="#f3f2ef", edgecolor=grid_colour, linewidth=1)
 
    labels = list(pct_series_dict)
    first_is_baseline = len(labels) > 1 and "avg" in str(labels[0]).lower()
    strip_keys = list(similarity_scores) if has_strip else []
    focus_colour = slots[strip_keys.index(highlight_label) % len(slots)] if highlight_label in strip_keys else None
    do_annotate = (len(labels) <= 2) if annotate == 'auto' else bool(annotate)
 
    # 1) draw every series, remember where its points are
    handles, drawn, c_idx = [], [], 0
    for i, label in enumerate(labels):
        pct_vals = pct_series_dict[label]
        vals = [float(pct_vals[f]) if np.isfinite(float(pct_vals[f])) else 0.0 for f in feature_list]
        if i == 0 and first_is_baseline:
            _, verts = radar.draw_radar_solid(vals, ax=ax, kwargs=dict(facecolor=muted, alpha=0.22,
                                                                       edgecolor=muted, linewidth=1.5))
            handles.append(Rectangle((0, 0), 1, 1, facecolor=muted, alpha=0.4, label=label))
            colour = muted
        else:
            colour = focus_colour if (focus_colour and first_is_baseline) else slots[c_idx % len(slots)]
            c_idx += 1
            _, verts = radar.draw_radar_solid(vals, ax=ax, kwargs=dict(facecolor="none", edgecolor=colour,
                                                                       linewidth=2.2, zorder=4))
            ax.scatter(verts[:, 0], verts[:, 1], s=22, color=colour, edgecolor=surface, linewidth=1, zorder=5)
            handles.append(Line2D([0], [0], color=colour, linewidth=2.2, label=label))
        drawn.append((label, np.asarray(vals), verts, colour))
 
    # 2) numbers: the higher point's number goes outside, the lower one's inside (away from each other);
    #    when two points are within 10 percentile points, the numbers also step sideways.
    #    Each number's box is outlined in its series' colour, so it is clear which line it belongs to.
    if do_annotate:
        stack = np.vstack([d[1] for d in drawn])
        for s, (label, vals, verts, colour) in enumerate(drawn):
            annotate_vals = raw_series_dict[label] if raw_series_dict else pct_series_dict[label]
            for j, ((x, y), feat) in enumerate(zip(verts, feature_list)):
                r = np.hypot(x, y) or 1.0
                ux, uy = x / r, y / r
                others = np.delete(stack[:, j], s)
                outward = len(others) == 0 or vals[j] >= others.max()
                push = 0.5 if outward else -0.5
                close = len(others) > 0 and np.min(np.abs(others - vals[j])) < 10
                side = (0.4 if s % 2 == 0 else -0.4) if close else 0.0
                v = annotate_vals[feat]
                ax.text(x + push * ux - side * uy, y + push * uy + side * ux,
                        "n/a" if not np.isfinite(float(v)) else f"{v:{fmt}}", ha="center", va="center",
                        fontsize=7, color=ink, zorder=6,
                        bbox=dict(boxstyle="round,pad=0.15", facecolor=surface, edgecolor=colour,
                                  linewidth=1.0, alpha=0.9))
 
    radar.draw_param_labels(ax=ax, fontsize=8.5, color=ink2, wrap=18)
    t = axs["title"]
    t.text(0.01, 0.97, "\n".join(textwrap.wrap(title, 70)), fontsize=12.5, fontweight="bold", color=ink,
           va="top", ha="left")
    note = "Rings at the 25th / 50th / 75th / 100th percentile."
    if do_annotate and raw_series_dict:
        note += f" Numbers = {value_label or 'the values behind each point'} (box colour = series)."
    t.text(0.01, 0.70 if has_strip else 0.30, note, fontsize=8, color=muted, va="top", ha="left")
    if has_strip:
        pos = t.get_position()
        _draw_similarity_strip(fig, similarity_scores, highlight_label,
                               rect=(pos.x0 + 0.08 * pos.width, pos.y0, 0.84 * pos.width, 0.45 * pos.height))
    axs["endnote"].legend(handles=handles, loc="center", ncol=min(3, len(handles)), fontsize=8.5, frameon=False)
    if save:
        return save_radar_chart(fig, position, n_clusters, folder_name, chart_name)
    plt.show()

def plot_cluster_comparison(chart_name, radar_sets, stats_df, column_name='cluster', suffix='_adj'):
    features = radar_sets[chart_name]
    pct_dict, raw_dict = {}, {}
    for c in sorted(stats_df[column_name].unique()):
        members = stats_df[stats_df[column_name] == c]
        pct_vals, raw_vals = _series_for(members, features, suffix)
        label = f'{column_name} {c}'
        pct_dict[label], raw_dict[label] = pct_vals, raw_vals

    build_radar_chart(features, pct_dict,
                       f'{chart_name.title()} — {column_name} comparison ({"raw" if suffix == "" else suffix})',
                       raw_series_dict=raw_dict, value_label=value_label_for(suffix))

def plot_player_vs_cluster(chart_name, radar_sets, player_id, team_id, stats_df, player_id_to_player,
                            team_id_to_team, column_name='cluster', suffix='_adj', n_clusters=None):
    features = radar_sets[chart_name]
    player_row = stats_df.xs(key=(player_id, team_id), level=('player_id', 'team_id')).iloc[0]
    cluster_id = player_row[column_name]
    cluster_members = stats_df[stats_df[column_name] == cluster_id]
    display_name = get_display_name(player_id, team_id, player_id_to_player, team_id_to_team)

    cluster_pct, cluster_raw = _series_for(cluster_members, features, suffix)
    player_pct, player_raw = _series_for(player_row, features, suffix)

    pct_dict = {f'{column_name} {cluster_id} avg': cluster_pct, display_name: player_pct}
    raw_dict = {f'{column_name} {cluster_id} avg': cluster_raw, display_name: player_raw}

    similarity_scores = highlight_label = None
    if n_clusters is not None:
        similarity_scores = {
            f'Cluster {i}': player_row[f'sim_cluster_{i}_k{n_clusters}'] for i in range(n_clusters)
        }
        highlight_label = f'Cluster {int(cluster_id)}'

    build_radar_chart(features, pct_dict,
                       f'{chart_name.title()} — {display_name} ({"raw" if suffix == "" else suffix})',
                       raw_series_dict=raw_dict,
                       similarity_scores=similarity_scores, highlight_label=highlight_label, value_label=value_label_for(suffix))

def plot_player_vs_league_cluster(chart_name, radar_sets, player_id, team_id, stats_df, player_id_to_player,
                                   team_id_to_team, column_name='cluster', suffix='_adj', n_clusters=None):
    features = radar_sets[chart_name]
    player_row = stats_df.xs(key=(player_id, team_id), level=('player_id', 'team_id')).iloc[0]
    cluster_id = player_row[column_name]
    league = player_row['league']

    league_cluster_members = stats_df[(stats_df['league'] == league) & (stats_df[column_name] == cluster_id)]
    display_name = get_display_name(player_id, team_id, player_id_to_player, team_id_to_team)

    cluster_pct, cluster_raw = _series_for(league_cluster_members, features, suffix)
    player_pct, player_raw = _series_for(player_row, features, suffix)

    pct_dict = {f'{column_name} {cluster_id} avg ({league})': cluster_pct, display_name: player_pct}
    raw_dict = {f'{column_name} {cluster_id} avg ({league})': cluster_raw, display_name: player_raw}

    similarity_scores = highlight_label = None
    if n_clusters is not None:
        similarity_scores = {
            f'Cluster {i}': player_row[f'sim_cluster_{i}_k{n_clusters}'] for i in range(n_clusters)
        }
        highlight_label = f'Cluster {int(cluster_id)}'

    build_radar_chart(features, pct_dict,
                       f'{chart_name.title()} — {display_name} vs {league} peers ({"raw" if suffix == "" else suffix})',
                       raw_series_dict=raw_dict,
                       similarity_scores=similarity_scores, highlight_label=highlight_label, value_label=value_label_for(suffix))

def export_cluster_comparison_charts(stats_df, position, n_clusters, chart_names, radar_sets,
                                      column_name='cluster', suffixes=('_adj', '')):
    """
    One radar chart per (chart_name, suffix), comparing all clusters' average stats.
    '_adj' keeps the original plain filename; '' (raw) gets a '_raw' tag, e.g.:
        radar_charts/Goalkeeper/k3/passing.png       <- adj (default)
        radar_charts/Goalkeeper/k3/passing_raw.png   <- raw
    """
    for suffix in suffixes:
        file_tag = f'_{suffix_label(suffix)}'
        for chart_name in chart_names:
            features = radar_sets[chart_name]
            pct_dict, raw_dict = {}, {}
            for c in sorted(stats_df[column_name].unique()):
                cluster_pct, cluster_raw = _series_for(stats_df[stats_df[column_name] == c], features, suffix)
                pct_dict[f'{column_name} {c}'] = cluster_pct
                raw_dict[f'{column_name} {c}'] = cluster_raw

            build_radar_chart(
                features, pct_dict,
                f'{chart_name.title()} — {column_name} comparison ({suffix_label(suffix)})',
                raw_series_dict=raw_dict,
                save=True, position=position, n_clusters=n_clusters,
                folder_name='', chart_name=f'{chart_name}{file_tag}', value_label=value_label_for(suffix)
            )

def export_cluster_comparison_charts_by_league(stats_df, position, n_clusters, chart_names, radar_sets,
                                                column_name='cluster', suffixes=('_adj', '')):
    """
    One radar chart per (league, chart_name, suffix), cluster averages computed
    within that league only:
        radar_charts/Goalkeeper/k3/passing_(EPL).png
        radar_charts/Goalkeeper/k3/passing_(EPL)_raw.png
    """
    for suffix in suffixes:
        file_tag = f'_{suffix_label(suffix)}'
        for league in stats_df['league'].dropna().unique():
            league_subset = stats_df[stats_df['league'] == league]
            safe_league = str(league).replace('/', '-').replace(' ', '_').replace("'", "")

            for chart_name in chart_names:
                features = radar_sets[chart_name]
                pct_dict, raw_dict = {}, {}
                for c in sorted(league_subset[column_name].unique()):
                    cluster_pct, cluster_raw = _series_for(league_subset[league_subset[column_name] == c], features, suffix)
                    pct_dict[f'{column_name} {c} ({league})'] = cluster_pct
                    raw_dict[f'{column_name} {c} ({league})'] = cluster_raw

                build_radar_chart(
                    features, pct_dict,
                    f'{chart_name.title()} — {column_name} comparison ({league}, {suffix_label(suffix)})',
                    raw_series_dict=raw_dict,
                    save=True, position=position, n_clusters=n_clusters,
                    folder_name='', chart_name=f'{chart_name}{file_tag}_{safe_league}', value_label=value_label_for(suffix)
                )

def export_all_player_charts(stats_df, position, n_clusters, chart_names, radar_sets, cluster_col,
                              player_id_to_player, team_id_to_team, suffixes=('_adj', ''),
                              include_similarity=True):
    similarity_available = include_similarity and f'sim_cluster_0_k{n_clusters}' in stats_df.columns

    for suffix in suffixes:
        file_tag = f'_{suffix_label(suffix)}'
        for idx, row in stats_df.iterrows():
            idx_map = dict(zip(stats_df.index.names, idx))
            player_id, team_id = idx_map['player_id'], idx_map['team_id']
            cluster_id = row[cluster_col]
            display_name = get_display_name(player_id, team_id, player_id_to_player, team_id_to_team)
            folder_name = get_folder_name(player_id, team_id, player_id_to_player, team_id_to_team)
            cluster_members = stats_df[stats_df[cluster_col] == cluster_id]

            similarity_scores = highlight_label = None
            if similarity_available:
                similarity_scores = {
                    f'Cluster {i}': row[f'sim_cluster_{i}_k{n_clusters}'] for i in range(n_clusters)
                }
                highlight_label = f'Cluster {int(cluster_id)}'

            for chart_name in chart_names:
                features = radar_sets[chart_name]
                cluster_pct, cluster_raw = _series_for(cluster_members, features, suffix)
                player_pct, player_raw = _series_for(row, features, suffix)

                build_radar_chart(
                    features,
                    {f'Cluster {cluster_id} avg': cluster_pct, display_name: player_pct},
                    f'{chart_name.title()} — {display_name} ({suffix_label(suffix)})',
                    raw_series_dict={f'Cluster {cluster_id} avg': cluster_raw, display_name: player_raw},
                    save=True, position=position, n_clusters=n_clusters,
                    folder_name=folder_name, chart_name=f'{chart_name}{file_tag}',
                    similarity_scores=similarity_scores, highlight_label=highlight_label, value_label=value_label_for(suffix)
                )

def export_all_player_charts_league_aware(stats_df, position, n_clusters, chart_names, radar_sets, cluster_col,
                                           player_id_to_player, team_id_to_team, suffixes=('_adj', ''),
                                           include_similarity=True):
    similarity_available = include_similarity and f'sim_cluster_0_k{n_clusters}' in stats_df.columns

    for suffix in suffixes:
        file_tag = f'_{suffix_label(suffix)}'
        for idx, row in stats_df.iterrows():
            idx_map = dict(zip(stats_df.index.names, idx))
            player_id, team_id = idx_map['player_id'], idx_map['team_id']
            league, cluster_id = row['league'], row[cluster_col]
            display_name = get_display_name(player_id, team_id, player_id_to_player, team_id_to_team)
            folder_name = get_folder_name(player_id, team_id, player_id_to_player, team_id_to_team)
            league_cluster_members = stats_df[(stats_df['league'] == league) & (stats_df[cluster_col] == cluster_id)]

            similarity_scores = highlight_label = None
            if similarity_available:
                similarity_scores = {
                    f'Cluster {i}': row[f'sim_cluster_{i}_k{n_clusters}'] for i in range(n_clusters)
                }
                highlight_label = f'Cluster {int(cluster_id)}'

            for chart_name in chart_names:
                features = radar_sets[chart_name]
                cluster_pct, cluster_raw = _series_for(league_cluster_members, features, suffix)
                player_pct, player_raw = _series_for(row, features, suffix)

                build_radar_chart(
                    features,
                    {f'Cluster {cluster_id} avg ({league})': cluster_pct, display_name: player_pct},
                    f'{chart_name.title()} — {display_name} vs {league} peers ({suffix_label(suffix)})',
                    raw_series_dict={f'Cluster {cluster_id} avg ({league})': cluster_raw, display_name: player_raw},
                    save=True, position=position, n_clusters=n_clusters,
                    folder_name=folder_name, chart_name=f'{chart_name}{file_tag}_league_relative',
                    similarity_scores=similarity_scores, highlight_label=highlight_label, value_label=value_label_for(suffix)
                )

def match_clusters(centroids_a, centroids_b):
    """Hungarian-algorithm pairing between two sets of centroids (labels are arbitrary between runs)."""
    dist = np.linalg.norm(centroids_a[:, None, :] - centroids_b[None, :, :], axis=2)
    row, col = optimize.linear_sum_assignment(dist)
    return dict(zip(row, col))

def cosine_sim(a, b):
    """Direction/shape similarity between two centroid vectors."""
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    return np.dot(a, b) / denom if denom else np.nan

def get_feature_order(X_std, candidate_features, method="pca", n_components=3):
    """
    method='pca':   order by summed abs. loading on top n_components (adds
                    the most-separating features first).
    method='given': returns candidate_features unchanged, for manual/domain order.
    """
    if method == "given":
        return list(candidate_features)
    pca = PCA(n_components=n_components).fit(X_std[candidate_features])
    loading_strength = np.abs(pca.components_).sum(axis=0)
    return list(np.array(candidate_features)[np.argsort(-loading_strength)])

def stability_vs_baseline(X_std, feature_order, k, baseline_n, test_ns, seed=42, n_init=10):
    """
    Fits ONE baseline clustering at baseline_n features. Every n in test_ns
    is compared directly against that same baseline -- not against the
    previous step -- so a single noisy transition can't cascade. One seed
    throughout, no multi-seed averaging needed.
    """
    feats_base = feature_order[:baseline_n]
    km_base = KMeans(n_clusters=k, random_state=seed, n_init=n_init).fit(X_std[feats_base].values)
    base_labels, base_centroids = km_base.labels_, km_base.cluster_centers_
    base_sizes = pd.Series(base_labels).value_counts()

    curve_rows = []
    tracking_df = pd.DataFrame(index=X_std.index)
    tracking_df["baseline_cluster"] = base_labels

    for n in test_ns:
        feats = feature_order[:n]
        km = KMeans(n_clusters=k, random_state=seed, n_init=n_init).fit(X_std[feats].values)
        labels, centroids = km.labels_, km.cluster_centers_

        ic = [feats.index(f) for f in feats_base]        # feats_base is always a prefix of feats
        match = match_clusters(base_centroids, centroids[:, ic])          # {base_idx: new_idx}
        remap = {new_idx: base_idx for base_idx, new_idx in match.items()}
        remapped_labels = np.array([remap[l] for l in labels])

        ari = adjusted_rand_score(base_labels, remapped_labels)
        pct_switched = float((remapped_labels != base_labels).mean())
        sims = [cosine_sim(base_centroids[i, :], centroids[j, ic]) for i, j in match.items()]

        remapped_sizes = pd.Series(remapped_labels).value_counts()
        size_diffs = [
            abs(remapped_sizes.get(i, 0) - base_sizes.get(i, 0)) / max(base_sizes.get(i, 0), 1)
            for i in base_sizes.index
        ]

        curve_rows.append(dict(
            n_features=n, pct_players_switched=pct_switched, ari=ari,
            prototype_sim=np.mean(sims), min_prototype_sim=np.min(sims),
            mean_size_drift=np.mean(size_diffs),
        ))
        tracking_df[f"cluster_at_{n}"] = remapped_labels

    cluster_cols = [c for c in tracking_df.columns if c.startswith("cluster_at_")]
    tracking_df["switched_from_baseline"] = tracking_df[cluster_cols].ne(tracking_df["baseline_cluster"], axis=0).any(axis=1)

    return pd.DataFrame(curve_rows), tracking_df

def plot_stability_vs_baseline(curve_df, position, k, baseline_n):
    fig, axes = plt.subplots(4, 1, figsize=(9, 10), sharex=True)

    axes[0].plot(curve_df["n_features"], curve_df["pct_players_switched"], marker="o", color="crimson")
    axes[0].axhline(0.05, color="gray", linestyle="--", alpha=0.4)
    axes[0].set_ylabel("% players switched\n(vs baseline)")

    axes[1].plot(curve_df["n_features"], curve_df["ari"], marker="o")
    axes[1].axhline(0.9, color="gray", linestyle="--", alpha=0.4)
    axes[1].set_ylabel("ARI vs baseline")

    axes[2].plot(curve_df["n_features"], curve_df["prototype_sim"], marker="o", color="orange", label="mean")
    axes[2].plot(curve_df["n_features"], curve_df["min_prototype_sim"], marker="o", color="orange", alpha=0.4, label="worst cluster")
    axes[2].axhline(0.97, color="gray", linestyle="--", alpha=0.4)
    axes[2].set_ylabel("Prototype cosine sim")
    axes[2].legend(fontsize=8)

    axes[3].plot(curve_df["n_features"], curve_df["mean_size_drift"], marker="o", color="green")
    axes[3].axhline(0.15, color="gray", linestyle="--", alpha=0.4)
    axes[3].set_ylabel("Mean size drift")
    axes[3].set_xlabel("Number of features")

    for ax in axes:
        ax.axvline(baseline_n, color="black", linestyle=":", alpha=0.6)

    fig.suptitle(f"{position} — stability vs baseline (n={baseline_n}), k={k}")
    plt.tight_layout()
    plt.show()

def assignment_stability_sweep(X_pca_full, n_values, k_values, reference_n=None, random_state=42, n_init=10):
    if reference_n is None:
        reference_n = max(n_values)
    rows = []
    for k in k_values:
        reference_labels = KMeans(n_clusters=k, n_init=n_init, random_state=random_state).fit_predict(X_pca_full[:, :reference_n])
        for n in n_values:
            labels_n = KMeans(n_clusters=k, n_init=n_init, random_state=random_state).fit_predict(X_pca_full[:, :n])
            rows.append({'n': n, 'k': k, 'ari_vs_reference': adjusted_rand_score(labels_n, reference_labels)})
    return pd.DataFrame(rows)

def plot_assignment_stability(stab_df, position_name):
    fig, ax = plt.subplots(figsize=(8, 4))
    colors = plt.cm.tab10.colors
    for i, k in enumerate(sorted(stab_df['k'].unique())):
        sub = stab_df[stab_df['k'] == k].sort_values('n')
        ax.plot(sub['n'], sub['ari_vs_reference'], marker='o', label=f'k={k}', color=colors[i])
    ax.axhline(0.8, color='gray', linestyle='--', linewidth=1, alpha=0.6, label='rough "strong agreement" guide')
    ax.set_xlabel('Number of PCA components (n)')
    ax.set_ylabel(f'ARI vs reference (n={stab_df["n"].max()})')
    ax.set_title(f'{position_name} — assignment stability vs n')
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.show()

def cluster_size_balance_sweep(X_pca_full, n_values, k, random_state=42, n_init=10):
    rows = []
    for n in n_values:
        labels = KMeans(n_clusters=k, n_init=n_init, random_state=random_state).fit_predict(X_pca_full[:, :n])
        sizes = pd.Series(labels).value_counts(normalize=True).sort_index()
        rows.append({'n': n, 'k': k, 'min_cluster_share': sizes.min()})
    return pd.DataFrame(rows)

def run_position_stability_check(X_pca_full, n_values, k_values, position_name, reference_n=None, random_state=42, n_init=10):
    stab_df = assignment_stability_sweep(X_pca_full, n_values, k_values, reference_n=reference_n,
                                          random_state=random_state, n_init=n_init)
    plot_assignment_stability(stab_df, position_name)

    balance_df = pd.concat([
        cluster_size_balance_sweep(X_pca_full, n_values, k, random_state=random_state, n_init=n_init)
        for k in k_values
    ], ignore_index=True)

    flagged = balance_df[balance_df['min_cluster_share'] < 0.10]
    if not flagged.empty:
        print(f"\n{position_name}: possible outlier-driven splits (min cluster share < 10%):")
        display(flagged)

    return stab_df, balance_df

# ---- 1. core metric computation, one fit at a time ----
def compute_separation_metrics(X, labels, centers):
    mean_sil = silhouette_score(X, labels)
    sample_sil = silhouette_samples(X, labels)
    worst_cluster_sil = pd.Series(sample_sil, index=labels).groupby(level=0).mean().min()
    db = davies_bouldin_score(X, labels)
    min_centroid_dist = spatial.distance.pdist(centers).min()
    return {
        'mean_silhouette': mean_sil,
        'worst_cluster_silhouette': worst_cluster_sil,
        'davies_bouldin': db,
        'min_centroid_dist': min_centroid_dist,
    }

# ---- 2. fit PCA once at the largest n you'll test ----
def fit_full_pca(X_std, max_n_components, random_state=42):
    """Fit PCA once at the largest n you'll test — PCA is nested, so slicing
    X_pca_full[:, :n] for smaller n is identical to refitting at that n."""
    pca_full = PCA(n_components=max_n_components, random_state=random_state).fit(X_std)
    X_pca_full = pca_full.transform(X_std)
    return pca_full, X_pca_full

# ---- 3. sweep across n and k, slicing the same PCA fit each time ----
def separation_sweep_pca(X_pca_full, n_values, k_values, random_state=42, n_init=10):
    rows = []
    for n in n_values:
        X_n = X_pca_full[:, :n]
        avg_pairwise_dist = spatial.distance.pdist(X_n).mean()
        for k in k_values:
            km = KMeans(n_clusters=k, n_init=n_init, random_state=random_state)
            labels = km.fit_predict(X_n)
            metrics = compute_separation_metrics(X_n, labels, km.cluster_centers_)
            metrics['min_centroid_dist_normalized'] = metrics['min_centroid_dist'] / avg_pairwise_dist
            rows.append({'n': n, 'k': k, **metrics})
    return pd.DataFrame(rows)

# ---- 4. tables, one per k ----
def print_separation_tables(sep_df, position_name=None):
    for k in sorted(sep_df['k'].unique()):
        table = sep_df[sep_df['k'] == k].drop(columns='k').set_index('n').round(4)
        print(f"\n===== {position_name or ''} k={k} =====")
        display(table)

# ---- 5. per-position 4-panel: all metrics, one line per k ----
def plot_separation_metrics(sep_df, position_name):
    metrics = ['mean_silhouette', 'worst_cluster_silhouette', 'davies_bouldin', 'min_centroid_dist_normalized']
    titles = ['Mean silhouette', 'Worst-cluster silhouette', 'Davies-Bouldin (lower better)', 'Min centroid dist (normalized)']

    fig, axes = plt.subplots(len(metrics), 1, figsize=(9, 11), sharex=True)
    colors = plt.cm.tab10.colors
    for ax, metric, title in zip(axes, metrics, titles):
        for i, k in enumerate(sorted(sep_df['k'].unique())):
            sub = sep_df[sep_df['k'] == k].sort_values('n')
            ax.plot(sub['n'], sub[metric], marker='o', label=f'k={k}', color=colors[i])
        ax.set_ylabel(title, fontsize=9)
        ax.grid(alpha=0.3)
    axes[0].legend(loc='best', fontsize=8)
    axes[-1].set_xlabel('Number of PCA components (n)')
    fig.suptitle(f'{position_name} — separation vs n_components', y=1.0)
    plt.tight_layout()
    plt.show()

# ---- 6. n x k heatmap for a single position — fast scan of every combination ----
def plot_position_heatmap(sep_df, position_name, metric='mean_silhouette'):
    pivot = sep_df.pivot(index='n', columns='k', values=metric).sort_index(ascending=False)
    cmap = 'RdYlGn_r' if metric == 'davies_bouldin' else 'RdYlGn'

    fig, ax = plt.subplots(figsize=(1.5 + 1.2 * len(pivot.columns), 0.4 * len(pivot) + 1.5))
    im = ax.imshow(pivot.values, cmap=cmap, aspect='auto')

    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels([f'k={k}' for k in pivot.columns])
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index)
    ax.set_ylabel('n components')

    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            val = pivot.values[i, j]
            if not np.isnan(val):
                ax.text(j, i, f'{val:.3f}', ha='center', va='center', fontsize=8)

    ax.set_title(f'{position_name} — {metric.replace("_", " ")} across n × k')
    fig.colorbar(im, ax=ax, shrink=0.8)
    plt.tight_layout()
    plt.show()

def run_position_separation_analysis(X_std, max_n_components, position_name,
                                      n_values=None, k_values=[2, 3, 4],
                                      reference_n=None,
                                      random_state=42, n_init=30,
                                      heatmap_metric='mean_silhouette'):
    """
    One call per position: fits PCA, sweeps separation metrics, sweeps
    assignment stability against a reference n, and screens for
    outlier-driven splits -- all in one pass.
    """
    if n_values is None:
        n_values = range(2, max_n_components + 1)
    if reference_n is None:
        reference_n = max(n_values)

    pca_full, X_pca_full = fit_full_pca(X_std, max_n_components, random_state=random_state)

    sep_df = separation_sweep_pca(X_pca_full, n_values, k_values, random_state=random_state, n_init=n_init)
    print_separation_tables(sep_df, position_name=position_name)
    plot_separation_metrics(sep_df, position_name)
    plot_position_heatmap(sep_df, position_name, metric=heatmap_metric)

    stab_df = assignment_stability_sweep(X_pca_full, n_values, k_values, reference_n=reference_n,
                                          random_state=random_state, n_init=n_init)
    plot_assignment_stability(stab_df, position_name)

    balance_df = pd.concat([
        cluster_size_balance_sweep(X_pca_full, n_values, k, random_state=random_state, n_init=n_init)
        for k in k_values
    ], ignore_index=True)
    flagged = balance_df[balance_df['min_cluster_share'] < 0.10]
    if not flagged.empty:
        print(f"\n{position_name}: possible outlier-driven splits (min cluster share < 10%):")
        display(flagged)

    print(f"\n{position_name} — quick verdict per k (ARI vs reference n={reference_n}):")
    for k in k_values:
        sub = stab_df[(stab_df['k'] == k) & (stab_df['n'] < reference_n)]
        median_ari = sub['ari_vs_reference'].median()
        verdict = "likely dimension-dilution artifact (assignments stable)" if median_ari >= 0.7 \
            else "possible genuine divergence (assignments shift with n)"
        print(f"  k={k}: median ARI = {median_ari:.3f} -> {verdict}")

    return {'pca': pca_full, 'X_pca_full': X_pca_full, 'sep_df': sep_df,
            'stab_df': stab_df, 'balance_df': balance_df}

def compute_soft_cluster_spectrum(X_pca, kmeans_model, stats_df, sigma_quantile=0.5):
    """
    (same docstring as before, with these changes:)
    - id_cols parameter removed: identity is now carried by stats_df's own
      MultiIndex (player_id, team_id, position_group), so there's nothing
      left to extract into columns before joining.
    - X_pca must be row-aligned with stats_df's INDEX specifically -- see
      the alignment warning below the function.
    """
    X_pca = np.asarray(X_pca)
    centroids = kmeans_model.cluster_centers_
    n_clusters = centroids.shape[0]

    assert len(X_pca) == len(stats_df), "X_pca and stats_df row counts differ"
    assert stats_df.index.is_unique, "stats_df index has duplicate player-team rows"

    dists = np.linalg.norm(X_pca[:, None, :] - centroids[None, :, :], axis=2)
    hard_cluster = np.argmin(dists, axis=1)

    own_dist = dists[np.arange(len(X_pca)), hard_cluster]
    sigma = max(np.quantile(own_dist, sigma_quantile), 1e-8)

    sim_raw = np.exp(-(dists ** 2) / (2 * sigma ** 2))
    sim = sim_raw / sim_raw.sum(axis=1, keepdims=True)

    # built directly on stats_df's own index -- no id_cols extraction needed
    out = pd.DataFrame(index=stats_df.index)
    for cluster_idx in range(n_clusters):
        out[f'dist_to_cluster_{cluster_idx}_k{n_clusters}'] = dists[:, cluster_idx]
    for cluster_idx in range(n_clusters):
        out[f'sim_cluster_{cluster_idx}_k{n_clusters}'] = sim[:, cluster_idx]
    out[f'hard_cluster_k{n_clusters}'] = hard_cluster
    sim_sorted = np.sort(sim, axis=1)[:, ::-1]
    out[f'margin_k{n_clusters}'] = sim_sorted[:, 0] - sim_sorted[:, 1]
    out[f'sigma_used_k{n_clusters}'] = sigma

    return stats_df.drop(columns=out.columns, errors="ignore").join(out)  # rerun-safe: old columns replaced

def build_subcluster_adj(df, cluster_col, feature_cols, covariate_col, clusters_to_refit):
    df = df.copy()
    for cluster_id in df[cluster_col].unique():
        sub_idx = df[df[cluster_col] == cluster_id].index
        if cluster_id in clusters_to_refit:
            refit = residualize(
                df.loc[sub_idx], feature_cols=feature_cols, covariate_col=covariate_col,
                group_cols=[cluster_col], robust=True,
            )
            for feat in feature_cols:
                df.loc[sub_idx, feat + "_subcluster_adj"] = refit[feat + "_adj"]
        else:
            for feat in feature_cols:
                df.loc[sub_idx, feat + "_subcluster_adj"] = (
                    df.loc[sub_idx].groupby("league")[feat + "_adj"].transform(safe_standardize)
                )
    return df

# --------------------------------------------------------------------------- #
# 4. Join to clustering results
# --------------------------------------------------------------------------- #
def attach_cluster_info(table: pd.DataFrame, cluster_df: pd.DataFrame, cluster_cols: list[str],
                        validate: str) -> pd.DataFrame:
    """Left-join cluster label + similarity columns on (player_id, team_id, position_group).
    validate='1:1' for the overall profile, 'm:1' for per-formation / occupancy tables.
    Players without a cluster (below minutes threshold, other position group) keep NaN."""
    cl = cluster_df
    if set(keys).issubset(set(cl.index.names)):
        cl = cl.reset_index()
    cl = cl[keys + list(cluster_cols)]
    assert not cl.duplicated(keys).any(), "cluster table must be unique on keys"
    int_cols = [c for c in cluster_cols if pd.api.types.is_integer_dtype(cl[c])]
    out = table.merge(cl, on=keys, how="left", validate=validate)
    for c in int_cols:                       # a left merge upcasts plain int -> float on any NaN it introduces
        out[c] = out[c].astype("Int64")
    out["has_cluster"] = out[cluster_cols[0]].notna()
    return out

def _maybe_int(s: pd.Series) -> pd.Series:
    """A cluster label stored as float64 (e.g. sklearn's .labels_ upcast to float somewhere upstream)
    prints as 0.0/1.0 and pivots into ugly column names like 'Goalkeeper__0.0'. If every non-null value
    is a whole number, cast to nullable Int64 (preserves NaN as pd.NA). Real fractional data (similarity
    scores, margins) is left untouched, since they will not pass the whole-number check."""
    if pd.api.types.is_integer_dtype(s):
        return s
    if pd.api.types.is_float_dtype(s):
        non_null = s.dropna()
        if len(non_null) and (non_null == non_null.round()).all():
            return s.astype("Int64")
    return s

def _flat(df: pd.DataFrame, position_group: str | None = None) -> pd.DataFrame:
    """Named index levels -> columns; add position_group if missing and a value is given."""
    names = [n for n in df.index.names if n is not None]
    t = df.reset_index(level=names) if names else df.copy()
    if "position_group" not in t.columns and position_group is not None:
        t["position_group"] = position_group
    return t

def standardize_cluster_table(df: pd.DataFrame, label_col: str, position_group: str | None = None,
                              sim_cols: list[str] = (), extra_cols: list[str] = ()) -> pd.DataFrame:
    """Bring ONE position group's clustering output into the shared schema, so all groups can be
    stacked with pd.concat and attached with a single attach_cluster_info call.
 
    label_col      -> renamed `cluster_l1` (the primary label)
    sim_cols       -> similarity columns (e.g. from compute_soft_cluster_spectrum), renamed `<PG>__<name>`
    extra_cols     -> any other label to carry (e.g. a k=3 label), renamed `<PG>__<name>`
    position_group -> only needed if the table has no position_group column / index level.
    The prefix keeps columns from different groups (whose clusters mean different things) apart.
    Only KEYS + the listed columns are kept, so feature columns never leak into the profile."""
    names = [n for n in df.index.names if n is not None]
    t = df.reset_index(level=names) if names else df.copy()
    if "position_group" not in t.columns:
        assert position_group is not None, "table has no position_group - pass position_group=..."
        t["position_group"] = position_group
    assert t["position_group"].nunique() == 1, "one position group per call"
    if position_group is not None:
        assert (t["position_group"] == position_group).all(), "position_group does not match the table"
    pre = str(t["position_group"].iloc[0]).replace("/", "")
    rename = {label_col: "cluster_l1", **{c: f"{pre}__{c}" for c in [*sim_cols, *extra_cols]}}
    t = t[keys + [label_col] + list(sim_cols) + list(extra_cols)].rename(columns=rename)
    t["cluster_l1"] = _maybe_int(t["cluster_l1"])
    assert not t.duplicated(keys).any(), "cluster table must be unique on keys"
    return t

def combine_hierarchical_clusters(parent_df: pd.DataFrame, child_dfs: dict, parent_col: str,
                                  child_col: str = None, child_sim_cols: list[str] = ()) -> pd.DataFrame:
    """Fold a two-level clustering (e.g. CM: k=3 on the combined DM/CM/AM pool, then each of the
    three clusters re-clustered) into ONE table with one row per (player, team, position_group).
 
    parent_df : KEYS (columns or index) + parent_col (+ any parent similarity columns)
    child_dfs : {parent_label: table} to use child_col/child_sim_cols (the defaults) for every parent, OR
                {parent_label: (table, child_col, child_sim_cols)} to override the label/sim columns for
                just that one parent - e.g. one sub-clustering run at k=3 while the others used k=2.
                Each table holds only the players assigned to that parent.
    Output columns: KEYS, cluster_l1 (parent), cluster_l2 (child, NaN if the player got none),
    cluster_path ('parent_child', NaN if no child), parent sims as given, and child sims renamed
    `sub<parent>_<name>` so the parents' child-similarity columns cannot collide - this also means a
    parent using different sim-column names (k=3's sim_cluster_2_k3 vs k=2's sim_cluster_0/1_k2) never
    collides with the others, so mixed k-levels across parents need no special handling here.
    Child similarities are NaN for players under other parents (structural, do not fill with 0)."""
    par = _flat(parent_df).rename(columns={parent_col: "cluster_l1"})
    pgs = par["position_group"].unique()
    fill = pgs[0] if len(pgs) == 1 else None       # child tables without position_group inherit the parent's
    kids = []
    for p, entry in child_dfs.items():
        if isinstance(entry, tuple):
            cdf, c_col, c_sims = entry
        else:
            cdf, c_col, c_sims = entry, child_col, child_sim_cols
        assert c_col is not None, f"no child_col for parent {p!r} - pass it in the tuple or as the default"
        c = _flat(cdf, fill)[keys + [c_col] + list(c_sims)]
        c = c.rename(columns={c_col: "cluster_l2", **{s: f"sub{p}_{s}" for s in c_sims}})
        c["_child_of"] = str(p)
        kids.append(c)
    kids = pd.concat(kids, ignore_index=True)
    assert not kids.duplicated(keys).any(), "a player appears in more than one parent's child table"
    orphans = int(kids.merge(par[keys], on=keys, how="left", indicator=True)["_merge"].ne("both").sum())
    assert orphans == 0, (f"{orphans} child rows have no matching player in the parent table "
                          "(check player_id / team_id / position_group in the child tables)")
    kids["cluster_l2"] = _maybe_int(kids["cluster_l2"])
    l2_is_int = pd.api.types.is_integer_dtype(kids["cluster_l2"])
 
    out = par.merge(kids, on=keys, how="left", validate="1:1")
    if l2_is_int:                            # keep 0/1/2 labels as ints (NaN -> <NA>), not 0.0/1.0
        out["cluster_l2"] = out["cluster_l2"].astype("Int64")
    has_child = out["_child_of"].notna()
    assert (out.loc[has_child, "_child_of"] == out.loc[has_child, "cluster_l1"].astype(str)).all(), \
        "a child table contains a player whose parent label differs in parent_df"
    out["cluster_path"] = (out["cluster_l1"].astype(str) + "_" + out["cluster_l2"].astype(str)
                           ).where(out["cluster_l2"].notna())
    first = keys + ["cluster_l1", "cluster_l2", "cluster_path"]
    return out.drop(columns="_child_of")[first + [c for c in out.columns if c not in first + ["_child_of"]]]
 
def infer_parent_label(child_df: pd.DataFrame, parent_df: pd.DataFrame, parent_col: str):
    """Which parent cluster does this child table belong to? Read it from the data: every player in
    the child table must carry the same parent label in the parent table."""
    par = _flat(parent_df)
    pgs = par["position_group"].unique()
    c = _flat(child_df, pgs[0] if len(pgs) == 1 else None)[keys]
    m = c.merge(par[keys + [parent_col]], on=keys, how="left", validate="1:1")
    assert m[parent_col].notna().all(), "child players missing from the parent table (check position_group / index)"
    labels = m[parent_col].unique()
    assert len(labels) == 1, f"child table spans several parent clusters: {list(labels)}"
    return labels[0]
 
def minutes_check(stats_df: pd.DataFrame, profile: pd.DataFrame, position_group: str | None = None) -> dict:
    """Pre-flight for the join. n_unmatched = cluster-table rows whose keys are missing from `profile`
    (typically a position_group string mismatch). If the table has a minutes_at_position column it also
    reports max_abs_diff against the profile's minutes; without that column only the key check runs."""
    s = _flat(stats_df, position_group)
    has_min = "minutes_at_position" in s.columns
    s = s[keys + (["minutes_at_position"] if has_min else [])]
    m = s.merge(profile[keys + ["minutes_at_position"]], on=keys, how="left",
                suffixes=("_stats", "_profile"), validate="1:1", indicator=True)
    out = {"n": len(m), "n_unmatched": int((m["_merge"] != "both").sum())}
    if has_min:
        out["max_abs_diff"] = float((m["minutes_at_position_stats"] - m["minutes_at_position_profile"]).abs().max())
    return out

def cluster_slot_mix(profile_wide: pd.DataFrame, cluster_col: str, position_group: str) -> pd.DataFrame:
    """Minutes-weighted mean slot shares per cluster: which roles each archetype occupies."""
    p = profile_wide[(profile_wide["position_group"] == position_group) & profile_wide[cluster_col].notna()]
    cols = [c for c in p.columns if c.startswith("slot_share_")]
    cols = [c for c in cols if p[c].abs().sum() > 0]
    w = p["minutes_at_position"]
    num = p[cols].mul(w, axis=0).groupby(p[cluster_col]).sum()
    return num.div(w.groupby(p[cluster_col]).sum(), axis=0)

# --------------------------------------------------------------------------- #
# Step 3: archetype usage per team (call once per position group)
# --------------------------------------------------------------------------- #
def team_position_shares(usage: pd.DataFrame, position_group: str, archetype_col: str,
                         include_unclassified: bool = False) -> pd.DataFrame:
    """Minutes-weighted archetype shares for one position group, one row per team.
    Shares sum to 1 across archetypes. `<PG>__coverage` = classified minutes / all minutes in the
    position group; filter or flag teams with low coverage before interpreting."""
    pre = position_group.replace("/", "")
    u = usage[usage["position_group"] == position_group].copy()
    total = u.groupby("team_id")["minutes"].sum()
    classified = u.loc[u[archetype_col].notna()].groupby("team_id")["minutes"].sum()
    coverage = (classified / total).reindex(total.index).fillna(0.0)
 
    u["arch"] = u[archetype_col]
    if include_unclassified:
        u["arch"] = u["arch"].fillna("unclassified")
    else:
        u = u[u["arch"].notna()]
    m = u.pivot_table(index="team_id", columns="arch", values="minutes", aggfunc="sum", fill_value=0.0)
    shares = m.div(m.sum(axis=1), axis=0)
    shares.columns = [f"{pre}__{c}" for c in shares.columns]
 
    out = total.rename(f"{pre}__minutes").to_frame().join(coverage.rename(f"{pre}__coverage")).join(shares)
    assert np.allclose(shares.sum(axis=1).dropna(), 1.0)
    return out

def sim_cols_for(usage, pg, k):
    pre = pg.replace('/', '')
    return sorted(c for c in usage.columns if c.startswith(f'{pre}__sim_cluster_') and c.endswith(f'_k{k}')) 

def team_position_weighted_mean(usage: pd.DataFrame, position_group: str,
                                cols: list[str], prefix: str) -> pd.DataFrame:
    """Minutes-weighted mean of numeric columns (soft memberships or z-scored style features)
    over classified players of one position group, one row per team."""
    pre = position_group.replace("/", "")
    u = usage[usage["position_group"] == position_group].dropna(subset=list(cols))
    w = u["minutes"]
    num = u[list(cols)].mul(w, axis=0).groupby(u["team_id"]).sum()
    den = w.groupby(u["team_id"]).sum()
    out = num.div(den, axis=0)
    out.columns = [f"{pre}__{prefix}_{c}" for c in cols]
    return out

def team_soft_shares(usage: pd.DataFrame, position_group: str, sim_cols: list[str],
                     normalize: bool = True) -> pd.DataFrame:
    """SOFT archetype shares, one row per team: minutes-weighted average of each player's similarity
    to each archetype (instead of counting a player's minutes fully toward ONE archetype).
    `sim_cols` = that group's attached similarity columns, e.g. ['FullWingBack__sim_cluster_0_k3', ...]
    (all from ONE k). Each player's similarities are rescaled to sum to 1 first (`normalize`), so the
    output shares sum to 1 per team and drop straight into composition_context_correlations / team_distance.
    Players with any missing similarity are skipped; a team with none gets NaN (same as the hard shares).
    Output columns: `<PG>__soft_<j>` for cluster j."""
    pre = position_group.replace("/", "")
    u = usage[usage["position_group"] == position_group].dropna(subset=list(sim_cols))
    S = u[list(sim_cols)].astype(float)
    if normalize:
        S = S.div(S.sum(axis=1), axis=0)
    w = u["minutes"]
    out = S.mul(w, axis=0).groupby(u["team_id"]).sum().div(w.groupby(u["team_id"]).sum(), axis=0)
    idx = [re.search(r"sim_cluster_(\d+)_k", c).group(1) for c in sim_cols]   # cluster number from the column name
    out.columns = [f"{pre}__soft_{j}" for j in idx]
    assert np.allclose(out.sum(axis=1), 1.0) or not normalize
    return out

def team_soft_path_shares(usage: pd.DataFrame, position_group: str, parent_col: str = "cluster_l1",
                          child_sims: dict | None = None, normalize: bool = True) -> pd.DataFrame:
    """SOFT shares for a two-level (parent -> sub-cluster) group such as CM: the soft counterpart of
    team_position_shares(..., 'cluster_path'). One row per team; columns `<PG>__soft_<parent>_<child>`
    (mirrors the hard path names `<PG>__<parent>_<child>`), summing to 1 over all paths.
 
    HARD parent, SOFT child: a player's minutes go to the parent they were assigned to, and are split
    across that parent's sub-clusters by their (normalised) sub-cluster similarities. The sub-cluster
    similarities only exist for the assigned parent (NaN under the other parents - the sub-clusterings
    never scored them), so the player's soft-ness BETWEEN parents cannot be carried to path level; that
    part is what team_soft_shares(...) on the parent similarities captures.
    `child_sims` = {parent_label: [that parent's child similarity columns]}; if None it is discovered
    from columns named `sub<parent>_sim_cluster_<c>_k<K>` (as made by combine_hierarchical_clusters).
    Players with no child similarities are skipped, like the hard path shares skip cluster_path = NaN."""
    pre = position_group.replace("/", "")
    if child_sims is None:
        found = {}
        for c in usage.columns:
            m = re.match(r"sub(.+?)_sim_cluster_(\d+)_k(\d+)$", str(c))
            if m:
                found.setdefault(m.group(1), []).append(c)
        child_sims = {p: sorted(cols) for p, cols in sorted(found.items())}
    assert child_sims, "no child similarity columns found - pass child_sims={parent: [cols]}"
    u = usage[usage["position_group"] == position_group]
    nums, dens = [], []
    for p, cols in child_sims.items():
        up = u[u[parent_col].astype(str) == str(p)].dropna(subset=list(cols))
        S = up[list(cols)].astype(float)
        if normalize:
            S = S.div(S.sum(axis=1), axis=0)
        num = S.mul(up["minutes"], axis=0).groupby(up["team_id"]).sum()
        num.columns = [f"{pre}__soft_{p}_" + re.search(r"sim_cluster_(\d+)_k", c).group(1) for c in cols]
        nums.append(num)
        dens.append(up["minutes"].groupby(up["team_id"]).sum())
    num = pd.concat(nums, axis=1).fillna(0.0)            # a team with no players under a parent: share 0 there
    den = pd.concat(dens, axis=1).sum(axis=1)
    out = num.div(den, axis=0)
    assert np.allclose(out.sum(axis=1), 1.0) or not normalize
    return out

# --------------------------------------------------------------------------- #
# Step 4: who is used (player level) and how concentrated (team level)
# --------------------------------------------------------------------------- #
def player_usage(minutes_df: pd.DataFrame, position_group: str, core_cum: float = 0.8) -> pd.DataFrame:
    """Player-level minutes share within team x position group. `is_core` marks the smallest set of
    players (ranked by minutes) covering `core_cum` of the group's minutes."""
    u = minutes_df[minutes_df["position_group"] == position_group].copy()
    u["minutes_share"] = u["minutes"] / u.groupby("team_id")["minutes"].transform("sum")
    u = u.sort_values(["team_id", "minutes"], ascending=[True, False])
    u["rank"] = u.groupby("team_id").cumcount() + 1
    before = u.groupby("team_id")["minutes_share"].cumsum() - u["minutes_share"]
    u["is_core"] = before < core_cum
    return u
 
 
def usage_shape(pu: pd.DataFrame, position_group: str) -> pd.DataFrame:
    pre = position_group.replace("/", "")
    g = pu.groupby("team_id")
    return pd.DataFrame({
        f"{pre}__n_used": g.size(),
        f"{pre}__top1_share": g["minutes_share"].max(),
        f"{pre}__effective_n": g["minutes_share"].apply(lambda s: 1.0 / np.square(s).sum()),
        f"{pre}__n_core": g["is_core"].sum(),
    })

# --------------------------------------------------------------------------- #
# Step 3b: archetype usage BY FORMATION (team_position_shares split by formation)
# --------------------------------------------------------------------------- #
def team_position_shares_by_formation(usage: pd.DataFrame, position_group: str, archetype_col: str,
                                      min_formation_minutes: float = 180.0,
                                      include_unclassified: bool = False) -> pd.DataFrame:
    """Like team_position_shares, but one row per (team_id, formation): minutes-weighted archetype
    shares for that team's players in position_group, WHILE PLAYING that formation. `reliable` flags
    team-formation cells with too few minutes to trust the split (mirrors player_slot_by_formation's
    threshold in formation_slots.py). `usage` = position_group_minutes_by_formation + attach_cluster_info."""
    pre = position_group.replace("/", "")
    u = usage[usage["position_group"] == position_group].copy()
    idx = ["team_id", "formation"]
    total = u.groupby(idx)["minutes"].sum()
    classified = u.loc[u[archetype_col].notna()].groupby(idx)["minutes"].sum()
    coverage = (classified / total).reindex(total.index).fillna(0.0)
 
    u["arch"] = u[archetype_col]
    if include_unclassified:
        u["arch"] = u["arch"].fillna("unclassified")
    else:
        u = u[u["arch"].notna()]
    m = u.pivot_table(index=idx, columns="arch", values="minutes", aggfunc="sum", fill_value=0.0)
    shares = m.div(m.sum(axis=1), axis=0)
    shares.columns = [f"{pre}__{c}" for c in shares.columns]
 
    out = total.rename(f"{pre}__minutes").to_frame().join(coverage.rename(f"{pre}__coverage")).join(shares)
    out[f"{pre}__reliable"] = out[f"{pre}__minutes"] >= min_formation_minutes
    assert np.allclose(shares.sum(axis=1).dropna(), 1.0)
    return out.reset_index()

def slot_archetype_mix(occupancy: pd.DataFrame, position_group: str, archetype_col: str,
                       include_unclassified: bool = False) -> pd.DataFrame:
    """Which archetype fills which EXACT slot, per team and formation - one row per
    (team_id, formation, position_name). Columns are archetype shares of that slot's minutes
    (minutes-weighted, so a slot rotated between two different-archetype players over the season
    shows a real split, not just its most-used player's type). `occupancy` is occupancy_c from
    Stage B (already carries `minutes` and the attached cluster columns)."""
    pre = position_group.replace("/", "")
    o = occupancy[occupancy["position_group"] == position_group].copy()
    idx = ["team_id", "formation", "position_name"]
    o["arch"] = o[archetype_col]
    if include_unclassified:
        o["arch"] = o["arch"].fillna("unclassified")
    else:
        o = o[o["arch"].notna()]
    m = o.pivot_table(index=idx, columns="arch", values="minutes", aggfunc="sum", fill_value=0.0)
    shares = m.div(m.sum(axis=1), axis=0)
    shares.columns = [f"{pre}__{c}" for c in shares.columns]
    assert np.allclose(shares.sum(axis=1).dropna(), 1.0)
    return shares.reset_index()

def shares(t, pre):
    return [c for c in t.columns if c.startswith(pre + '__') and not c.endswith(('__minutes', '__coverage'))]

def _bh(p: np.ndarray) -> np.ndarray:
    flat = p.ravel()
    order = np.argsort(flat)
    ranked = flat[order] * len(flat) / (np.arange(len(flat)) + 1)
    adj = np.minimum.accumulate(ranked[::-1])[::-1].clip(max=1.0)
    out = np.empty_like(flat)
    out[order] = adj
    return out.reshape(p.shape)

def composition_context_correlations(team_wide: pd.DataFrame, share_cols: list[str],
                                     context_cols: list[str], n_perm: int = 5000, seed: int = 42):
    """Spearman r between archetype shares and team context, with permutation p-values and
    Benjamini-Hochberg adjusted p. With k=2 pass ONE share column per position group
    (the other is 1 - it). Complete cases only."""
    d = team_wide[share_cols + context_cols].dropna()
    keep_x = [c for c in share_cols if d[c].nunique() > 1]
    keep_y = [c for c in context_cols if d[c].nunique() > 1]
    X = d[keep_x].rank().to_numpy(float)
    Y = d[keep_y].rank().to_numpy(float)
    X = (X - X.mean(0)) / X.std(0)
    Y = (Y - Y.mean(0)) / Y.std(0)
    n = len(d)
    obs = X.T @ Y / n
    rng = np.random.default_rng(seed)
    exceed = np.zeros_like(obs)
    for _ in range(n_perm):
        exceed += np.abs(X[rng.permutation(n)].T @ Y / n) >= np.abs(obs) - 1e-12
    p = (exceed + 1) / (n_perm + 1)
    mk = lambda a: pd.DataFrame(a, index=keep_x, columns=keep_y)
    return mk(obs), mk(p), mk(_bh(p))

def tidy(r, p, p_adj):
    out = pd.concat({'r': r.stack(), 'p': p.stack(), 'p_adj': p_adj.stack()}, axis=1)
    out.index.names = ['share', 'context']
    return out.sort_values('p_adj')

def compare_runs(r, p, a, rr, pr, ar):
    t_raw = tidy(r, p, a).reset_index()
    t_adj = tidy(rr, pr, ar).reset_index()
    t_adj['context'] = t_adj['context'].str.replace('_resid', '_z', regex=False)
    m = t_raw.merge(t_adj, on=['share', 'context'], suffixes=('_raw', '_adj'))
    return m[(m.p_adj_raw < 0.10) | (m.p_adj_adj < 0.10)].sort_values('p_adj_adj')[
        ['share', 'context', 'r_raw', 'p_adj_raw', 'r_adj', 'p_adj_adj']]

def league_sign_consistency(team_wide: pd.DataFrame, league: pd.Series, x: str, y: str,
                            min_n: int = 5) -> pd.DataFrame:
    """Per-league Spearman r for one (share, context) pair - the 'holds in >=3 of 4 leagues' check."""
    d = team_wide[[x, y]].join(league.rename("league")).dropna()
    rows = []
    for lg, g in d.groupby("league"):
        r = stats.spearmanr(g[x], g[y])[0] if len(g) >= min_n else np.nan
        rows.append((lg, len(g), r))
    return pd.DataFrame(rows, columns=["league", "n", "spearman_r"])

def league_check(team_wide, r, p, a, cutoff=0.05):
    t = tidy(r, p, a).reset_index()
    cands = t[t['p_adj'] < cutoff]
    rows = []
    for _, c in cands.iterrows():
        lc = league_sign_consistency(team_wide, team_wide['league'], c['share'], c['context'], min_n=5)
        rows.append(dict(share=c['share'], context=c['context'], r_pooled=c['r'], p_adj=c['p_adj'],
                         same_sign=int((np.sign(lc['spearman_r']) == np.sign(c['r'])).sum()),
                         leagues=int(lc['spearman_r'].notna().sum()),
                         **{lg: r_ for lg, r_ in zip(lc['league'], lc['spearman_r'])}))
    return pd.DataFrame(rows)

def compare_groups(df: pd.DataFrame, flag: pd.Series, cols: list[str], n_boot: int = 5000,
                   seed: int = 42) -> pd.DataFrame:
    """Descriptive comparison of a small group of teams (flag True, e.g. the 7 wingerless sides)
    against the rest, one row per column in `cols` (pick them BEFORE looking at results).
    gap = group median - rest median (in the columns' own units; z units for *_z columns),
    ci_low/ci_high = 95% bootstrap interval for that gap, n_below/n_above_rest_median = how many
    group teams sit on each side of the rest's median (consistency). No p-values: descriptive only."""
    flag = flag.reindex(df.index).fillna(False).astype(bool)
    rng = np.random.default_rng(seed)
    rows = {}
    for c in cols:
        a = df.loc[flag, c].dropna().to_numpy(float)
        b = df.loc[~flag, c].dropna().to_numpy(float)
        boots = (np.median(rng.choice(a, size=(n_boot, len(a))), axis=1)
                 - np.median(rng.choice(b, size=(n_boot, len(b))), axis=1))
        lo, hi = np.percentile(boots, [2.5, 97.5])
        mb = np.median(b)
        rows[c] = dict(median_group=np.median(a), median_rest=mb, gap=np.median(a) - mb,
                       ci_low=lo, ci_high=hi,
                       n_below_rest_median=int((a < mb).sum()), n_above_rest_median=int((a > mb).sum()),
                       n_group=len(a), n_rest=len(b))
    return pd.DataFrame(rows).T

def team_distance_partial(team_wide: pd.DataFrame, share_groups: dict, context_cols: list, w_comp: float = 0.5,
                          none_groups=()) -> pd.DataFrame:
    """share_groups = {group: [ALL share columns of that group]} (each set sums to 1 -> Hellinger).
    Composition distance of a pair = mean of the per-group Hellinger distances over the groups defined for BOTH teams.
    none_groups: groups whose NaN means 'no classified use' and should count as a distinct category (a team with no
    classified minutes is then maximally different from teams that have some, and identical to other such teams)
    instead of being skipped. Context columns must be complete (teams with a NaN there are dropped).
    Each component is divided by its median off-diagonal distance before weighting, as in team_distance.
    Without any NaN the result equals team_profile.team_distance exactly."""
    ctx_df = team_wide[list(context_cols)].dropna()
    idx = ctx_df.index
    n = len(idx)
    num, cnt = np.zeros((n, n)), np.zeros((n, n))
    for g, cs in share_groups.items():
        S = team_wide.loc[idx, cs].to_numpy(float)
        ok = ~np.isnan(S).any(axis=1)
        P = np.sqrt(np.where(ok[:, None], S, 0.0))
        if g in none_groups:                                           # an extra 'none' dimension: 1 for teams without classified use
            P = np.hstack([P, (~ok).astype(float)[:, None]])
            pair = np.ones((n, n), dtype=bool)
        else:
            pair = np.outer(ok, ok)
        dist = spatial.distance.cdist(P, P) / np.sqrt(2)
        num += np.where(pair, dist, 0.0)
        cnt += pair
    comp = np.divide(num, cnt, out=np.full_like(num, np.nan), where=cnt > 0)
    Z = ctx_df.to_numpy(float)
    ctx = spatial.distance.cdist(Z, Z)
    off = ~np.eye(n, dtype=bool)
    comp_n = comp / np.nanmedian(comp[off])
    ctx_n = ctx / np.median(ctx[off])
    D = np.where(np.isnan(comp_n), ctx_n, w_comp * comp_n + (1 - w_comp) * ctx_n)     # pairs with no common group: context only
    np.fill_diagonal(D, 0.0)
    return pd.DataFrame(D, index=idx, columns=idx)

def neighbours(D, league, k=5):
    rows = []
    for t in D.index:
        for rank, (j, d) in enumerate(D[t].drop(t).nsmallest(k).items(), 1):
            rows.append(dict(team_id=t, rank=rank, neighbour=j, distance=d,
                             same_league=league[t] == league[j]))
    return pd.DataFrame(rows)

def strength_gap(team_wide, Dx, k=5):
    s = team_wide.loc[Dx.index, 'context_score']
    nn_gap = np.mean([(s[Dx[t].drop(t).nsmallest(k).index] - s[t]).abs().mean() for t in Dx.index])
    diff = np.abs(s.values[:, None] - s.values[None, :])
    all_gap = diff[~np.eye(len(s), dtype=bool)].mean()
    return nn_gap / all_gap

def top_k_overlap(D1, D2, k=5):
    return pd.Series({t: len(set(D1[t].drop(t).nsmallest(k).index) & set(D2[t].drop(t).nsmallest(k).index)) for t in D1.index})

def explain_pair(team_wide, share_groups, a, b, cols, Dc, Ds, n=6, labels=None):
    """Why are teams a and b close (or not)? Squad side and style side, side by side.
    cols: style columns (main: *_z, adjusted: *_adj). Dc: squad distance matrix. Ds: style distance matrix."""
    labels = labels or {}
    na, nb_ = team_wide.loc[a, 'team'], team_wide.loc[b, 'team']
    off = ~np.eye(len(Dc), dtype=bool)
    closer_than = lambda Dx: (Dx.to_numpy()[off] > Dx.loc[a, b]).mean()      # share of all pairs that are further apart

    print(f"{na} ({team_wide.loc[a, 'league']}, strength {team_wide.loc[a, 'context_score']})  vs  "
          f"{nb_} ({team_wide.loc[b, 'league']}, strength {team_wide.loc[b, 'context_score']})")
    print(f"Squad: closer than {closer_than(Dc) * 100}% of pairs | Style: closer than {closer_than(Ds) * 100}% of pairs\n")

    rows = []
    for g, cs in share_groups.items():
        pa = team_wide.loc[a, cs].astype(float).to_numpy()
        pb = team_wide.loc[b, cs].astype(float).to_numpy()
        h = np.sqrt(((np.sqrt(pa) - np.sqrt(pb)) ** 2).sum() / 2)
        for c, x, y in zip(cs, pa, pb):
            rows.append({'group': g, 'archetype': labels.get(c, c), na: x, nb_: y, 'group_difference': h})
    squad = pd.DataFrame(rows).set_index(['group', 'archetype'])

    z = team_wide.loc[[a, b], cols].T.astype(float)
    z.columns = [na, nb_]
    z.index = z.index.str.replace(r'_(z|adj)$', '', regex=True)
    same_side = np.sign(z[na]) == np.sign(z[nb_])
    z['shared_strength'] = np.where(same_side, np.minimum(z[na].abs(), z[nb_].abs()), 0.0)
    z['gap'] = (z[na] - z[nb_]).abs()
    shared = z.nlargest(n, 'shared_strength')[[na, nb_]]
    differ = z.nlargest(n, 'gap')[[na, nb_, 'gap']]

    print('Squad build (share of minutes; group_difference 0 = same mix, 1 = nothing in common):')
    print(squad.to_string(), '\n')
    print('Shared style traits (both above or both below their league average):')
    print(shared.to_string(), '\n')
    print('Biggest style differences:')
    print(differ.to_string(), '\n')
    return squad, shared, differ

def tukey_high(s):
    q1, q3 = s.quantile([0.25, 0.75])
    return s > q3 + 1.5 * (q3 - q1)

def curvature_scan(df, adj_cols, ctx_col='context_score', exclude_team=937, top=10):
    """How strongly each adjusted feature still bends with team strength (U-shape), with and without one team."""
    ctx = df[ctx_col]
    ctx_sq = (ctx - ctx.mean()) ** 2
    all_teams = df[adj_cols].corrwith(ctx_sq, method='spearman')
    mask = df.index.get_level_values('team_id') != exclude_team
    without = df.loc[mask, adj_cols].corrwith(ctx_sq[mask], method='spearman')
    out = pd.DataFrame({'all_teams': all_teams, 'without_barcelona': without})
    return out.reindex(all_teams.abs().sort_values(ascending=False).index).head(top)

def plot_team_cluster_comparison(df, feature_list, cluster_col, n_clusters, group_name, suffix,
                                 league=None, position="teams", save=False):
    data = df if league is None else df[df["league"] == league]
    pct_series_dict, raw_series_dict = {}, {}
    for c in sorted(df[cluster_col].dropna().unique()):
        members = data[data[cluster_col] == c]
        if members.empty:
            continue
        label = f"{cluster_col} {int(c)}"
        pct_series_dict[label], raw_series_dict[label] = _series_for(members, feature_list, suffix)

    where = "" if league is None else f", {league}"
    league_slug = None if league is None else str(league).replace('/', '-').replace(' ', '_').replace("'", '')
    chart_name = f"{group_name}_{suffix_label(suffix)}"
    if league_slug:
        chart_name += f"_{league_slug}"

    return build_radar_chart(feature_list, pct_series_dict,
                             f"{group_name} — {cluster_col} comparison{where} ({suffix_label(suffix)})",
                             raw_series_dict=raw_series_dict, save=save, position=position,
                             n_clusters=n_clusters, folder_name=None,
                             chart_name=chart_name, value_label=value_label_for(suffix))

def plot_team_vs_cluster(df, team_id, feature_list, cluster_col, n_clusters, group_name, suffix,
                         team_id_to_team, team_id_to_league, own_league=False, leave_one_out=True,
                         position="teams", save=False):
    row = df.loc[team_id]
    if pd.isna(row[cluster_col]):
        return None
    c = int(row[cluster_col])
    members = df[df[cluster_col] == c]
    if own_league:
        members = members[members["league"] == row["league"]]
    if leave_one_out:                                    # the team itself is not part of the average
        members = members.drop(index=team_id, errors="ignore")
    if members.empty:                                    # e.g. only team of its cluster in its league
        return None
 
    display_name = get_display_name(team_id, team_id, team_id_to_team, team_id_to_league)
    scope = "league only" if own_league else "all teams" 
    avg_label = f"Cluster {c} avg" + (f", {row['league']}" if own_league else "") + f" ({len(members)} teams)"
    pct_series_dict, raw_series_dict = {}, {}
    pct_series_dict[avg_label], raw_series_dict[avg_label] = _series_for(members, feature_list, suffix)
    pct_series_dict[display_name], raw_series_dict[display_name] = _series_for(row, feature_list, suffix)
 
    similarity_scores = None
    sim_cols = [f"sim_cluster_{i}_k{n_clusters}" for i in range(n_clusters)]
    if all(col in df.columns for col in sim_cols):
        sims = row[sim_cols].astype(float)
        similarity_scores = {f"Cluster {i}": v / sims.sum() for i, v in enumerate(sims)}
 
    return build_radar_chart(feature_list, pct_series_dict,
                             f"{group_name} — {display_name} ({suffix_label(suffix)}) · {scope}",
                             raw_series_dict=raw_series_dict, save=save, position=position,
                             n_clusters=n_clusters,
                             folder_name=get_folder_name(team_id, team_id, team_id_to_team, team_id_to_league),
                             chart_name=f"{group_name}_{suffix_label(suffix)}" + ("_league" if own_league else ""),
                             similarity_scores=similarity_scores, highlight_label=f"Cluster {c}", value_label=value_label_for(suffix))
 
 
def plot_team_vs_league_cluster(df, team_id, feature_list, cluster_col, n_clusters, group_name, suffix,
                                team_id_to_team, team_id_to_league, leave_one_out=True,
                                position="teams", save=False):
    return plot_team_vs_cluster(df, team_id, feature_list, cluster_col, n_clusters, group_name, suffix,
                                team_id_to_team, team_id_to_league, own_league=True,
                                leave_one_out=leave_one_out, position=position, save=save)
 
 
def export_team_cluster_comparison_charts(df, feature_groups, cluster_col, n_clusters,
                                          suffixes=("_adj", ""), position="teams"):
    paths = []
    for suffix in suffixes:
        for group_name, feature_list in feature_groups.items():
            paths.append(plot_team_cluster_comparison(df, feature_list, cluster_col, n_clusters, group_name,
                                                      suffix, position=position, save=True))
    return paths
 
 
def export_team_cluster_comparison_charts_by_league(df, feature_groups, cluster_col, n_clusters,
                                                    suffixes=("_adj", ""), position="teams"):
    paths = []
    for league in sorted(df["league"].dropna().unique()):
        for suffix in suffixes:
            for group_name, feature_list in feature_groups.items():
                paths.append(plot_team_cluster_comparison(df, feature_list, cluster_col, n_clusters, group_name,
                                                          suffix, league=league, position=position, save=True))
    return paths
 
 
def export_all_team_cluster_charts(df, feature_groups, cluster_col, n_clusters, team_id_to_team,
                                   team_id_to_league, suffixes=("_adj", ""), team_ids=None, position="teams"):
    paths = []
    for team_id in (team_ids if team_ids is not None else df.index):
        for suffix in suffixes:
            for group_name, feature_list in feature_groups.items():
                p = plot_team_vs_cluster(df, team_id, feature_list, cluster_col, n_clusters, group_name, suffix,
                                         team_id_to_team, team_id_to_league, position=position, save=True)
                if p:
                    paths.append(p)
    return paths
 
 
def export_all_team_cluster_charts_league_aware(df, feature_groups, cluster_col, n_clusters, team_id_to_team,
                                                team_id_to_league, suffixes=("_adj", ""), team_ids=None,
                                                position="teams"):
    """Per team: vs its cluster within its own league only."""
    paths = []
    for team_id in (team_ids if team_ids is not None else df.index):
        for suffix in suffixes:
            for group_name, feature_list in feature_groups.items():
                p = plot_team_vs_league_cluster(df, team_id, feature_list, cluster_col, n_clusters, group_name,
                                                suffix, team_id_to_team, team_id_to_league, position=position,
                                                save=True)
                if p:
                    paths.append(p)
    return paths

slots = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]

def group_flow(label_frame, level_names, level_colours=None, level_titles=None, gap=2.0,
               min_count_label=2, number_pad=0.07,
               title="How teams move between groups as k grows"):
    """Alluvial diagram. label_frame: one column per level (e.g. kmeans_2/3/4_cluster), index = team_id.
    level_names: {column: {label: name}} - dict order = top-to-bottom order of the blocks.
    level_colours: {column: {label: hex}}; ribbons take the colour of the block they leave."""
    cols = list(level_names)
    level_colours = level_colours or {c: {g: slots[i] for i, g in enumerate(level_names[c])} for c in cols}
    n = len(label_frame)
    w = 0.10
    blocks = {}
    for j, c in enumerate(cols):
        counts = label_frame[c].value_counts()
        groups = [g for g in level_names[c] if counts.get(g, 0) > 0]
        total = n + gap * (len(groups) - 1)
        top = total / 2
        for g in groups:
            h = counts[g]
            blocks[(c, g)] = [j, top, top - h]
            top -= h + gap
    fig, ax = plt.subplots(figsize=(10, 7))
    for (c, g), (j, y0, y1) in blocks.items():
        ax.add_patch(Rectangle((j - w / 2, y1), w, y0 - y1, color=level_colours[c][g], zorder=3))
        shift = number_pad if j < len(cols) - 1 else 0.0
        ax.text(j + w / 2 + 0.02 + shift, (y0 + y1) / 2, f"{level_names[c][g]}\n{int(y0 - y1)} teams",
                va="center", ha="left", fontsize=8, color=ink, zorder=5,
                bbox=dict(boxstyle="round,pad=0.15", facecolor=surface, edgecolor="none", alpha=0.85))
    tt = np.linspace(0, 1, 200)         # add once, just before the `for a, b in zip(cols[:-1], cols[1:])` loop
    for a, b in zip(cols[:-1], cols[1:]):
        ct = pd.crosstab(label_frame[a], label_frame[b])
        out_cursor = {g: blocks[(a, g)][1] for g in ct.index if (a, g) in blocks}
        in_cursor = {g: blocks[(b, g)][1] for g in ct.columns if (b, g) in blocks}
        src_order = [g for g in level_names[a] if g in ct.index]
        dst_order = [g for g in level_names[b] if g in ct.columns]
        flows = {}
        for ga in src_order:                              # leave each source block in target order
            for gb in dst_order:
                m = int(ct.loc[ga, gb])
                if m:
                    flows[(ga, gb)] = [out_cursor[ga], out_cursor[ga] - m]
                    out_cursor[ga] -= m
        for gb in dst_order:                              # arrive at each target block in source order
            for ga in src_order:
                if (ga, gb) in flows:
                    m = flows[(ga, gb)][0] - flows[(ga, gb)][1]
                    flows[(ga, gb)] += [in_cursor[gb], in_cursor[gb] - m]
                    in_cursor[gb] -= m
        ja, jb = cols.index(a), cols.index(b)
        x0, x1 = ja + w / 2, jb - w / 2
        xm = (x0 + x1) / 2
        for (ga, gb), (s0, s1, t0, t1) in flows.items():
            verts = [(x0, s0), (xm, s0), (xm, t0), (x1, t0), (x1, t1), (xm, t1), (xm, s1), (x0, s1), (x0, s0)]
            codes = [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4, Path.LINETO,
                     Path.CURVE4, Path.CURVE4, Path.CURVE4, Path.CLOSEPOLY]
            ax.add_patch(PathPatch(Path(verts, codes), facecolor=level_colours[a][ga], edgecolor="none",
                                   alpha=0.35, zorder=2))
            m = int(round(s0 - s1))
            if m >= min_count_label:
                ax.text(x0 + 0.035, (s0 + s1) / 2, str(m), ha="center", va="center",
                        fontsize=7, color=ink2, zorder=4)
    for j, c in enumerate(cols):
        ax.text(j, n / 2 + gap * 2.2, (level_titles or {}).get(c, c), ha="center", va="bottom",
                fontsize=10, fontweight="bold", color=ink)
    ax.set_xlim(-0.3, len(cols) - 0.3)
    ax.set_ylim(-n / 2 - gap * 2.5, n / 2 + gap * 4.0)
    ax.axis("off")
    ax.set_title(title, loc="left", fontsize=11)
    ax.text(0, 0.0, "Ribbon width = number of teams; numbers on ribbons = teams moving along that path.",
            transform=ax.transAxes, fontsize=7.5, color=muted)
    return fig

def export_group_flow(team_wide, ks=(2, 3, 4), fig_dir=player_fig_dir, position="teams", filename="group_flow.png",
                      dpi=200, **kwargs):
    """-> <fig_dir>/<position>/all_k/group_flow.png. Groups are named 'Cluster g' with the radar colours."""
    cols = [f"kmeans_{k}_cluster" for k in ks]
    label_frame = team_wide[cols].dropna().astype(int)
    level_names = {c: {g: f"Cluster {g}" for g in sorted(label_frame[c].unique())} for c in cols}
    level_colours = {c: {g: slots[g] for g in level_names[c]} for c in cols}
    level_titles = {f"kmeans_{k}_cluster": f"k = {k}" for k in ks}
    fig = group_flow(label_frame, level_names, level_colours, level_titles, **kwargs)
    out_dir = os.path.join(fig_dir, position, "all_k")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, filename)
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    return path

slot_xy = {   # vertical pitch, x across (0-80, team's left on the left), y up (0 own goal -> 120)
    "Goalkeeper": (40, 7),
    "Right Back": (68, 34), "Right Center Back": (53, 22), "Center Back": (40, 20),
    "Left Center Back": (27, 22), "Left Back": (12, 34),
    "Right Wing Back": (72, 50), "Left Wing Back": (8, 50),
    "Right Defensive Midfield": (52, 42), "Center Defensive Midfield": (40, 40), "Left Defensive Midfield": (28, 42),
    "Right Midfield": (70, 64), "Right Center Midfield": (54, 56), "Center Midfield": (40, 56),
    "Left Center Midfield": (26, 56), "Left Midfield": (10, 64),
    "Right Wing": (68, 86), "Right Attacking Midfield": (54, 76), "Center Attacking Midfield": (40, 76),
    "Left Attacking Midfield": (26, 76), "Left Wing": (12, 86),
    "Right Center Forward": (50, 98), "Center Forward": (40, 100), "Striker": (40, 100),
    "Left Center Forward": (30, 98), "Secondary Striker": (40, 88),
}

def formation_text(f) -> str:
    return "-".join(str(int(f)))

def _draw_pitch(ax, line=axis_colour):
    """Plain vertical pitch, 80 wide x 120 long, own goal at the bottom."""
    kw = dict(fill=False, edgecolor=line, linewidth=1.0)
    ax.add_patch(Rectangle((0, 0), 80, 120, **kw))
    ax.plot([0, 80], [60, 60], color=line, linewidth=1.0)
    ax.add_patch(Circle((40, 60), 10, **kw))
    for y0, h in [(0, 18), (102, 18)]:
        ax.add_patch(Rectangle((18, y0), 44, h, **kw))
    for y0, h in [(0, 6), (114, 6)]:
        ax.add_patch(Rectangle((30, y0), 20, h, **kw))
    ax.add_patch(Arc((40, 12), 20, 20, theta1=37, theta2=143, **{k: v for k, v in kw.items() if k != "fill"}))
    ax.add_patch(Arc((40, 108), 20, 20, theta1=217, theta2=323, **{k: v for k, v in kw.items() if k != "fill"}))
    ax.set_xlim(-2, 82); ax.set_ylim(-2, 122); ax.set_aspect("equal"); ax.axis("off")

def formation_minutes(occ: pd.DataFrame) -> pd.DataFrame:
    """Minutes and share of minutes per team x formation, read from the occupancy table
    (goalkeeper slot minutes = minutes the team spent in that formation)."""
    gk = occ[occ["position_group"] == "Goalkeeper"]
    m = gk.groupby(["team_id", "formation"])["minutes"].sum().rename("minutes").reset_index()
    m["share"] = m["minutes"] / m.groupby("team_id")["minutes"].transform("sum")
    return m.sort_values(["team_id", "minutes"], ascending=[True, False]).reset_index(drop=True)

def typical_xi(occ: pd.DataFrame, team_id, formation=None, n_slots: int = 11) -> pd.DataFrame:
    """Most-used player per slot in the team's most-used formation (or the formation given).
    Keeps the n_slots slots with the most minutes, so odd one-off slot names drop out.
    Adds the second-choice player and her share, so rotation is visible."""
    fm = formation_minutes(occ)
    fm = fm[fm["team_id"] == team_id]
    form = fm.iloc[0]["formation"] if formation is None else formation
    o = occ[(occ["team_id"] == team_id) & (occ["formation"] == form)]
    slots = (o.groupby("position_name")["slot_minutes"].first().sort_values(ascending=False).index[:n_slots])
    first = o[(o["position_name"].isin(slots)) & (o["rank_in_slot"] == 1)].set_index("position_name")
    second = o[(o["position_name"].isin(slots)) & (o["rank_in_slot"] == 2)].set_index("position_name")
    out = first[["position_group", "player_id", "share_of_slot", "slot_minutes"]].copy()
    out["second_player_id"] = second["player_id"].reindex(out.index)
    out["second_share"] = second["share_of_slot"].reindex(out.index)
    out.attrs.update(formation=form, formation_share=float(fm.set_index("formation").loc[form, "share"]))
    return out

def _spread_rows(pos, min_dx=24.0, row_tol=4.0, lo=8.0, hi=72.0):
    """Push dots in the same row apart (back three, front two ...) so their labels fit side by side.
    pos = {slot: (x, y)}; slots whose y differs by less than row_tol count as one row."""
    out = dict(pos)
    order = sorted(out, key=lambda s: out[s][1])
    rows, cur = [], []
    for s in order:
        if cur and out[s][1] - out[cur[-1]][1] > row_tol:
            rows.append(cur); cur = []
        cur.append(s)
    if cur:
        rows.append(cur)
    for row in rows:
        if len(row) < 2:
            continue
        row.sort(key=lambda s: out[s][0])
        xs = [out[s][0] for s in row]
        gap = min(min_dx, (hi - lo) / (len(row) - 1))
        for _ in range(100):
            moved = False
            for i in range(1, len(xs)):
                d = xs[i] - xs[i - 1]
                if d < gap - 1e-6:
                    xs[i - 1] -= (gap - d) / 2; xs[i] += (gap - d) / 2; moved = True
            xs = [min(max(v, lo), hi) for v in xs]
            if not moved:
                break
        for s, v in zip(row, xs):
            out[s] = (v, out[s][1])
    return out

def plot_typical_xi(occ: pd.DataFrame, team_id, team_names: pd.Series, player_names: dict,
                    archetype_of: dict | None = None, formation=None,
                    show_second_below: float = 0.6, name_width: int = 18, min_dx: float = 24.0):
    xi = typical_xi(occ, team_id, formation)
    pos = _spread_rows({s: slot_xy.get(s, (40, 60)) for s in xi.index}, min_dx=min_dx)
    fig, ax = plt.subplots(figsize=(6.2, 8.4))
    _draw_pitch(ax)

    def _full(pid):
        n = player_names.get(pid)
        if n is not None:
            return str(n)
        return str(int(pid)) if pd.notna(pid) else "?"

    NB = "\u00a0"                      # keeps a share on the same line as the last word
    lowest = 0.0
    for slot, r in xi.iterrows():
        x, y = pos[slot]
        ax.scatter(x, y, s=260, color="#2a78d6", edgecolor=surface, linewidth=2, zorder=3)

        # name + share wrapped together; slots near the touchline get a narrower limit
        limit = min(name_width + 4, int(2 * min(x - 1, 79 - x) / 1.15))
        name_lines = textwrap.wrap(f"{_full(r.player_id)}{NB}{r.share_of_slot:.0%}", limit,
                                   break_on_hyphens=False) or ["?"]
        items = []                     # archetype / second choice, each wrapped on its own
        if archetype_of:
            a = archetype_of.get((r.player_id, r.position_group))
            if a:
                items.append(textwrap.wrap(a, name_width + 6, break_on_hyphens=False))
        if pd.notna(r.second_player_id) and r.share_of_slot < show_second_below:
            items.append(textwrap.wrap(f"+ {_full(r.second_player_id)}{NB}{r.second_share:.0%}",
                                       name_width + 6, break_on_hyphens=False))

        # keep the whole label on the pitch (widths estimated from character counts)
        w = max([0.575 * len(t) for t in name_lines] + [0.46 * len(t) for it in items for t in it])
        lx = min(max(x, 1 + w), 79 - w)

        ax.text(lx, y - 5.2, "\n".join(name_lines), ha="center", va="top", fontsize=7.5, color=ink,
                fontweight="bold", linespacing=1.15, zorder=4)
        y_next = y - 5.2 - (2.0 + 2.3 * (len(name_lines) - 1)) - 1.0
        for lines in items:
            ax.text(lx, y_next, "\n".join(lines), ha="center", va="top", fontsize=6.5, color=ink2,
                    linespacing=1.1, zorder=4)
            y_next -= (1.7 + 1.9 * (len(lines) - 1)) + 1.2
        lowest = min(lowest, y_next)

    f = xi.attrs["formation"]
    ax.set_title(f"{team_names.get(team_id, team_id)} - {formation_text(f)} "
                 f"({xi.attrs['formation_share']:.0%} of minutes)", loc="left", fontsize=11)
    ax.text(0, min(-3.0, lowest - 1.5),
            "Most-used player per slot and her share of that slot's minutes in this formation.",
            va="top", fontsize=7.5, color=muted)
    return fig

def export_all_typical_xi(occ, team_id_to_team, team_id_to_league, player_names, archetype_of=None,
                          team_ids=None, formation=None, fig_dir=player_fig_dir, position="teams",
                          filename="typical_xi.png", dpi=200, **plot_kwargs):
    """Save one typical-XI pitch plot per team to <fig_dir>/<position>/all_k/<Team>_<League>/<filename>.
    team_ids=None -> every team in team_id_to_team. Extra keyword arguments (name_width, min_dx,
    show_second_below) go to plot_typical_xi. Returns the list of saved paths."""
    paths, failed = [], []
    base = os.path.join(fig_dir, position, "all_k")
    for team_id in (team_ids if team_ids is not None else list(team_id_to_team)):
        folder = get_folder_name(team_id, team_id, team_id_to_team, team_id_to_league)
        out_dir = os.path.join(base, folder)
        try:
            fig = plot_typical_xi(occ, team_id, team_id_to_team, player_names, archetype_of,
                                  formation=formation, **plot_kwargs)
        except Exception as e:                                  # one bad team should not stop the other 49
            failed.append((team_id, team_id_to_team[team_id], repr(e)))
            continue
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, filename)
        fig.savefig(path, dpi=dpi, bbox_inches="tight")
        plt.close(fig)                                          # keeps memory flat over 50 figures
        paths.append(path)
    print(f"saved {len(paths)} typical-XI plots to {base}")
    for team_id, team, err in failed:
        print(f"  FAILED {team_id} ({team}): {err}")
    return paths

group_markers = ["o", "s", "^", "v", "P", "X", "h", "<"]
group_colours_list = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
_profile_band = "#f3f2ef"

def _strip(col: str) -> str:
    return re.sub(r"_(z|resid|adj)$", "", col)

# def _label(col: str) -> str:
#     return EXTRA_LABELS.get(_strip(col), label(col))

def _colours(groups, group_colours):
    return group_colours or {g: group_colours_list[i % len(group_colours_list)] for i, g in enumerate(groups)}

def _legend_handles(groups, group_names, colours, counts=None):
    return [Line2D([0], [0], marker=group_markers[i % 3], linestyle="", markersize=8, color=colours[g],
                   markeredgecolor=surface,
                   label=group_names[g] + (f" ({counts[g]})" if counts is not None else ""))
            for i, g in enumerate(groups)]

def _dodge(xs, gap):
    """Keep sorted positions at least `gap` apart by nudging neighbours symmetrically."""
    xs = list(xs)
    for _ in range(50):
        moved = False
        for i in range(1, len(xs)):
            d = xs[i] - xs[i - 1]
            if d < gap - 1e-9:
                xs[i - 1] -= (gap - d) / 2; xs[i] += (gap - d) / 2; moved = True
        if not moved:
            break
    return xs

def group_profile(df, features_by_category, cluster_col, group_colours=None, groups=None, show_n=False,
                  team_id=None, team_name=None, leave_one_out=True,
                  title="How the groups play", row_height=0.5, min_label_gap=0.06,
                  similarity_scores=None, similarity_caption=None, x_limit=None, fmt=".3f"):
    """One row per feature, grouped by category.
    LEFT  (dots): strength-adjusted group mean, comparable across rows. Own group = larger marker with a dark ring;
          the grey bar joins the team to its own group only. Nothing is printed on this side.
    RIGHT (table): the raw group averages in real units, one column per group plus the team, own group outlined.
    features_by_category: {category: [feature, ...]} (names without _adj), e.g. your top_features_by_category_combined.
    groups: full list of clusters, to keep colours/markers tied to the cluster when df is a subset (one league).
    show_n: add the number of teams to each column header.
    team_id: also draw that team (black diamond, bold numbers); with leave_one_out its own group's average is
    computed without it.
    x_limit: half-width of the adjusted axis. Default 2.2 when a team is drawn (so every team uses the same axis),
    otherwise automatic. A point beyond the axis is drawn at its edge with a small arrow.
    fmt: number format of the raw table, e.g. ".3f" (default), ".1f". Shares stored 0-1 are shown as percentages
    with the same format. team_profile passes it through, so team_profile(..., fmt=".1f") works too."""
    all_groups = list(groups) if groups is not None else sorted(df[cluster_col].dropna().unique())
    colours = _colours(all_groups, group_colours or {g: group_colours_list[i % len(group_colours_list)]
                                                     for i, g in enumerate(all_groups)})
    base = df.drop(index=team_id) if (team_id is not None and leave_one_out) else df
    n_of = base[cluster_col].value_counts()
 
    feats = list(dict.fromkeys(f for fs in features_by_category.values() for f in fs))
    raw = base.groupby(cluster_col)[feats].mean().T
    adj = base.groupby(cluster_col)[[f + "_adj" for f in feats]].mean().T
    adj.index = [_strip(i) for i in adj.index]
    groups = [g for g in all_groups if g in raw.columns]
    has_team = team_id is not None
    own = None
    if has_team:
        t_raw = df.loc[team_id, feats].astype(float)
        t_adj = df.loc[team_id, [f + "_adj" for f in feats]].astype(float)
        t_adj.index = [_strip(i) for i in t_adj.index]
        o = df.loc[team_id, cluster_col]
        own = o if (pd.notna(o) and o in groups) else None          # a group with no other team has no column
    cols = groups + (["team"] if has_team else [])
    ncol = len(cols)
    mk = {g: group_markers[all_groups.index(g) % len(group_markers)] for g in groups}
 
    # ---- rows (y runs downward from 0) ----
    y, rows_y, heads = 0.0, [], []
    for cat, fs in features_by_category.items():
        if not fs:
            continue
        heads.append((cat, y)); y -= 0.9
        for f in fs:
            rows_y.append((f, y)); y -= 1.0
    allv = adj.loc[feats, groups].to_numpy(float).ravel()
    if has_team:
        allv = np.concatenate([allv, t_adj.to_numpy(float)])
    lim = float(x_limit) if x_limit else (2.2 if has_team else max(1.2, float(np.nanmax(np.abs(allv))) * 1.15))
    edge = 0.955 * lim                                                  # beyond this a point is pinned to the edge
 
    # ---- size of everything in inches, so the layout does not depend on tight_layout ----
    COL_W, AX_W, GAP, RIGHT = 0.95, 5.2, 0.15, 0.30
    lab_in = 0.35 + 0.062 * max(len(f) for f, _ in rows_y)             # feature names at fontsize 8
    tbl_w = ncol * COL_W
    plot_h = row_height * (0.3 - y)
    has_strip = similarity_scores is not None
    legend_y = 1.75 if has_strip else 0.80                             # legend centre, inches from the top
    top_in, bottom_in = legend_y + 0.95, 1.05
    W, H = lab_in + AX_W + GAP + tbl_w + RIGHT, top_in + plot_h + bottom_in
    fig = plt.figure(figsize=(W, H))
    fig.set_facecolor(surface)
    axL = fig.add_axes([lab_in / W, bottom_in / H, AX_W / W, plot_h / H])
    axR = fig.add_axes([(lab_in + AX_W + GAP) / W, bottom_in / H, tbl_w / W, plot_h / H], sharey=axL)
    for a in (axL, axR):
        a.set_facecolor(surface)
    axL.set_ylim(y + 0.4, 0.7)
    axL.set_xlim(-lim, lim)
    step = 0.5 if lim <= 2.6 else 1.0
    axL.set_xticks(np.arange(-np.floor(lim / step) * step, lim + 1e-9, step))
    axR.set_xlim(0, ncol); axR.axis("off")
    axL.axvline(0, color=axis_colour, linewidth=1)
    axL.grid(axis="x"); axL.set_axisbelow(True)
    for s in ("top", "right", "left"):
        axL.spines[s].set_visible(False)
 
    def place(x):                                                       # (x to draw at, was it pinned?)
        return (float(np.sign(x) * 0.93 * lim), True) if abs(x) > edge else (float(x), False)
 
    # ---- rows: dots on the left, numbers on the right ----
    clipped = False
    for n_row, (f, yy) in enumerate(rows_y):
        v = {g: float(adj.loc[f, g]) for g in groups}
        r = {g: float(raw.loc[f, g]) for g in groups}
        if has_team:
            v["team"], r["team"] = float(t_adj[f]), float(t_raw[f])
        if n_row % 2 == 1:
            for a in (axL, axR):
                a.axhspan(yy - 0.5, yy + 0.5, color=_profile_band, linewidth=0, zorder=0)
        if own is not None and np.isfinite(v[own]) and np.isfinite(v["team"]):
            axL.plot([place(v[own])[0], place(v["team"])[0]], [yy, yy], color=axis_colour, linewidth=3.2, zorder=2,
                     solid_capstyle="round")
        for g in groups:
            if not np.isfinite(v[g]):
                continue
            is_own = (g == own)
            xp, pinned = place(v[g]); clipped |= pinned
            axL.scatter(xp, yy, s=130 if is_own else 80, marker=mk[g], facecolor=colours[g],
                        edgecolor=ink if is_own else surface, linewidth=1.6 if is_own else 1.3,
                        zorder=5 if is_own else 3)
            if pinned:
                axL.scatter(np.sign(v[g]) * 0.985 * lim, yy, s=16, marker=">" if v[g] > 0 else "<",
                            facecolor=colours[g], linewidths=0, zorder=4)
        if has_team and np.isfinite(v["team"]):
            xp, pinned = place(v["team"]); clipped |= pinned
            axL.scatter(xp, yy, s=140, marker="D", facecolor=ink, edgecolor=surface, linewidth=1.5, zorder=6)
            if pinned:
                axL.scatter(np.sign(v["team"]) * 0.985 * lim, yy, s=16, marker=">" if v["team"] > 0 else "<",
                            facecolor=ink, linewidths=0, zorder=4)
        pct = max([abs(x) for x in r.values() if np.isfinite(x)] or [0.0]) <= 1.5   # shares stored 0-1 show as %
        for i, c in enumerate(cols):
            val = r.get(c, np.nan)
            txt = "–" if not np.isfinite(val) else (f"{val * 100:{fmt}}%" if pct else f"{val:{fmt}}")
            bold = (c == own) or (c == "team")
            axR.text(i + 0.5, yy, txt, ha="center", va="center", fontsize=8.5,
                     color=ink if bold else ink2, fontweight="bold" if bold else "normal", zorder=4)
 
    # ---- category headings and separators ----
    for k, (cat, hy) in enumerate(heads):
        if k:
            for a in (axL, axR):
                a.axhline(hy + 0.5, color=axis_colour, linewidth=0.6, alpha=0.5)
        axL.text(0.0, hy, cat.replace("_", " ").capitalize(), transform=axL.get_yaxis_transform(),
                 ha="left", va="center", fontsize=8.5, fontweight="bold", color=ink)
    axL.set_yticks([yy for _, yy in rows_y])
    axL.set_yticklabels([f for f, _ in rows_y], fontsize=8)
    axL.tick_params(axis="y", length=0)
    axL.tick_params(axis="x", labelsize=8.5, colors=muted)
 
    # ---- table header: marker above, name below, centred on the column; own column outlined ----
    tr = blended_transform_factory(axR.transData, axR.transAxes)
    up = lambda inch: 1 + inch / plot_h
    for i, c in enumerate(cols):
        if c == "team":
            nm = textwrap.wrap(team_name or str(team_id), 13)
            lines = nm if len(nm) <= 2 else [nm[0], textwrap.shorten(" ".join(nm[1:]), 13, placeholder="…")]
            axR.plot([i + 0.5], [up(0.50)], marker="D", markersize=8, color=ink, markeredgecolor=surface,
                     linestyle="", transform=tr, clip_on=False)
        else:
            lines = [f"Cluster {int(c)}"] + ([f"n={int(n_of.get(c, 0))}"] if show_n else [])
            axR.plot([i + 0.5], [up(0.50)], marker=mk[c], markersize=8, color=colours[c], markeredgecolor=surface,
                     linestyle="", transform=tr, clip_on=False)
        axR.text(i + 0.5, up(0.08), "\n".join(lines), transform=tr, ha="center", va="bottom", fontsize=8.3,
                 linespacing=1.15, color=ink, fontweight="bold" if (c == own or c == "team") else "normal",
                 clip_on=False)
    if own is not None:
        axR.add_patch(Rectangle((cols.index(own) + 0.04, 0), 0.92, up(0.62), transform=tr, fill=False,
                                edgecolor=ink, linewidth=1.3, clip_on=False, zorder=7))
    cap = ("Raw values in real units; each group's average excludes the team" if has_team and leave_one_out
           else "Raw values in real units")
    axR.text(ncol / 2, -0.22 / plot_h, textwrap.fill(cap, max(18, int(tbl_w / 0.06))), transform=tr, ha="center",
             va="top", fontsize=8, color=muted)
    axL.set_xlabel("Dots: " + ("after allowing for team strength" if has_team else "group average after allowing for strength")
                   + " (0 = average team)", fontsize=8.5, color=ink2, labelpad=6)
    foot = "Positions allow for team strength; numbers are what was recorded, so the same number can sit at different places for different teams."
    if clipped:
        foot += "  Arrow = beyond the axis."
    fig.text(0.15 / W, 0.20 / H, foot, fontsize=7.5, color=muted, ha="left", va="center")
 
    # ---- title, strip, legend ----
    t_title = fig.text(0.15 / W, 1 - 0.15 / H, title, ha="left", va="top", fontsize=15, fontweight="bold", color=ink)
    t_bb = t_title.get_window_extent(fig.canvas.get_renderer())                # a long title shrinks to fit the figure
    t_room = W * fig.dpi - t_bb.x0 - 0.15 * fig.dpi
    if t_bb.width > t_room:
        t_title.set_fontsize(max(10.0, 15 * t_room / t_bb.width))
    if has_strip:
        fig.text(0.15 / W, 1 - 0.52 / H, similarity_caption or "Style similarity to each group (outlined = own group)",
                 ha="left", va="top", fontsize=8, color=ink2)
        _draw_similarity_strip(fig, similarity_scores,
                               highlight_label=f"Cluster {int(own)}" if own is not None else None,
                               rect=(lab_in / W, 1 - (0.72 + 0.9) / H, (AX_W + GAP + tbl_w) / W, 0.9 / H),
                               colors=[colours.get(i, group_colours_list[i % len(group_colours_list)])
                                       for i in range(len(similarity_scores))])
    handles = [Line2D([0], [0], marker=mk[g], linestyle="", markersize=8, color=colours[g], markeredgecolor=surface,
                      label=f"Cluster {int(g)}") for g in groups]
    if has_team:
        handles.append(Line2D([0], [0], marker="D", linestyle="", color=ink, markersize=7, markeredgecolor=surface,
                              label=team_name or str(team_id)))
    fig.legend(handles=handles, loc="center left", bbox_to_anchor=(lab_in / W, 1 - legend_y / H), ncol=len(handles),
               frameon=False, fontsize=8.5)
    return fig

def export_group_profile(df, feature_groups, cluster_col, n_clusters, fig_dir=player_fig_dir, position="teams",
                         filename="group_profile.png", dpi=200, **kwargs):
    """All teams -> <fig_dir>/<position>/k<n>/_groups/group_profile.png. Returns the saved path."""
    fig = group_profile(df, feature_groups, cluster_col, title=f"How the groups play (k = {n_clusters})", **kwargs)
    out_dir = os.path.join(fig_dir, position, f"k{n_clusters}")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, filename)
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    return path


def export_group_profile_by_league(df, feature_groups, cluster_col, n_clusters, fig_dir=player_fig_dir,
                                   position="teams", dpi=200, **kwargs):
    """One plot per league -> <...>/k<n>/_groups/group_profile_<League>.png. Returns the paths."""
    groups = sorted(df[cluster_col].dropna().unique())
    out_dir = os.path.join(fig_dir, position, f"k{n_clusters}")
    os.makedirs(out_dir, exist_ok=True)
    paths = []
    for league in sorted(df["league"].dropna().unique()):
        fig = group_profile(df[df["league"] == league], feature_groups, cluster_col, groups=groups, show_n=True,
                            title=f"How the groups play, {league} (k = {n_clusters})", **kwargs)
        slug = str(league).replace("/", "-").replace(" ", "_").replace("'", "")
        path = os.path.join(out_dir, f"group_profile_{slug}.png")
        fig.savefig(path, dpi=dpi, bbox_inches="tight")
        plt.close(fig)
        paths.append(path)
    return paths

def team_profile(df, team_id, features_by_category, cluster_col, names=None, k=None, league_only=False,
                 leave_one_out=True, similarity=True, **kwargs):
    """One team against every group's mean (same layout as group_profile) with a similarity strip on top:
    the team's share of similarity to every group (shares add to 100%, its own group is outlined).
    names: {team_id: name}.
    league_only: the group means (dots and numbers) use only the teams of the team's own league (needs a 'league'
    column); a group with no other team in that league is left out. False = all teams.
    The strip is read from the same columns as plot_team_vs_cluster, sim_cluster_<i>_k<k> (k = the k argument, or
    the number of groups when k is None), each team's values divided by their sum. So it shows the same numbers
    as your radar charts, and it is the same in the all-teams and league_only versions. No strip when those
    columns are not in df. similarity=False = no strip."""
    name = str(names.get(team_id, team_id)) if names is not None else str(team_id)
    league = df.loc[team_id, "league"] if league_only else None
    ref = df[df["league"] == league] if league_only else df
    all_groups = sorted(df[cluster_col].dropna().unique())
    kwargs.setdefault("groups", all_groups)
    if league_only:
        kwargs.setdefault("show_n", True)
    title = (f"{name} against the group averages" + (f" (k = {k})" if k else "")
             + (f", {league} teams only" if league_only else ""))
 
    scores = None
    if similarity:                                      # strip from your sim_cluster_<i>_k<k> columns
        n_k = int(k) if k else len(all_groups)
        sim_cols = [f"sim_cluster_{i}_k{n_k}" for i in range(n_k)]
        if all(c in df.columns for c in sim_cols):
            sims = df.loc[team_id, sim_cols].astype(float)
            if np.isfinite(sims.to_numpy()).all() and sims.sum() > 0:
                scores = {f"Cluster {i}": float(v / sims.sum()) for i, v in enumerate(sims)}
    return group_profile(ref, features_by_category, cluster_col, team_id=team_id, team_name=name,
                         leave_one_out=leave_one_out, title=title, similarity_scores=scores,
                         similarity_caption=("Style similarity to each group (outlined = own group"
                                             + ("; not league-specific)" if league_only else ")")),
                         **kwargs)

def team_profile_vs_league(df, team_id, features_by_category, cluster_col, names=None, k=None, **kwargs):
    """team_profile restricted to the teams of the team's own league: the same plot, but every group's mean (dots
    and numbers) is taken over that league's teams only. Same as team_profile(..., league_only=True), so
    leave_one_out, similarity and the other options work as there."""
    return team_profile(df, team_id, features_by_category, cluster_col, names, k, league_only=True, **kwargs)

def export_team_profiles(df, feature_groups, cluster_col, n_clusters, team_id_to_team, team_id_to_league,
                         team_ids=None, fig_dir=player_fig_dir, position="teams", filename=None,
                         dpi=200, **kwargs):
    """One plot per team -> <fig_dir>/<position>/k<n>/<Team>_<League>/team_profile.png, or team_profile_league.png
    when league_only=True is passed. Returns the paths."""
    if filename is None:
        filename = "team_profile_league.png" if kwargs.get("league_only") else "team_profile.png"
    paths = []
    for team_id in (team_ids if team_ids is not None else list(team_id_to_team)):
        fig = team_profile(df, team_id, feature_groups, cluster_col, team_id_to_team, k=n_clusters, **kwargs)
        out_dir = os.path.join(fig_dir, position, f"k{n_clusters}",
                               get_folder_name(team_id, team_id, team_id_to_team, team_id_to_league))
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, filename)
        fig.savefig(path, dpi=dpi, bbox_inches="tight")
        plt.close(fig)
        paths.append(path)
    print(f"saved {len(paths)} team profiles (k = {n_clusters}) to "
          f"{os.path.abspath(os.path.join(fig_dir, position, f'k{n_clusters}'))}")
    return paths

def export_team_profiles_vs_league(df, feature_groups, cluster_col, n_clusters, team_id_to_team, team_id_to_league,
                                   team_ids=None, fig_dir=player_fig_dir, position="teams",
                                   filename="team_profile_vs_league.png", dpi=200, **kwargs):
    """export_team_profiles for the league-restricted plots -> <...>/k<n>/<Team>_<League>/team_profile_league.png.
    Same as export_team_profiles(..., league_only=True)."""
    return export_team_profiles(df, feature_groups, cluster_col, n_clusters, team_id_to_team, team_id_to_league,
                                league_only=True, **kwargs)

blues = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#104281"]

_entry_word = {"pass": "passes", "carry": "carries"}

def _as_entries(entry):
    """'pass' -> ('pass',); ('pass', 'carry') stays. At most two types: the first is drawn solid, the second outlined."""
    e = (entry,) if isinstance(entry, str) else tuple(entry)
    if not 1 <= len(e) <= 2:
        raise ValueError(f"entry/entries must name one or two types, got {entry!r}")
    return e
 
def _entry_words(entries):                       # "passes and carries"
    return " and ".join(_entry_word.get(e, e) for e in entries)
 
def _entry_tag(entries):                         # file-name part: '' for the combined plot, '_pass' for one type
    return "" if len(entries) > 1 else f"_{entries[0]}"
 
def _arrow_key(entries):
    if len(entries) == 1:
        return f"Arrows: share of final-third entries by {_entry_words(entries)}"
    a, b = (_entry_word.get(e, e) for e in entries)
    return f"Arrows: share of final-third entries (solid = {a}, outlined = {b})"

entry_weight_col = "pass_into_final_third_share_per_game"
_sides = ("left", "central", "right")
_entry_cols = [f"final_third_entry_{s}_per_game_pct" for s in _sides]
_kind_words = {"both": "passes and carries combined", "pass": "passes", "carry": "carries"}


pitch_cols = ["final_third_touch_left_per_game_pct", "final_third_touch_central_per_game_pct",
              "final_third_touch_right_per_game_pct", "defensive_actions_x_avg", "defensive_actions_y_std",
              "counterpress_actions_applied_opposing_half_pct", "pressures_applied_opposing_half_pct"] + \
             [f"{e}_into_final_third_{s}_per_game_pct" for e in ("pass", "carry") for s in ("left", "central", "right")]

def _entry_kind(entry):
    """('pass', 'carry') in any order, or 'both' -> 'both'; 'pass' / ('pass',) -> 'pass'; 'carry' -> 'carry'."""
    e = {entry} if isinstance(entry, str) else set(entry)
    if e in ({"both"}, {"all"}, {"pass", "carry"}):
        return "both"
    if e in ({"pass"}, {"carry"}):
        return next(iter(e))
    raise ValueError(f"entry/entries must be 'pass', 'carry' or both ('pass', 'carry'); got {entry!r}")
 
def _entry_tag(kind):                            # file-name part: '' for the combined plot
    return "" if kind == "both" else f"_{kind}"
 
def _arrow_key(kind):
    return ("Arrows: share of final-third entries, passes and carries combined" if kind == "both"
            else f"Arrows: share of final-third entries by {_kind_words[kind]}")
 
def _with_entry_cols(team_wide, kind):
    """team_wide plus the three combined-entry columns (only when kind == 'both')."""
    if kind != "both":
        return team_wide
    need = [entry_weight_col] + [f"{t}_into_final_third_{s}_per_game_pct" for t in ("pass", "carry") for s in _sides]
    missing = [c for c in need if c not in team_wide.columns]
    if missing:
        raise KeyError(f"cannot combine passes and carries: missing {missing}. For one type use entry='pass' / 'carry'.")
    w = team_wide[entry_weight_col].astype(float)
    if (w.dropna() < 0).any() or (w.dropna() > 1).any() or w.median() < 0.4:
        warnings.warn(f"{entry_weight_col}: median {w.median():.2f}, range {w.min():.2f}-{w.max():.2f}. It should be the share "
                      "of final-third entries made by pass (about 0.5-0.9). If it is a rate, the combined arrows are wrong: "
                      "change ENTRY_WEIGHT_COL.")
    out = team_wide.copy()
    for s, name in zip(_sides, _entry_cols):
        out[name] = w * team_wide[f"pass_into_final_third_{s}_per_game_pct"] \
            + (1 - w) * team_wide[f"carry_into_final_third_{s}_per_game_pct"]
    return out
 
def _pitch_columns(team_wide):
    return [c for c in list(pitch_cols) + _entry_cols if c in team_wide.columns]

def _pitch_profile(ax, v: pd.Series, title: str, entry=("pass", "carry"), colour: str = "#2a78d6"):
    """Draws one profile from a Series of RAW values (team or group average).
    entry: ('pass', 'carry') = one arrow per channel for all final-third entries (needs the combined columns added by
    _with_entry_cols); 'pass' or 'carry' = that type only."""
    kind = _entry_kind(entry)
    _draw_pitch(ax)
    zones = [("left", 0.0), ("central", 80 / 3), ("right", 160 / 3)]
    for side, x0 in zones:
        t = float(v.get(f"final_third_touch_{side}_per_game_pct", np.nan))
        if np.isfinite(t):
            shade = blues[min(len(blues) - 1, int(np.clip((t - 0.15) / 0.30, 0, 0.999) * len(blues)))]
            ax.add_patch(Rectangle((x0, 80), 80 / 3, 40, facecolor=shade, edgecolor=surface, linewidth=1.5,
                                   alpha=0.55, zorder=1))
            ax.text(x0 + 40 / 3, 114, f"touches\n{t:.0%}", ha="center", va="top", fontsize=7, color=ink, zorder=3)
    for side, xc in [("left", 40 / 3), ("central", 40), ("right", 200 / 3)]:
        col = f"final_third_entry_{side}_per_game_pct" if kind == "both" else f"{kind}_into_final_third_{side}_per_game_pct"
        s = float(v.get(col, np.nan))
        if np.isfinite(s):
            ax.add_patch(FancyArrow(xc, 62, 0, 18, width=max(1.0, s * 18), head_width=max(3.0, s * 26),
                                    head_length=5, length_includes_head=True, color=colour, alpha=0.9, zorder=4))
            ax.text(xc, 90, f"{s:.0%}", ha="center", va="center", fontsize=9, fontweight="bold", color=ink, zorder=5)
    h = float(v.get("defensive_actions_x_avg", np.nan))
    sd = float(v.get("defensive_actions_y_std", np.nan))
    if np.isfinite(h):
        half = sd if np.isfinite(sd) else 25
        ax.plot([40 - half, 40 + half], [h, h], color="#e34948", linewidth=3, solid_capstyle="round", zorder=4)
        ax.text(40, h - 3, f"avg defensive action {h:.1f} yds from own goal", ha="center", va="top",
                fontsize=7, color=ink2, zorder=5)
    lines = []
    for c, txt in [("counterpress_actions_applied_opposing_half_pct", "Counterpressing in opp. half"),
                   ("pressures_applied_opposing_half_pct", "Pressing in opp. half")]:
        if c in v.index and pd.notna(v[c]):
            lines.append(f"{txt}: {v[c]:.0%}")
    if lines:
        ax.text(2, 2, "\n".join(lines), fontsize=7, color=ink2, va="bottom", ha="left", zorder=5)
    ax.set_title(title, loc="left", fontsize=10)

def pitch_profiles_by_group(team_wide, cluster_col, entry=("pass", "carry"), include_all=True, group_colours=None,
                            league=None):
    """One pitch per group (plus 'All teams'): raw group averages. entry: ('pass', 'carry') = all final-third entries
    (default), or 'pass' / 'carry' alone.
    league: only the teams of that league (a group the league has no team in is left out; the colours stay tied to
    the cluster)."""
    kind = _entry_kind(entry)
    team_wide = _with_entry_cols(team_wide, kind)
    all_groups = sorted(team_wide[cluster_col].dropna().unique())
    df = team_wide[team_wide["league"] == league] if league is not None else team_wide
    groups = [g for g in all_groups if (df[cluster_col] == g).any()]
    gnames = {g: f"Cluster {int(g)}" for g in groups}
    colours = group_colours or {g: slots[i] for i, g in enumerate(all_groups)}
    cols = _pitch_columns(team_wide)
    panels = []
    for g in groups:
        ids = df.index[df[cluster_col] == g]
        panels.append((f"{gnames[g]} ({len(ids)} team{'' if len(ids) == 1 else 's'})",
                       df.loc[ids, cols].mean(), colours[g]))
    if include_all:
        panels.append((f"All {league} teams ({len(df)})" if league is not None else f"All teams ({len(df)})",
                       df[cols].mean(), muted))
    fig, axes = plt.subplots(1, len(panels), figsize=(3.6 * len(panels), 6.4))
    for ax, (t, v, c) in zip(np.atleast_1d(axes), panels):
        _pitch_profile(ax, v, t, kind, c)
    fig.suptitle((f"{league}: " if league is not None else "") +
                 f"Where attacks enter the final third ({_kind_words[kind]}), where the ball is touched "
                 "there, and how high they defend", x=0.01, ha="left", fontweight="bold", fontsize=10.5)
    fig.tight_layout()
    return fig

def pitch_profile_team(team_wide, team_id, names, entry=("pass", "carry")):
    """One team on its own (no group involved): channels of attack, final-third touches, defensive height."""
    kind = _entry_kind(entry)
    team_wide = _with_entry_cols(team_wide, kind)
    cols = _pitch_columns(team_wide)
    TITLE_H = 0.92                                                   # inches for the title block above the pitch
    H = 6.6 + TITLE_H
    fig, ax = plt.subplots(figsize=(4.2, H))
    team_name = str(names.get(team_id, team_id))
    _pitch_profile(ax, team_wide.loc[team_id, cols], team_name, kind, ink)
    fig.text(0.01, 0.005, _arrow_key(kind) + "; shaded: share of final-third touches; "
             "red line: height and width spread of defensive actions.", color=muted, fontsize=6.3, wrap=True)
    fig.tight_layout(rect=(0, 0.26 / H, 1, 1 - TITLE_H / H))
    x0 = ax.get_position().x0
    fig.text(x0, 1 - 0.12 / H, f"{team_name}: pitch profile", ha="left", va="top", fontsize=10.5, fontweight="bold",
             color=ink)
    fig.text(x0, 1 - 0.40 / H, f"Where attacks enter the final third ({_kind_words[kind]}),\ntouches there, and how high they defend",
             ha="left", va="top", fontsize=8, color=ink2, linespacing=1.4)
    return fig

def pitch_profile_team_vs_group(team_wide, team_id, names, cluster_col, entry=("pass", "carry"), leave_one_out=True,
                                group_colours=None, league_only=False, k=None, similarity=True):
    """The team's pitch profile next to its own group's average (team left out of the average), with a similarity strip on
    top: the team's share of similarity to every group (shares add to 100%, its own group is outlined), read from the
    sim_cluster_<i>_k<k> columns (k = the k argument, or the number of groups when k is None), each team's values divided
    by their sum, so it shows the same numbers as your radar charts and team_profile. No strip when those columns are not
    in team_wide; similarity=False = no strip.
    league_only: the average is over the teams of that group in the team's own league (the strip is not league-specific).
    Returns None when no other team of the group is left to average (the team is alone in its group, or in its group
    within the league)."""
    kind = _entry_kind(entry)
    team_wide = _with_entry_cols(team_wide, kind)
    groups = sorted(team_wide[cluster_col].dropna().unique())
    gnames = {g: f"Cluster {int(g)}" for g in groups}
    colours = group_colours or {g: slots[i] for i, g in enumerate(groups)}
    cols = _pitch_columns(team_wide)
    g = team_wide.loc[team_id, cluster_col]
    if pd.isna(g):
        return None
    league = team_wide.loc[team_id, "league"] if league_only else None
    ids = team_wide.index[team_wide[cluster_col] == g]
    if league_only:
        ids = ids[(team_wide.loc[ids, "league"] == league).to_numpy()]
    if leave_one_out:
        ids = ids.drop(team_id, errors="ignore")
    if len(ids) == 0:
        return None
    avg_title = f"{gnames[g]} average" + (f", {league}" if league_only else "")
    avg_count = (f"{len(ids)} other team{'' if len(ids) == 1 else 's'}" if leave_one_out
                 else f"{len(ids)} team{'' if len(ids) == 1 else 's'}")
    scores = None
    if similarity:                                                   # strip from your sim_cluster_<i>_k<k> columns
        n_k = int(k) if k else len(groups)
        sim_cols = [f"sim_cluster_{i}_k{n_k}" for i in range(n_k)]
        if all(c in team_wide.columns for c in sim_cols):
            sim_v = team_wide.loc[team_id, sim_cols].astype(float)
            if np.isfinite(sim_v.to_numpy()).all() and sim_v.sum() > 0:
                scores = {f"Cluster {i}": float(v / sim_v.sum()) for i, v in enumerate(sim_v)}
    TITLE_H = 0.62                                                   # inches for the title block above the pitches
    band = TITLE_H + (1.30 if scores is not None else 0.0)           # + the strip, if there is one
    H = 6.4 + band
    fig, axes = plt.subplots(1, 2, figsize=(7.4, H))
    team_name = str(names.get(team_id, team_id))
    _pitch_profile(axes[0], team_wide.loc[team_id, cols], team_name, kind, ink)
    _pitch_profile(axes[1], team_wide.loc[ids, cols].mean(),
                   f"{avg_title}\n({avg_count})" if league_only else
                   (f"{avg_title} ({avg_count})" if leave_one_out else avg_title),
                   kind, colours[g])
    if kind == "both":
        fig.text(0.01, 0.005, _arrow_key(kind), color=muted, fontsize=7.5)
    fig.tight_layout(rect=(0, 0.03 if kind == "both" else 0, 1, 1 - band / H))
    x0, x1 = axes[0].get_position().x0, axes[1].get_position().x1
    fig.text(x0, 1 - 0.12 / H, f"{team_name} against the {gnames[g]} average" + (f", {league} teams only" if league_only else ""),
             ha="left", va="top", fontsize=10.5, fontweight="bold", color=ink)
    fig.text(x0, 1 - 0.40 / H, f"Where attacks enter the final third ({_kind_words[kind]}), touches there, and how high they defend",
             ha="left", va="top", fontsize=8, color=ink2)
    if scores is not None:                                           # strip across the width of the two pitches
        fig.text(x0, 1 - (TITLE_H + 0.10) / H, "Style similarity to each group (outlined = own group"
                 + ("; not league-specific)" if league_only else ")"), ha="left", va="top", fontsize=8, color=ink2)
        _draw_similarity_strip(fig, scores, highlight_label=f"Cluster {int(g)}",
                               rect=(x0, 1 - (TITLE_H + 0.40 + 0.90) / H, x1 - x0, 0.90 / H),
                               colors=[colours.get(i, slots[i % len(slots)]) for i in range(len(scores))])
    return fig

def export_pitch_profiles_by_group(team_wide, cluster_col, n_clusters, entries=("pass", "carry"),
                                   fig_dir=player_fig_dir, position="teams", dpi=200, **kwargs):
    """-> <...>/k<n>/pitch_profiles.png (all final-third entries on each pitch), or pitch_profiles_<entry>.png when
    entries is a single type. Returns the paths."""
    kind = _entry_kind(entries)
    out_dir = os.path.join(fig_dir, position, f"k{n_clusters}")
    os.makedirs(out_dir, exist_ok=True)
    fig = pitch_profiles_by_group(team_wide, cluster_col, kind, **kwargs)
    path = os.path.join(out_dir, "pitch_profiles.png")
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    return [path]

def export_pitch_profiles_by_group_by_league(team_wide, cluster_col, n_clusters, entries=("pass", "carry"),
                                             fig_dir=player_fig_dir, position="teams", dpi=200, **kwargs):
    """One plot per league -> <...>/k<n>/pitch_profiles_<League>.png (or pitch_profiles_<entry>_<League>.png when
    entries is a single type). Returns the paths."""
    entries = _as_entries(entries)
    out_dir = os.path.join(fig_dir, position, f"k{n_clusters}")
    os.makedirs(out_dir, exist_ok=True)
    paths = []
    for league in sorted(team_wide["league"].dropna().unique()):
        slug = str(league).replace("/", "-").replace(" ", "_").replace("'", "")
        fig = pitch_profiles_by_group(team_wide, cluster_col, entries, league=league, **kwargs)
        path = os.path.join(out_dir, f"pitch_profiles_{slug}.png")
        fig.savefig(path, dpi=dpi, bbox_inches="tight")
        plt.close(fig)
        paths.append(path)
    return paths

def export_pitch_profile_teams(team_wide, team_id_to_team, team_id_to_league, entries=("pass", "carry"),
                               team_ids=None, fig_dir=player_fig_dir, position="teams", dpi=200):
    """One plot per team -> <...>/all_k/<Team>_<League>/pitch_profile.png (or pitch_profile_<entry>.png when
    entries is a single type)."""
    entries = _as_entries(entries)
    paths = []
    for team_id in (team_ids if team_ids is not None else list(team_id_to_team)):
        fig = pitch_profile_team(team_wide, team_id, team_id_to_team, entries)
        out_dir = os.path.join(fig_dir, position, "all_k",
                               get_folder_name(team_id, team_id, team_id_to_team, team_id_to_league))
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, "pitch_profile.png")
        fig.savefig(path, dpi=dpi, bbox_inches="tight")
        plt.close(fig)
        paths.append(path)
    print(f"saved team pitch profiles ({_entry_words(entries)}) to "
          f"{os.path.abspath(os.path.join(fig_dir, position, 'all_k'))}")
    return paths

def export_pitch_profile_teams_vs_group(team_wide, cluster_col, n_clusters, team_id_to_team, team_id_to_league,
                                        entries=("pass", "carry"), team_ids=None, fig_dir=player_fig_dir,
                                        position="teams", dpi=200, **kwargs):
    """-> <...>/k<n>/<Team>_<League>/pitch_profile_vs_group.png, or pitch_profile_vs_group_league.png when
    league_only=True is passed (a single type adds _<entry>: pitch_profile_vs_group_<entry>[_league].png).
    Teams with nothing to compare against are skipped and listed."""
    entries = _as_entries(entries)
    suffix = "_league" if kwargs.get("league_only") else ""
    paths, skipped = [], []
    for team_id in (team_ids if team_ids is not None else list(team_id_to_team)):
        fig = pitch_profile_team_vs_group(team_wide, team_id, team_id_to_team, cluster_col, entries, **kwargs)
        if fig is None:
            skipped.append(str(team_id_to_team.get(team_id, team_id)))
            continue
        out_dir = os.path.join(fig_dir, position, f"k{n_clusters}",
                               get_folder_name(team_id, team_id, team_id_to_team, team_id_to_league))
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, f"pitch_profile_vs_group{suffix}.png")
        fig.savefig(path, dpi=dpi, bbox_inches="tight")
        plt.close(fig)
        paths.append(path)
    print(f"saved team-vs-group pitch profiles ({_entry_words(entries)}, k = {n_clusters}) to "
          f"{os.path.abspath(os.path.join(fig_dir, position, f'k{n_clusters}'))}")
    if skipped:
        print(f"skipped (no other team of the group to compare against): {', '.join(dict.fromkeys(skipped))}")
    return paths

# ============================================================================================= #
# 5. Formations per team
# ============================================================================================= #
def formation_profile_team(occ, team_id, names, fm=None, min_share=0.02,
                           back_3_share=None, wingerless_share=None):
    """One team as doughnuts: the share of its minutes in each formation (legend with the minutes, if
    formation_minutes has a minutes column), then one doughnut for the back-three share and one for the
    wingerless share, taken from your ready-made tables (index team_id, one column each, or a Series).
    A table left as None, or a team missing from it, leaves that doughnut out; the one exception is the
    back-three doughnut, which is worked out from the formations (those starting 3 or 5) when no value is supplied.
    fm = formation_minutes(occ), pass it in to avoid recomputing for every team."""
    fm = formation_minutes(occ) if fm is None else fm
    t = fm[fm["team_id"] == team_id].copy()
    if t.empty:
        raise ValueError(f"no formation minutes for team {team_id}")
    t["label"] = [formation_text(c) for c in t["formation"]]
    mcol = next((c for c in ("minutes", "mins", "minutes_played") if c in t.columns), None)
    t = t.groupby("label").agg({"share": "sum", **({mcol: "sum"} if mcol else {})}).sort_values("share",
                                                                                              ascending=False)
    shown = t[t["share"] >= min_share]
    rest = t[t["share"] < min_share]
    rows = [(f, float(r["share"]), float(r[mcol]) if mcol else None) for f, r in shown.iterrows()]
    if len(rest):
        rows.append((f"Other ({len(rest)})", float(rest["share"].sum()), float(rest[mcol].sum()) if mcol else None))
    n_main = len(rows) - (1 if len(rest) else 0)
    slice_colours = [matplotlib.colors.to_rgba(slots[0], 1.0 - 0.65 * i / max(n_main - 1, 1)) for i in range(n_main)]
    if len(rest):
        slice_colours.append("#d9d9d9")

    b3_s = back_3_share.iloc[:, 0] if isinstance(back_3_share, pd.DataFrame) else back_3_share
    nw_s = wingerless_share.iloc[:, 0] if isinstance(wingerless_share, pd.DataFrame) else wingerless_share
    b3_given = b3_s is not None and team_id in b3_s.index and pd.notna(b3_s.loc[team_id])
    nw_given = nw_s is not None and team_id in nw_s.index and pd.notna(nw_s.loc[team_id])
    if b3_given:
        binary = [("Back three", float(b3_s.loc[team_id]), slots[1])]
    else:
        binary = [("Back three", float(t[[f[0] in "35" for f in t.index]]["share"].sum()), slots[1])]
    if nw_given:
        binary.append(("No wingers", float(nw_s.loc[team_id]), slots[2]))

    n_bin = len(binary)
    fig = plt.figure(figsize=(4.0 + 1.9 + 2.4 * n_bin, 3.9 + 0.12 * max(0, len(rows) - 5)))
    gs = fig.add_gridspec(1, 2 + n_bin, width_ratios=[1.15, 1.0] + [0.85] * n_bin, wspace=0.12)
    ax = fig.add_subplot(gs[0])                                          # formations doughnut
    wedges, _ = ax.pie([r[1] for r in rows], colors=slice_colours, startangle=90, counterclock=False,
                       wedgeprops=dict(width=0.38, edgecolor=surface, linewidth=1.5))
    ax.text(0, 0.07, rows[0][0], ha="center", va="center", fontsize=13, fontweight="bold", color=ink)
    ax.text(0, -0.2, f"{rows[0][1]:.0%} of minutes", ha="center", va="center", fontsize=7.5, color=muted)
    ax.set_title("Formations", fontsize=9.5, color=ink2)
    axl = fig.add_subplot(gs[1]); axl.axis("off")                        # legend: formation, share, minutes
    axl.legend(wedges, [f"{lab}   {s:.0%}" + (f"  ·  {m:,.0f} min" if m is not None else "") for lab, s, m in rows],
               loc="center left", fontsize=8.5, frameon=False, handlelength=1.2, borderaxespad=0)
    for j, (lab, v, c) in enumerate(binary):
        axb = fig.add_subplot(gs[2 + j])
        axb.pie([max(v, 0), max(1 - v, 0)], colors=[c, "#e3e3df"], startangle=90, counterclock=False,
                wedgeprops=dict(width=0.38, edgecolor=surface, linewidth=1.5))
        axb.text(0, 0.07, f"{v:.0%}", ha="center", va="center", fontsize=15, fontweight="bold", color=ink)
        axb.text(0, -0.2, "of minutes", ha="center", va="center", fontsize=7.5, color=muted)
        axb.set_title(lab, fontsize=9.5, color=ink2)
    fig.suptitle(f"{names.get(team_id, team_id)}: formations used", x=0.01, y=0.98, ha="left",
                 fontsize=plt.rcParams["axes.titlesize"])
    if not b3_given:                                                     # only the worked-out back-three doughnut needs explaining
        fig.text(0.01, 0.01, "Back three: formations with three or five at the back.", color=muted, fontsize=6.8)
    return fig

def export_formation_profiles(occ, team_id_to_team, team_id_to_league, team_ids=None, fig_dir=player_fig_dir,
                              position="teams", filename="formations.png", dpi=200,
                              back_3_share=None, wingerless_share=None, **kwargs):
    """One plot per team -> <...>/all_k/<Team>_<League>/formations.png.
    back_3_share / wingerless_share: your tables (index team_id, one column each); they have to be passed in, a
    function in this file cannot see the variables of your notebook."""
    fm = formation_minutes(occ)
    paths = []
    for team_id in (team_ids if team_ids is not None else list(team_id_to_team)):
        fig = formation_profile_team(occ, team_id, team_id_to_team, fm=fm, back_3_share=back_3_share,
                                     wingerless_share=wingerless_share, **kwargs)
        out_dir = os.path.join(fig_dir, position, "all_k",
                               get_folder_name(team_id, team_id, team_id_to_team, team_id_to_league))
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, filename)
        fig.savefig(path, dpi=dpi, bbox_inches="tight")
        plt.close(fig)
        paths.append(path)
    print(f"saved {len(paths)} formation profiles to {os.path.abspath(os.path.join(fig_dir, position, 'all_k'))}")
    return paths

# ============================================================================================= #
# 4. Strength and dominance strips
# ============================================================================================= #
def group_strips(team_wide, cluster_col, cols, names=None, label_ids=None, col_labels=None, col_formats=None,
                 group_colours=None, seed=0, title=None, league=None):
    """One panel per measure in cols; every team is a dot in its group's column (small random sideways jitter so
    dots do not stack), the black line is the group median. Heavily overlapping columns = the groups do not differ
    on that measure. label_ids: team ids to name on the plot; col_labels: {col: panel title};
    col_formats: {col: 'pct' | 'num'}.
    league: only the teams of that league (a group the league has no team in is left out; colour and marker stay
    tied to the cluster)."""
    all_groups = sorted(team_wide[cluster_col].dropna().unique())
    df = team_wide[team_wide["league"] == league] if league is not None else team_wide
    groups = [g for g in all_groups if (df[cluster_col] == g).any()]
    gnames = {g: f"Cluster {int(g)}" for g in groups}
    cmap = group_colours or {g: slots[i] for i, g in enumerate(all_groups)}
    mark = {g: group_markers[i % 3] for i, g in enumerate(all_groups)}
    if title is None:
        title = ("Strength and dominance by group" + (f", {league}" if league is not None else "")
                 + " (line = group median)")
    rng = np.random.default_rng(seed)
    fig, axes = plt.subplots(1, len(cols), figsize=(3.2 * len(cols), 4.6), squeeze=False)
    for ax, c in zip(axes[0], cols):
        for i, g in enumerate(groups):
            ids = list(df.index[df[cluster_col] == g])
            v = df.loc[ids, c].astype(float)
            xj = i + rng.uniform(-0.18, 0.18, len(v))
            ax.scatter(xj, v, s=26, marker=mark[g], color=cmap[g], edgecolor=surface, linewidth=1,
                       zorder=3)
            ax.hlines(v.median(), i - 0.3, i + 0.3, color=ink, linewidth=2, zorder=4)
            for t, xx, yy in zip(ids, xj, v):
                if label_ids and t in label_ids and names is not None:
                    ax.annotate(names.get(t, t), (xx, yy), xytext=(4, 2), textcoords="offset points",
                                fontsize=6.5, color=ink2)
        ax.set_xticks(range(len(groups)),
                      [f"{gnames[g]}\n({int((df[cluster_col] == g).sum())})" for g in groups], fontsize=7.5)
        ax.grid(axis="y"); ax.set_axisbelow(True)
        ax.set_title((col_labels or {}).get(c, str(c).replace("_", " ")), loc="left", fontsize=9.5)
        if (col_formats or {}).get(c) == "pct":
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}"))
    fig.suptitle(title, x=0.01, ha="left", fontweight="bold")
    fig.tight_layout()
    return fig

def export_group_strips(team_wide, cluster_col, n_clusters, cols, fig_dir=player_fig_dir, position="teams",
                        filename="strength_dominance_strips.png", dpi=200, **kwargs):
    """-> <...>/k<n>/_groups/strength_dominance_strips.png."""
    fig = group_strips(team_wide, cluster_col, cols,
                       title=f"Strength and dominance by group (k = {n_clusters}; line = group median)", **kwargs)
    out_dir = os.path.join(fig_dir, position, f"k{n_clusters}")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, filename)
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    return path

def export_group_strips_by_league(team_wide, cluster_col, n_clusters, cols, fig_dir=player_fig_dir, position="teams",
                                  dpi=200, **kwargs):
    """One plot per league -> <...>/k<n>/_groups/strength_dominance_strips_<League>.png. Returns the paths."""
    out_dir = os.path.join(fig_dir, position, f"k{n_clusters}")
    os.makedirs(out_dir, exist_ok=True)
    paths = []
    for league in sorted(team_wide["league"].dropna().unique()):
        fig = group_strips(team_wide, cluster_col, cols, league=league,
                           title=f"Strength and dominance by group, {league} (k = {n_clusters}; line = group median)",
                           **kwargs)
        slug = str(league).replace("/", "-").replace(" ", "_").replace("'", "")
        path = os.path.join(out_dir, f"strength_dominance_strips_{slug}.png")
        fig.savefig(path, dpi=dpi, bbox_inches="tight")
        plt.close(fig)
        paths.append(path)
    return paths

# ============================================================================================= #
# 3. Player-type shares (soft shares: columns named '<Position>__soft_*' in ARCHETYPES)
# ============================================================================================= #
def team_type_mix(team_wide, team_id, names, positions=None, share_cols=None, type_cols=None, sub_types=True):
    """One team on its own: for each position a 100% bar of the team's minutes split by player type (soft shares).
    sub_types: for a position with sub-types (columns '<Position>__soft_<parent>_<child>') two more bars follow the
    soft one: the hard parent shares (columns '<Position>__<parent>', each player counted wholly in one type) and
    all the sub-types in one bar, in the same order. The sub-types are a soft split inside each hard parent, so
    each parent's sub-types add up to its hard share and line up under it; each sub-type has its parent's colour,
    lighter for later children.
    type_cols: the soft-share columns to use (default: every '<Position>__soft_<n>' and '<Position>__soft_<n>_<m>'
    column in team_wide)."""
    def suf(c):   # "Center Back__soft_3" -> "3"; "Center Back__soft_1_2" -> "1_2"; hard "Center Back__3" -> "3"
        s = str(c).split("__")[-1]
        return s[5:] if s.startswith("soft_") else s
    def lab(c):   # "Type 3"; a sub-type "Type 1.2"; a text suffix is shown as it is
        s = suf(c)
        return "Type " + s.replace("_", ".") if s.replace("_", "").isdigit() else s.replace("_", " ")
    def kid(c):   # is it a sub-type column ("<parent>_<child>")?
        return "_" in suf(c) and suf(c).replace("_", "").isdigit()
    def colr(c, j):   # a type: its slot colour; a sub-type: its parent's colour, lighter for later children
        if not kid(c):
            return slots[j]
        a, b = (int(t) for t in suf(c).split("_")[:2])
        return tuple(x + (1 - x) * (0.0, 0.3, 0.55, 0.7)[min(b, 3)]
                     for x in plt.matplotlib.colors.to_rgb(slots[a % len(slots)]))
    pool = list(type_cols) if type_cols is not None else [
        c for c in team_wide.columns if "__soft_" in c and c.split("__soft_")[-1].replace("_", "").isdigit()]
    if not pool:
        raise ValueError("no '<Position>__soft_<number>' columns in team_wide; pass type_cols=[...]")
    pos = list(positions) if positions else list(dict.fromkeys(c.split("__soft_")[0] for c in pool))
    views = []   # (label, columns, kind): kind is "soft", "hard" or "sub"
    for p in pos:
        mine = [c for c in pool if c.startswith(p + "__soft_")]
        top = list(share_cols) if share_cols else [c for c in mine if not kid(c)]
        subs = sorted([c for c in mine if kid(c)], key=lambda c: [int(t) for t in suf(c).split("_")])
        has_sub = sub_types and not share_cols and bool(subs)
        views.append((f"{p} (soft)" if has_sub else p, top, "soft"))
        if has_sub:
            hard = [c.replace("__soft_", "__") for c in top]
            if all(h in team_wide.columns for h in hard):
                views.append((f"{p} (hard)", hard, "hard"))
            views.append((f"{p} sub-types (soft)", subs, "sub"))
    fig, ax = plt.subplots(figsize=(9.0, 0.78 * len(views) + 1.8))
    for i, (title, cols, kind) in enumerate(views):
        y = len(views) - 1 - i
        if kind != "sub" and len(cols) > len(slots):
            raise ValueError(f"{title}: {len(cols)} type columns but only {len(slots)} colours: {cols}")
        v = team_wide.loc[team_id, cols].to_numpy(float) if cols else np.array([np.nan])
        if np.isnan(v).all():
            ax.barh(y, 1.0, height=0.62, color="#d9d9d9")
            ax.text(0.5, y, "no classified players", ha="center", va="center", fontsize=7.5, color=ink2)
            continue
        left = 0.0
        for j, (c, s) in enumerate(zip(cols, np.nan_to_num(v))):
            ax.barh(y, s, left=left, height=0.62, color=colr(c, j), edgecolor=surface, linewidth=1.5)
            if s >= (0.05 if kind == "sub" else 0.09):
                t = lab(c).replace("Type ", "") if kind == "sub" else lab(c)
                ax.text(left + s / 2, y, f"{textwrap.fill(t, 12)}\n{s:.0%}", ha="center", va="center",
                        fontsize=7, color=ink)
            left += s
    ax.set_yticks(range(len(views)), [v[0] for v in views][::-1])
    ax.tick_params(axis="y", length=0)
    ax.set_xlim(0, 1)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}"))
    for s_ in ["left", "bottom"]:
        ax.spines[s_].set_visible(False)
    ax.set_xlabel("Share of the team's minutes at that position")
    ax.set_title(f"{names.get(team_id, team_id)}: player-type mix by position", loc="left")
    fig.tight_layout()
    return fig

def team_type_vs_group(team_wide, team_id, names, cluster_col, positions=None, share_cols=None,
                       leave_one_out=True, ncols=3, group_colours=None, type_cols=None, sub_types=True,
                       k=None, similarity=True, league_only=False):
    """One chart for the whole squad: for each position (and, with sub_types, its hard split and its sub-types) one row per
    player type on a 0-100% axis. The black line is the average share of the team's own group (team left out if
    leave_one_out); the bar runs from that line to the team's share (right = the team uses the type more, left = less).
    Plain number = the group's share (at the line), bold number = the team's share (end of the bar). A similarity strip on
    top shows how close the team is to each group.
    sub_types: for a position with sub-types (columns '<Position>__soft_<parent>_<child>') two more blocks: the hard parent
    shares ('<Position>__<parent>') and all the sub-types (soft split inside each hard parent), labelled parent.child.
    type_cols: the soft-share columns to use (default: every '<Position>__soft_<n>' and '<Position>__soft_<n>_<m>' column
    in team_wide). ncols: kept so existing calls work; not used. group_colours: {group: colour} for the strip.
    k, similarity: as in team_profile. The strip is the team's share of similarity to every group (shares add to 100%,
    its own group is outlined), read from sim_cluster_<i>_k<k> (k = the k argument, or the number of groups when k is
    None), each team's values divided by their sum. No strip when those columns are not in team_wide."""
    def suf(c):   # "Center Back__soft_3" -> "3"; "Center Back__soft_1_2" -> "1_2"; hard "Center Back__3" -> "3"
        s = str(c).split("__")[-1]
        return s[5:] if s.startswith("soft_") else s
    def lab(c):   # "Type 3"; a sub-type "Type 1.2"; a text suffix is shown as it is
        s = suf(c)
        return "Type " + s.replace("_", ".") if s.replace("_", "").isdigit() else s.replace("_", " ")
    def kid(c):   # is it a sub-type column ("<parent>_<child>")?
        return "_" in suf(c) and suf(c).replace("_", "").isdigit()
    def colr(c, j):   # a type: its slot colour; a sub-type: its parent's colour, lighter for later children
        if not kid(c):
            return slots[j]
        a, b = (int(t) for t in suf(c).split("_")[:2])
        return tuple(x + (1 - x) * (0.0, 0.3, 0.55, 0.7)[min(b, 3)]
                     for x in plt.matplotlib.colors.to_rgb(slots[a % len(slots)]))
    pool = list(type_cols) if type_cols is not None else [
        c for c in team_wide.columns if "__soft_" in c and c.split("__soft_")[-1].replace("_", "").isdigit()]
    if not pool:
        raise ValueError("no '<Position>__soft_<number>' columns in team_wide; pass type_cols=[...]")
    g = team_wide.loc[team_id, cluster_col]
    same = team_wide[cluster_col] == g
    league = None
    if league_only:                                     # only the teams of the team's own league
        if "league" not in team_wide.columns:
            raise KeyError("league_only needs a 'league' column in team_wide")
        league = team_wide.loc[team_id, "league"]
        same = same & (team_wide["league"] == league)
    members = team_wide.index[same]
    if leave_one_out:
        members = members.drop(team_id, errors="ignore")
    team_name = str(names.get(team_id, team_id))
    n_m = len(members)
    group_label = (f"Cluster {int(g)} average" + (f", {league}" if league_only else "")
                   + f" ({n_m} {'other ' if leave_one_out else ''}team{'' if n_m == 1 else 's'}"
                   + ("; few teams, read with care)" if league_only and n_m < 3 else ")"))
    groups = sorted(team_wide[cluster_col].dropna().unique())
    scores = None
    if similarity:                                      # strip from your sim_cluster_<i>_k<k> columns
        n_k = int(k) if k else len(groups)
        sim_cols = [f"sim_cluster_{i}_k{n_k}" for i in range(n_k)]
        if all(c in team_wide.columns for c in sim_cols):
            sim_v = team_wide.loc[team_id, sim_cols].astype(float)
            if np.isfinite(sim_v.to_numpy()).all() and sim_v.sum() > 0:
                scores = {f"Cluster {i}": float(v / sim_v.sum()) for i, v in enumerate(sim_v)}
    pos = list(positions) if positions else list(dict.fromkeys(c.split("__soft_")[0] for c in pool))
    views = []   # (title, columns, kind): kind is "soft", "hard" or "sub"
    for p in pos:
        mine = [c for c in pool if c.startswith(p + "__soft_")]
        top = list(share_cols) if share_cols else [c for c in mine if not kid(c)]
        subs = sorted([c for c in mine if kid(c)], key=lambda c: [int(t) for t in suf(c).split("_")])
        has_sub = sub_types and not share_cols and bool(subs)
        views.append((f"{p} (soft)" if has_sub else p, top, "soft"))
        if has_sub:
            hard = [c.replace("__soft_", "__") for c in top]
            if all(h in team_wide.columns for h in hard):
                views.append((f"{p} (hard)", hard, "hard"))
            views.append((f"{p} sub-types (soft)", subs, "sub"))
 
    # ---- rows: a heading per view, then one row per type ----
    rows, y = [], 0.0
    for title, cols, kind in views:
        if kind != "sub" and len(cols) > len(slots):
            raise ValueError(f"{title}: {len(cols)} type columns but only {len(slots)} colours: {cols}")
        t = team_wide.loc[team_id, cols].to_numpy(float)
        a = team_wide.loc[members, cols].mean().to_numpy(float)
        rows.append(("head", title, y)); y -= 0.95
        for j, c in enumerate(cols):
            rows.append(("row", lab(c), y, t[j], a[j], colr(c, j)))
            y -= 1.0
        y -= 0.35
    ymin = y + 0.5
 
    # ---- figure: sizes in inches (distances from the top: title .22, subtitle .5, note .74, strip, legend) ----
    LEFT, AX_W, RIGHT, BOTTOM = 1.15, 7.2, 0.45, 1.0
    STRIP_TOP, STRIP_H = 1.34, 0.90
    legend_y = (STRIP_TOP + STRIP_H + 0.12) if scores is not None else 1.08
    TOP = legend_y + 0.38
    plot_h = 0.255 * (0.7 - ymin)
    W, H = LEFT + AX_W + RIGHT, TOP + plot_h + BOTTOM
    fig = plt.figure(figsize=(W, H))
    fig.set_facecolor(surface)
    ax = fig.add_axes([LEFT / W, BOTTOM / H, AX_W / W, plot_h / H])
    ax.set_facecolor(surface)
    ax.set_ylim(ymin, 0.7); ax.set_xlim(0, 1)                      # always the full 0-100% scale
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_xticklabels(["0%", "25%", "50%", "75%", "100%"], fontsize=8.5, color=muted)
    ax.grid(axis="x"); ax.set_axisbelow(True)
    for s in ("top", "right", "left", "bottom"):
        ax.spines[s].set_visible(False)
    ax.tick_params(axis="y", length=0)
 
    ytl, ytl_lab, n_row, placed = [], [], 0, []
    for r in rows:
        if r[0] == "head":
            ax.text(0.995, r[2], r[1], ha="right", va="center", fontsize=9, fontweight="bold", color=ink)
            if n_row:
                ax.axhline(r[2] + 0.55, color=muted, linewidth=0.6, alpha=0.4)
            continue
        _, name, yy, tv, av, colour = r
        ytl.append(yy); ytl_lab.append(name)
        if n_row % 2 == 1:
            ax.axhspan(yy - 0.5, yy + 0.5, color="#f3f2ef", linewidth=0, zorder=0)
        n_row += 1
        if np.isfinite(av) and np.isfinite(tv) and abs(tv - av) < 5e-4:
            tv = av                                    # equal to the displayed precision: just the line, no bar
        if np.isfinite(av) and np.isfinite(tv) and tv != av:
            ax.barh(yy, tv - av, left=av, height=0.66, color=colour, edgecolor="none", zorder=3)   # the deviation
        if np.isfinite(av):                            # the group's average: the line
            ax.plot([av, av], [yy - 0.42, yy + 0.42], color=ink, linewidth=2.2, solid_capstyle="butt", zorder=4)
        elif np.isfinite(tv):                          # nobody to average against: just a marker where the team is
            ax.plot([tv], [yy], marker="D", markersize=5, color=ink, zorder=4, linestyle="")
        placed.append(dict(y=yy, tv=tv, av=av))
    ax.set_yticks(ytl); ax.set_yticklabels(ytl_lab, fontsize=8.5, color=ink2)
    ax.set_xlabel("Share of the position's minutes", fontsize=8.5, color=ink2, labelpad=8)
 
    # ---- numbers: written after the axes are fixed, so each can be measured against the room it has ----
    # layout A: the group's number on the far side of the line, the team's number just beyond the end of the bar.
    # If that does not fit: B = both beyond the end of the bar (team's first), or C = both on the far side of the line.
    fig.canvas.draw()
    rend = fig.canvas.get_renderer()
    px = lambda x: ax.transData.transform((x, 0))[0]
    dx = lambda p: ax.transData.inverted().transform((p, 0))[0]
    gap = 0.06 * fig.dpi
    x_min, x_max = px(0) + 2, px(1.0) + (RIGHT - 0.03) * fig.dpi   # text may reach the left of the axis and the right margin
    def mk(s, bold, italic=False, size=8):
        t = ax.text(0, 0, s, va="center", fontsize=size, fontweight="bold" if bold else "normal",
                    color=ink if bold else (muted if italic else ink2), style="italic" if italic else "normal",
                    zorder=6, clip_on=False)
        return t, t.get_window_extent(rend).width
    def put(t, x_px, ha, yy):
        t.set_ha(ha); t.set_position((dx(x_px), yy))
    def span(x_px, w, side):                           # pixel extent of a label written from x_px going towards `side`
        return (x_px, x_px + w) if side > 0 else (x_px - w, x_px)
    def fits(*spans):                                  # do these [left, right] pixel extents stay on the page?
        return min(a for a, _ in spans) >= x_min and max(b for _, b in spans) <= x_max
    for p in placed:
        yy, tv, av = p["y"], p["tv"], p["av"]
        if not np.isfinite(av):                        # team only
            if np.isfinite(tv):
                t_t, w_t = mk(f"{tv:.0%}", True); put(t_t, px(tv) + gap, "left", yy)
                n_t, _ = mk("no group average", False, True, 7.5); put(n_t, px(tv) + 2 * gap + w_t, "left", yy)
            continue
        g_t, w_g = mk(f"{av:.0%}", False)
        if not np.isfinite(tv):                        # the team has no classified players in this position
            n_t, w_n = mk("no classified players", False, True, 7.5)
            if px(av) + 3 * gap + w_g + w_n <= x_max:
                put(g_t, px(av) + gap, "left", yy); put(n_t, px(av) + 2 * gap + w_g, "left", yy)
            else:                                      # no room to the right of the line: write it all to the left
                put(g_t, px(av) - gap, "right", yy); put(n_t, px(av) - 2 * gap - w_g, "right", yy)
            continue
        t_t, w_t = mk(f"{tv:.0%}", True)
        s = 1 if tv >= av else -1                      # +1: the bar lies to the right of the line, -1: to the left
        ha_bar = "left" if s > 0 else "right"          # alignment of a label written beyond the bar's end
        ha_far = "right" if s > 0 else "left"          # alignment of a label written on the far side of the line
        if fits(span(px(av) - s * gap, w_g, -s), span(px(tv) + s * gap, w_t, s)):                       # A
            put(g_t, px(av) - s * gap, ha_far, yy); put(t_t, px(tv) + s * gap, ha_bar, yy)
        elif fits(span(px(tv) + s * gap, w_t, s), span(px(tv) + s * (2 * gap + w_t), w_g, s)):          # B
            put(t_t, px(tv) + s * gap, ha_bar, yy); put(g_t, px(tv) + s * (2 * gap + w_t), ha_bar, yy)
        elif fits(span(px(av) - s * gap, w_g, -s), span(px(av) - s * (2 * gap + w_g), w_t, -s)):        # C
            put(g_t, px(av) - s * gap, ha_far, yy); put(t_t, px(av) - s * (2 * gap + w_g), ha_far, yy)
        else:                                          # nothing fits: A anyway
            put(g_t, px(av) - s * gap, ha_far, yy); put(t_t, px(tv) + s * gap, ha_bar, yy)
 
    # ---- title, reading note, strip, legend ----
        fig.text(0.15 / W, 1 - 0.22 / H, "Share of minutes by player type, team vs its own group"
             + (" (own league only)" if league_only else ""), fontsize=11,
             fontweight="bold", va="center", color=ink)
    fig.text(0.15 / W, 1 - 0.50 / H, f"{team_name} against {group_label}.", fontsize=8.5, color=ink2, va="center")
    fig.text(0.15 / W, 1 - 0.74 / H, "Bar to the right of the line = the team uses this type more than its group, to the left = less.",
             fontsize=8.5, color=ink2, va="center")
    if scores is not None:
        gcol = group_colours if isinstance(group_colours, dict) else {}
        fig.text(0.15 / W, 1 - (STRIP_TOP - 0.42) / H, "Style similarity to each group (outlined = own group"
                 + ("; not league-specific)" if league_only else ")"), ha="left",
                 va="top", fontsize=8, color=ink2)
        _draw_similarity_strip(fig, scores, highlight_label=f"Cluster {int(g)}" if pd.notna(g) else None,
                               rect=(LEFT / W, 1 - (STRIP_TOP + STRIP_H) / H, AX_W / W, STRIP_H / H),
                               colors=[gcol.get(i, group_colours_list[i % len(group_colours_list)])
                                       for i in range(len(scores))])
    handles = [Line2D([0], [0], color=ink, linewidth=2.2,
                      label=f"Cluster {int(g)} average" + (f", {league}" if league_only else "") + " (line, plain number)"),
               Rectangle((0, 0), 1, 1, facecolor="#9a9892", label="Team minus group (bar, coloured by player type); bold number = team's share")]
    fig.legend(handles=handles, loc="center left", bbox_to_anchor=(LEFT / W, 1 - legend_y / H), ncol=2, frameon=False,
               fontsize=8, columnspacing=1.4)
    return fig

def group_type_shares(team_wide, cluster_col, positions=None, share_cols=None, include_all=True, ncols=3,
                      group_colours=None, type_cols=None, sub_types=True, league=None):
    """One panel per position: for each group the average share of each player type (100% bar).
    sub_types: for a position with sub-types (columns '<Position>__soft_<parent>_<child>') two more panels: the
    hard parent shares ('<Position>__<parent>') and all the sub-types in one bar (soft split inside each hard
    parent, so each parent's sub-types add up to its hard share); each sub-type has its parent's colour, lighter
    for later children.
    type_cols: the soft-share columns to use (default: every '<Position>__soft_<n>' and '<Position>__soft_<n>_<m>'
    column in team_wide)."""
    def suf(c):   # "Center Back__soft_3" -> "3"; "Center Back__soft_1_2" -> "1_2"; hard "Center Back__3" -> "3"
        s = str(c).split("__")[-1]
        return s[5:] if s.startswith("soft_") else s
    def lab(c):   # "Type 3"; a sub-type "Type 1.2"; a text suffix is shown as it is
        s = suf(c)
        return "Type " + s.replace("_", ".") if s.replace("_", "").isdigit() else s.replace("_", " ")
    def kid(c):   # is it a sub-type column ("<parent>_<child>")?
        return "_" in suf(c) and suf(c).replace("_", "").isdigit()
    def colr(c, j):   # a type: its slot colour; a sub-type: its parent's colour, lighter for later children
        if not kid(c):
            return slots[j]
        a, b = (int(t) for t in suf(c).split("_")[:2])
        return tuple(x + (1 - x) * (0.0, 0.3, 0.55, 0.7)[min(b, 3)]
                     for x in plt.matplotlib.colors.to_rgb(slots[a % len(slots)]))
    pool = list(type_cols) if type_cols is not None else [
        c for c in team_wide.columns if "__soft_" in c and c.split("__soft_")[-1].replace("_", "").isdigit()]
    if not pool:
        raise ValueError("no '<Position>__soft_<number>' columns in team_wide; pass type_cols=[...]")
    if league is not None:                                  # one league only: group averages over that league's teams
        if "league" not in team_wide.columns:
            raise KeyError("league needs a 'league' column in team_wide")
        team_wide = team_wide[team_wide["league"] == league]
        if team_wide.empty:
            raise ValueError(f"no teams in league {league!r}")
    groups = sorted(team_wide[cluster_col].dropna().unique())
    gnames = {g: f"Cluster {int(g)}" for g in groups}
    pos = list(positions) if positions else list(dict.fromkeys(c.split("__soft_")[0] for c in pool))
    views = []   # (title, columns, kind): kind is "soft", "hard" or "sub"
    for p in pos:
        mine = [c for c in pool if c.startswith(p + "__soft_")]
        top = list(share_cols) if share_cols else [c for c in mine if not kid(c)]
        subs = sorted([c for c in mine if kid(c)], key=lambda c: [int(t) for t in suf(c).split("_")])
        has_sub = sub_types and not share_cols and bool(subs)
        views.append((f"{p} (soft)" if has_sub else p, top, "soft"))
        if has_sub:
            hard = [c.replace("__soft_", "__") for c in top]
            if all(h in team_wide.columns for h in hard):
                views.append((f"{p} (hard)", hard, "hard"))
            views.append((f"{p} sub-types (soft)", subs, "sub"))
    rows = [(f"{gnames[g]} ({int((team_wide[cluster_col] == g).sum())})", team_wide.index[team_wide[cluster_col] == g])
            for g in groups]
    if include_all:
        rows.append((f"All {league} teams ({len(team_wide)})" if league is not None else f"All teams ({len(team_wide)})",
                     team_wide.index))
    nrows = int(np.ceil(len(views) / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(4.4 * ncols, (0.5 * len(rows) + 1.9) * nrows), squeeze=False)
    for ax, (title, cols, kind) in zip(axes.ravel(), views):
        if kind != "sub" and len(cols) > len(slots):
            raise ValueError(f"{title}: {len(cols)} type columns but only {len(slots)} colours: {cols}")
        for i, (name, ids) in enumerate(rows):
            y = len(rows) - 1 - i
            left = 0.0
            for j, (c, s) in enumerate(zip(cols, np.nan_to_num(team_wide.loc[ids, cols].mean().to_numpy(float)))):
                ax.barh(y, s, left=left, height=0.66, color=colr(c, j), edgecolor=surface, linewidth=1.5)
                if s >= (0.06 if kind == "sub" else 0.08):
                    ax.text(left + s / 2, y, f"{s:.0%}", ha="center", va="center", fontsize=7, color=ink)
                left += s
        ax.set_yticks(range(len(rows)), [r[0] for r in rows][::-1], fontsize=7.5)
        ax.tick_params(axis="y", length=0)
        ax.set_xlim(0, 1)
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}"))
        for s_ in ["left", "bottom"]:
            ax.spines[s_].set_visible(False)
        ax.set_title(title, loc="left", fontsize=9.5)
        ax.legend(handles=[Patch(color=colr(c, j), label=textwrap.shorten(lab(c), 22)) for j, c in enumerate(cols)],
                  loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=2, fontsize=6.5, frameon=False)
    for ax in axes.ravel()[len(views):]:
        ax.axis("off")
    fig.suptitle("Average share of minutes by player type, by group" + (f", {league}" if league is not None else ""),
                 x=0.01, ha="left", fontweight="bold",
                 fontsize=10.5)
    fig.tight_layout()
    return fig

def team_type_shares(team_wide, cluster_col, position, names, share_cols=None, group_colours=None,
                     type_cols=None, sub=False, league=None):
    """One 100% bar per team for one position, teams grouped by cluster and sorted inside each cluster by the
    first type's share. Teams with no classified players at that position show as a grey bar.
    sub: False = the position's soft type shares; "hard" = its hard type shares (columns '<Position>__<n>');
    True = its sub-types in one bar (columns '<Position>__soft_<parent>_<child>', a soft split inside each hard
    parent), each in its parent's colour, lighter for later children.
    type_cols: the soft-share columns to use (default: every '<Position>__soft_<n>' and '<Position>__soft_<n>_<m>'
    column in team_wide)."""
    def suf(c):   # "Center Back__soft_3" -> "3"; "Center Back__soft_1_2" -> "1_2"; hard "Center Back__3" -> "3"
        s = str(c).split("__")[-1]
        return s[5:] if s.startswith("soft_") else s
    def lab(c):   # "Type 3"; a sub-type "Type 1.2"; a text suffix is shown as it is
        s = suf(c)
        return "Type " + s.replace("_", ".") if s.replace("_", "").isdigit() else s.replace("_", " ")
    def kid(c):   # is it a sub-type column ("<parent>_<child>")?
        return "_" in suf(c) and suf(c).replace("_", "").isdigit()
    def colr(c, j):   # a type: its slot colour; a sub-type: its parent's colour, lighter for later children
        if not kid(c):
            return slots[j]
        a, b = (int(t) for t in suf(c).split("_")[:2])
        return tuple(x + (1 - x) * (0.0, 0.3, 0.55, 0.7)[min(b, 3)]
                     for x in plt.matplotlib.colors.to_rgb(slots[a % len(slots)]))
    pool = list(type_cols) if type_cols is not None else [
        c for c in team_wide.columns if "__soft_" in c and c.split("__soft_")[-1].replace("_", "").isdigit()]
    if not pool:
        raise ValueError("no '<Position>__soft_<number>' columns in team_wide; pass type_cols=[...]")
    if league is not None:                                  # one league only: its teams, still grouped by style group
        if "league" not in team_wide.columns:
            raise KeyError("league needs a 'league' column in team_wide")
        team_wide = team_wide[team_wide["league"] == league]
        if team_wide.empty:
            raise ValueError(f"no teams in league {league!r}")
    groups = sorted(team_wide[cluster_col].dropna().unique())
    gnames = {g: f"Cluster {int(g)}" for g in groups}
    mine = [c for c in pool if c.startswith(position + "__soft_")]
    tag = {False: "", "hard": " (hard)", True: " sub-types (soft)"}[sub]
    if share_cols:
        cols = list(share_cols)
    elif sub is True:
        cols = sorted([c for c in mine if kid(c)], key=lambda c: [int(t) for t in suf(c).split("_")])
    else:
        cols = [c for c in mine if not kid(c)]
        if sub == "hard":
            cols = [c.replace("__soft_", "__") for c in cols]
            if not all(c in team_wide.columns for c in cols):
                raise ValueError(f"{position}: hard share columns {cols} are not all in team_wide")
    if not cols:
        raise ValueError(f"{position}: no{tag or ' type'} columns found")
    if sub is not True and len(cols) > len(slots):
        raise ValueError(f"{position}: {len(cols)} type columns but only {len(slots)} colours: {cols}")
    rows, ypos, heads, yy = [], [], [], 0.0
    for g in groups:
        ids = list(team_wide.index[team_wide[cluster_col] == g])
        ids = sorted(ids, key=lambda t: -np.nan_to_num(team_wide.loc[t, cols[0]], nan=-1))
        heads.append((yy, f"{gnames[g]} ({len(ids)})")); yy += 1.2
        for t in ids:
            rows.append(t); ypos.append(yy); yy += 1
        yy += 0.6
    fig, ax = plt.subplots(figsize=(8.2, 0.24 * len(rows) + 2.6))
    left = np.zeros(len(rows))
    for i, c in enumerate(cols):
        v = team_wide.loc[rows, c].to_numpy(float)
        ax.barh(ypos, np.nan_to_num(v), left=left, height=0.82, color=colr(c, i), edgecolor=surface, linewidth=1.0,
                label=lab(c))
        left += np.nan_to_num(v)
    missing = team_wide.loc[rows, cols].isna().all(axis=1).to_numpy()
    ax.barh(np.array(ypos)[missing], 1.0, height=0.82, color="#d9d9d9", label="No classified players")
    ax.set_yticks(ypos, [names.get(t, t) for t in rows], fontsize=7)
    ax.tick_params(axis="y", length=0)
    for y0, h in heads:
        ax.text(-0.01, y0, h, ha="right", va="center", fontsize=8.5, fontweight="bold", color=ink,
                transform=ax.get_yaxis_transform())
    ax.axvline(0.5, color=surface, linewidth=0.8, linestyle=(0, (2, 2)))
    ax.set_xlim(0, 1); ax.invert_yaxis()
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}"))
    for s in ["left", "bottom"]:
        ax.spines[s].set_visible(False)
    ax.set_xlabel(f"Share of the team's {position.lower()} minutes")
    h, l = ax.get_legend_handles_labels()
    h[-1] = Patch(color="#d9d9d9")        # the empty grey bar has no patch to take its legend colour from
    ax.legend(h, l, loc="lower left", bbox_to_anchor=(0, 1.0), ncol=4, fontsize=8)
    ax.set_title(f"{position}{tag}: player-type mix by team" + (f", {league}" if league is not None else ""),
                 loc="left", pad=28 + 15 * (len(cols) // 4))
    fig.tight_layout()
    return fig

def export_team_type_mix(team_wide, team_id_to_team, team_id_to_league, team_ids=None, fig_dir=player_fig_dir,
                         position="teams", filename="type_shares.png", dpi=200, **kwargs):
    """One plot per team, no group involved -> <...>/all_k/<Team>_<League>/type_shares.png."""
    paths = []
    for team_id in (team_ids if team_ids is not None else list(team_id_to_team)):
        fig = team_type_mix(team_wide, team_id, team_id_to_team, **kwargs)
        out_dir = os.path.join(fig_dir, position, "all_k",
                               get_folder_name(team_id, team_id, team_id_to_team, team_id_to_league))
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, filename)
        fig.savefig(path, dpi=dpi, bbox_inches="tight")
        plt.close(fig)
        paths.append(path)
    print(f"saved {len(paths)} team player-type mixes to {os.path.abspath(os.path.join(fig_dir, position, 'all_k'))}")
    return paths

def export_team_type_vs_group(team_wide, cluster_col, n_clusters, team_id_to_team, team_id_to_league,
                              team_ids=None, fig_dir=player_fig_dir, position="teams",
                              filename="type_shares_vs_group.png", dpi=200, **kwargs):
    """One plot per team -> <...>/k<n>/<Team>_<League>/type_shares_vs_group.png."""
    paths = []
    for team_id in (team_ids if team_ids is not None else list(team_id_to_team)):
        fig = team_type_vs_group(team_wide, team_id, team_id_to_team, cluster_col, **kwargs)
        out_dir = os.path.join(fig_dir, position, f"k{n_clusters}",
                               get_folder_name(team_id, team_id, team_id_to_team, team_id_to_league))
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, filename.replace(".png", "_league.png") if kwargs.get("league_only") else filename)
        fig.savefig(path, dpi=dpi, bbox_inches="tight")
        plt.close(fig)
        paths.append(path)
    print(f"saved {len(paths)} team-vs-group player-type plots (k = {n_clusters}) to "
          f"{os.path.abspath(os.path.join(fig_dir, position, f'k{n_clusters}'))}")
    return paths

def export_group_type_shares(team_wide, cluster_col, n_clusters, fig_dir=player_fig_dir, position="teams",
                             filename="type_shares_by_group.png", dpi=200, **kwargs):
    """-> <...>/k<n>/_groups/type_shares_by_group.png."""
    fig = group_type_shares(team_wide, cluster_col, **kwargs)
    out_dir = os.path.join(fig_dir, position, f"k{n_clusters}")
    os.makedirs(out_dir, exist_ok=True)
    league = kwargs.get("league")
    path = os.path.join(out_dir, filename if league is None
                        else filename.replace(".png", f"_{str(league).replace('/', '-').replace(' ', '_').replace("'", '')}.png"))
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    return path

def export_group_type_shares_by_league(team_wide, cluster_col, n_clusters, leagues=None, **kwargs):
    leagues = list(leagues) if leagues is not None else sorted(team_wide["league"].dropna().unique())
    return [export_group_type_shares(team_wide, cluster_col, n_clusters, league=lg, **kwargs) for lg in leagues]

def export_team_type_shares(team_wide, cluster_col, n_clusters, names, positions=None, fig_dir=player_fig_dir,
                            position="teams", dpi=200, type_cols=None, sub_types=True, league=None, **kwargs):
    """One all-teams plot per position -> <...>/k<n>/_groups/type_shares_teams_<Position>.png; for a position with
    sub-types also type_shares_teams_<Position>_hard.png (hard parent shares) and
    type_shares_teams_<Position>_sub.png (the sub-types in one bar); sub_types=False leaves those out."""
    pool = list(type_cols) if type_cols is not None else [
        c for c in team_wide.columns if "__soft_" in c and c.split("__soft_")[-1].replace("_", "").isdigit()]
    pos = list(positions) if positions else list(dict.fromkeys(c.split("__soft_")[0] for c in pool))
    out_dir = os.path.join(fig_dir, position, f"k{n_clusters}")
    os.makedirs(out_dir, exist_ok=True)
    paths = []
    for p in pos:
        slug = p.replace('/', '-').replace(' ', '_').replace("'", '')
        mine = [c for c in pool if c.startswith(p + "__soft_")]
        top = [c for c in mine if "_" not in c.split("__soft_")[-1]]
        modes = [(False, "")]
        if sub_types and any("_" in c.split("__soft_")[-1] for c in mine):
            if all(c.replace("__soft_", "__") in team_wide.columns for c in top):
                modes.append(("hard", "_hard"))
            modes.append((True, "_sub"))
        for sub, ext in modes:
            fig = team_type_shares(team_wide, cluster_col, p, names, type_cols=type_cols, sub=sub, league=league, **kwargs)
            path = os.path.join(out_dir, f"type_shares_teams_{slug}{ext}"
                                + (f"_{str(league).replace('/', '-').replace(' ', '_').replace("'", '')}" if league is not None else "") + ".png")
            fig.savefig(path, dpi=dpi, bbox_inches="tight")
            plt.close(fig)
            paths.append(path)
    return paths

def export_team_type_shares_by_league(team_wide, cluster_col, n_clusters, names, leagues=None, **kwargs):
    leagues = list(leagues) if leagues is not None else sorted(team_wide["league"].dropna().unique())
    paths = []
    for lg in leagues:
        paths += export_team_type_shares(team_wide, cluster_col, n_clusters, names, league=lg, **kwargs)
    return paths

pos, neg = "#2a78d6", "#e34948" 

# ============================================================================================= #
# 7. Team card (one page per team): how the squad is built, how it plays, closest comparators
# ============================================================================================= #
def _card_subheader(team_wide, team_id, cluster_cols, similarity=True, margin_cut=0.10):
    """'k=2: group 0 (leads by 20 pts) · k=3: group 0 (between groups, leads by 2 pts; moved) · ...'
    group = cluster column; lead = own share minus best other share (sim_cluster_<i>_k<k>, divided by their sum);
    between groups = lead under margin_cut; moved = the team's group at the previous k is not the group most of
    its new group's teams came from (same rule as team_paths)."""
    bits, prev = [], None
    for c in [c for c in cluster_cols if c in team_wide.columns]:
        lab = team_wide[c].dropna().astype(int)
        if team_id not in lab.index:
            prev = None
            continue
        groups = sorted(lab.unique())
        k, g = len(groups), int(lab[team_id])
        notes = []
        sim_cols = [f"sim_cluster_{i}_k{k}" for i in groups]
        if similarity and all(s in team_wide.columns for s in sim_cols):
            p = team_wide.loc[team_id, sim_cols].to_numpy(float)
            if np.isfinite(p).all() and p.sum() > 0:
                p = p / p.sum()
                gi = groups.index(g)
                lead = p[gi] - np.delete(p, gi).max()
                pts = f"{np.floor(abs(lead) * 1000 + 1e-9) / 10:g}"   # points, one decimal, rounded down: never "10 pts" under the cut
                if 0 <= lead < margin_cut:
                    notes.append("between groups")
                notes.append(f"leads by {pts} pts" if lead >= 0 else f"behind by {pts} pts")
        if prev is not None:
            p_lab = team_wide[prev].dropna().astype(int)
            members = lab.index[(lab == g)].intersection(p_lab.index)
            parent = int(p_lab[members].value_counts().sort_index().idxmax())
            if team_id in p_lab.index and int(p_lab[team_id]) != parent:
                notes[-1:] = [notes[-1] + "; moved"] if notes else ["moved"]
        bits.append(f"k={k}: group {g}" + (f" ({', '.join(notes)})" if notes else ""))
        prev = c
    return "  ·  ".join(bits)
 
 
def _fmt_raw(col, v, series):
    """Raw value for the value column: shares / percentages as %, everything else with 3 dps."""
    try:
        v = float(v)
    except (TypeError, ValueError):
        return "–"
    if not np.isfinite(v):
        return "–"
    name = str(col).lower()
    if "pct" in name or "share" in name or "tilt" in name:
        s = pd.to_numeric(series, errors="coerce").dropna()
        return f"{v * 100:.3f}%" if len(s) and s.between(0, 1).all() else f"{v:.3f}%"
    return f"{v:.3f}"
 
 
def _closest_from_D(D, team_id, n, close_share):
    """Closest n teams to team_id in D (divided by its median pair, so 1 = a typical pair), how many teams are within the
    close cut (the closest close_share of all pairs) and the cut itself. None when the team is not in D."""
    if D is None or team_id not in D.index or team_id not in D.columns:
        return None
    ids = [t for t in D.index if t in D.columns]
    M = D.loc[ids, ids].astype(float)
    off = M.to_numpy()[np.triu_indices(len(ids), 1)]
    off = off[np.isfinite(off)]
    med = float(np.median(off))
    cut = float(np.quantile(off, close_share)) / med
    row = (M.loc[team_id].drop(team_id) / med).dropna().sort_values()
    return row.head(n), int((row <= cut + 1e-12).sum()), cut

_card_labels = {"ppda_inv": "pressing intensity (-ppda)"}

def _formation_rows(occ, team_id, fm=None, min_share=0.02, back_3_share=None, wingerless_share=None):
    """The same numbers as formation_profile_team: formations by share of minutes (those under min_share merged into
    'Other (n)'), then the back-three share (from back_3_share, else worked out from formations starting 3 or 5) and the
    no-wingers share (only when wingerless_share has the team). Returns (rows, n_main, binary, back_3_given);
    rows = [(label, share, minutes or None)], binary = [(label, share)]."""
    fm = formation_minutes(occ) if fm is None else fm
    t = fm[fm["team_id"] == team_id].copy()
    if t.empty:
        raise ValueError(f"no formation minutes for team {team_id}")
    t["label"] = [formation_text(c) for c in t["formation"]]
    mcol = next((c for c in ("minutes", "mins", "minutes_played") if c in t.columns), None)
    t = t.groupby("label").agg({"share": "sum", **({mcol: "sum"} if mcol else {})}).sort_values("share",
                                                                                              ascending=False)
    shown = t[t["share"] >= min_share]
    rest = t[t["share"] < min_share]
    rows = [(f, float(r["share"]), float(r[mcol]) if mcol else None) for f, r in shown.iterrows()]
    if len(rest):
        rows.append((f"Other ({len(rest)})", float(rest["share"].sum()), float(rest[mcol].sum()) if mcol else None))
    n_main = len(rows) - (1 if len(rest) else 0)
    b3_s = back_3_share.iloc[:, 0] if isinstance(back_3_share, pd.DataFrame) else back_3_share
    nw_s = wingerless_share.iloc[:, 0] if isinstance(wingerless_share, pd.DataFrame) else wingerless_share
    b3_given = b3_s is not None and team_id in b3_s.index and pd.notna(b3_s.loc[team_id])
    nw_given = nw_s is not None and team_id in nw_s.index and pd.notna(nw_s.loc[team_id])
    if b3_given:
        binary = [("Back three", float(b3_s.loc[team_id]))]
    else:
        binary = [("Back three", float(t[[f[0] in "35" for f in t.index]]["share"].sum()))]
    if nw_given:
        binary.append(("No wingers", float(nw_s.loc[team_id])))
    return rows, n_main, binary, b3_given

def team_card(team_wide, team_id, team_id_to_team, team_id_to_league, card_style_cols, nb=None, nb_resid=None,
              type_cols=None, cluster_cols=None, league_col="league", n_neighbours=5,
              label_strip=("_adj",), row_in=0.27, similarity=True,
              D_squad=None, D_style=None, D_overall=None, close_share=0.10, mark_shared=True,
              adj_suffix="_adj", style_reference="all", show_raw_tick=False, labels=None, margin_cut=0.10,
              stand_out=True, occ=None, fm=None, formation_min_share=0.02, back_3_share=None, wingerless_share=None):
    """One team on one page. The clustering appears only in the subheader; the three panels describe the team.
    Left:   how the squad is built (unchanged). For every player type ('<Position>__soft_<n>', shown as 'Type <n>') the
            average share of minutes over all teams sits in a strip in the middle; the bar is how far above (right) or
            below (left) that average the team is, in percentage points.
    Middle: how it plays. card_style_cols = list, or dict {category: [columns]} (bold heading per category). For a column
            with a partner column + adj_suffix the bar is the z-score of the partner (strength-adjusted) against all teams
            (style_reference="all") or the own league ("league"); a column without a partner (e.g. possession_pct,
            field_tilt, ppda_inv, context_score) is the raw z-score against the own league (marked ° when the card mixes
            both kinds). The raw value is printed on the right. Bars within 1 z are pale. show_raw_tick=True adds a | at
            the raw z-score against the own league for the adjusted rows. labels={column: label} for plain labels.
    Right:  D_squad / D_style / D_overall (team x team distance DataFrames) -> "Builds most like", "Plays most like",
            "Most like overall": rank, team, distance (1 = a typical pair in that table); the heading counts the teams
            within the closest close_share of pairs, names outside that cut are grey; mark_shared puts a ◆ after names
            in more than one list. Without any D_*, the nb / nb_resid tables (team_id, rank, neighbour, distance) are
            listed as before. A table that is None is left out.
    Subheader: one entry per cluster column (default every 'kmeans_<k>_cluster'; [] for none): group, lead over the next
            group in points (similarity=False leaves it out), 'between groups' under margin_cut, 'moved' as in team_paths.
    stand_out: two lines under "How it plays": the (up to) three highest and two lowest style rows at least 1 z from
            average (the strength-adjusted rows when the card has them, else every row).
    Formations (bottom of the right column): pass occ (or fm = formation_minutes(occ)) to list the formations by share
            of minutes, then the back-three and no-wingers shares - the same numbers and arguments as your
            formation_profile_team (formation_min_share = its min_share, back_3_share, wingerless_share).
    label_strip: words removed from the style labels ('_pct' stays). row_in: height of one row in inches."""
    if type_cols is None:
        type_cols = [c for c in team_wide.columns if "__soft_" in str(c) and str(c).split("__soft_")[-1].isdigit()]
    type_cols = [c for c in type_cols if c in team_wide.columns]
    if not type_cols:
        raise ValueError("no player-type columns found in team_wide ('<Position>__soft_<n>'); pass type_cols=[...]")
    if style_reference not in ("all", "league"):
        raise ValueError("style_reference must be 'all' or 'league'")
    if isinstance(label_strip, str):                             # ("_adj") is a plain string, not a tuple: treat it as one word
        label_strip = (label_strip,)
    if cluster_cols is None:
        cluster_cols = sorted(c for c in team_wide.columns if str(c).startswith("kmeans_") and str(c).endswith("_cluster"))
    if isinstance(card_style_cols, dict):
        style_groups = [(str(k).replace("_", " ").capitalize(), [c for c in cs if c in team_wide.columns])
                        for k, cs in card_style_cols.items()]                 # headings as in team_profile: build_up -> Build up
    else:
        style_groups = [(None, [c for c in card_style_cols if c in team_wide.columns])]
    style_groups = [(k, cs) for k, cs in style_groups if cs]
    style_cols = [c for _, cs in style_groups for c in cs]
    n_teams = len(team_wide)
    title = get_display_name(team_id, team_id, team_id_to_team, team_id_to_league)
    name_of = lambda nid: (get_display_name(nid, nid, team_id_to_team, team_id_to_league) if nid in team_id_to_team
                           else str(nid))
 
    # ---- right column: the lists ----
    lists = []                                                   # dicts: head, caption, rows [(rank, id, dist, close)], n_close
    if any(d is not None for d in (D_squad, D_style, D_overall)):
        for D_, head, cap in [(D_squad, "Builds most like", "player-type minutes"),
                              (D_style, "Plays most like", "style, strength-adjusted"),
                              (D_overall, "Most like overall", "style and squad together")]:
            if D_ is None:
                continue
            res = _closest_from_D(D_, team_id, n_neighbours, close_share)
            if res is None:
                lists.append(dict(head=head, caption=cap, rows=[], n_close=None))
                continue
            row, n_close, cut = res
            lists.append(dict(head=head, caption=cap, n_close=n_close,
                              rows=[(r + 1, nid, float(d), d <= cut + 1e-12) for r, (nid, d) in enumerate(row.items())]))
    else:
        for tbl, head in [(nb, "Closest comparators"), (nb_resid, "Closest comparators (residuals)")]:
            if tbl is not None:
                sub = tbl.loc[tbl["team_id"] == team_id].sort_values("rank").head(n_neighbours)
                lists.append(dict(head=head, caption=None, n_close=None,
                                  rows=[(int(r["rank"]), r["neighbour"], float(r["distance"]), True) for _, r in sub.iterrows()]))
    shown = [set(nid for _, nid, _, _ in L_["rows"]) for L_ in lists]
    shared = {nid for s in shown for nid in s if sum(nid in s2 for s2 in shown) > 1} if mark_shared else set()
 
    # ---- rows of the left panel: a bold position heading, then one row per type ----
    positions = []
    for c in type_cols:
        p = str(c).split("__soft_")[0]
        if p not in positions:
            positions.append(p)
    ys1, heads1, y = {}, {}, 0.0
    for p in positions:
        heads1[p] = y + 0.5
        y += 1.0
        for c in type_cols:
            if str(c).split("__soft_")[0] == p:
                ys1[c] = y + 0.5
                y += 1.0
        y += 0.4
    total1 = y
 
    # ---- middle panel: which yardstick each row uses, and its label ----
    adj_of = {c: (str(c) + adj_suffix if adj_suffix and (str(c) + adj_suffix) in team_wide.columns else None)
              for c in style_cols}
    has_adj = any(v is not None for v in adj_of.values())
    has_raw = any(v is None for v in adj_of.values())
    mixed = has_adj and has_raw
    def_labels = {}
    for c in style_cols:
        s = str(c)
        for word in label_strip:
            if word:
                s = (s + "_").replace(word + "_", "_")[:-1]
        def_labels[c] = s.replace("_", " ").strip()
    seen = pd.Series(list(def_labels.values())).value_counts()
    for c in style_cols:
        if seen[def_labels[c]] > 1:
            def_labels[c] = str(c).replace("_", " ")
    for c in style_cols:
        if labels and c in labels:
            def_labels[c] = str(labels[c])
        elif str(c) in _card_labels:
            def_labels[c] = _card_labels[str(c)]
        if mixed and adj_of[c] is None:
            def_labels[c] += " °"
    def_labels = {c: "\n".join(textwrap.wrap(t, 60)) for c, t in def_labels.items()}
    ys2, heads2, y = {}, {}, 0.0
    for k, cs in style_groups:
        if k is not None:
            heads2[k] = y + 0.5
            y += 1.0
        for c in cs:
            ys2[c] = y + 0.5
            y += 1.0
        y += 0.4 if k is not None else 0.0
    total2 = y
 
    lg = team_wide.loc[team_id, league_col] if league_col in team_wide.columns else None
    has_lg = lg is not None and pd.notna(lg)
    in_league = (team_wide[league_col] == lg) if has_lg else pd.Series(True, index=team_wide.index)
    every = pd.Series(True, index=team_wide.index)
 
    def zscore(col, mask):
        peers = pd.to_numeric(team_wide.loc[mask, col], errors="coerce").dropna()
        try:
            v = float(team_wide.loc[team_id, col])
        except (TypeError, ValueError):
            return np.nan
        sd = peers.std(ddof=0)                                  # divide by n, like the StandardScaler behind your _z columns
        if len(peers) < 3 or not sd > 0 or not np.isfinite(v):
            return np.nan
        return (v - peers.mean()) / sd
 
    z, zraw = {}, {}
    for c in style_cols:
        if adj_of[c] is not None:
            z[c] = zscore(adj_of[c], every if style_reference == "all" else in_league)
            zraw[c] = zscore(c, in_league) if show_raw_tick else np.nan
        else:
            z[c] = zscore(c, in_league)
            zraw[c] = np.nan
    lg_name = lg if has_lg else "all teams"
    n_lg = int(in_league.sum())
    ref_txt = f"all {n_teams} teams" if style_reference == "all" else f"{lg_name} ({n_lg} teams)"
    if has_adj and not has_raw:
        xlab = f"z-score, strength-adjusted, vs {ref_txt}"
    elif mixed:
        xlab = f"z-score: style strength-adjusted vs {ref_txt}\n° raw vs {lg_name} ({n_lg} teams)"
    else:
        xlab = f"z-score within {lg_name} ({n_lg} teams)"
 
    # ---- stand-out lines: the clearest style traits, high and low ----
    so_lines = []
    if stand_out:
        pool = [c for c in style_cols if (adj_of[c] is not None or not has_adj) and np.isfinite(z[c])]
        clean = lambda c: def_labels[c].replace("\n", " ").removesuffix(" °")
        hi_ = sorted([c for c in pool if z[c] >= 1], key=lambda c: -z[c])[:3]
        lo_ = sorted([c for c in pool if z[c] <= -1], key=lambda c: z[c])[:2]
        if hi_:
            so_lines.append(("Stands out for: ", [f"{clean(c)} ({z[c]:+.1f})" for c in hi_]))
        if lo_:
            so_lines.append(("Low on: ", [f"{clean(c)} ({z[c]:+.1f})" for c in lo_]))
        if not so_lines:
            so_lines.append(("", ["No style row is more than 1 from the average."]))
 
    # ---- formations (same numbers as formation_profile_team) ----
    form = form_err = None
    if occ is not None or fm is not None:
        try:
            form = _formation_rows(occ, team_id, fm=fm, min_share=formation_min_share, back_3_share=back_3_share,
                                   wingerless_share=wingerless_share)
        except ValueError as e:
            form_err = str(e)
 
    # ---- page geometry in inches ----
    L, R, gap = 0.3, 0.3, 0.45
    g1, w1 = 0.85, 4.05                                            # type labels | bars with the average strip in the middle
    g2 = min(4.3, 0.062 * max(len(s) for s in def_labels.values()) + 0.3) if def_labels else 1.6
    g2 = max(g2, 1.6)
    w2, vw = 4.0, 0.75                                             # bars | value column
    side = g1 + w1                  # left and right blocks get the same width, so the middle block is centred on the page
    w3 = side
    LIST_HEAD, ROW_L, LIST_END = 0.9, 0.38, 0.3
    right_need = sum(LIST_HEAD + max(len(L_["rows"]), 1) * ROW_L + LIST_END for L_ in lists)
    if form is not None:
        right_need += 0.65 + (len(form[0]) + 1) * ROW_L + (0.3 if not form[3] else 0.0)
    elif form_err:
        right_need += 0.65 + ROW_L
    so_wrapped, so_width = [], int((g2 + w2 + vw) * 72 / (8.5 * 0.52))
    for prefix, items in so_lines:                              # wrap between traits, never inside one
        cur = prefix
        for i, it in enumerate(items):
            piece = it + (", " if i < len(items) - 1 else "")
            if len(cur) + len(piece) > so_width and cur != prefix:
                so_wrapped.append(cur.rstrip())
                cur = "    " + piece
            else:
                cur += piece
        so_wrapped.append(cur.rstrip())    
    so_h = 0.15 + 0.2 * len(so_wrapped) if so_wrapped else 0.0
    top_off, bottom_off = 1.45 + so_h, 1.25
    body_h = max(total1 * row_in, total2 * row_in, right_need - 0.4 - so_h)
    right_side = bool(lists) or form is not None or bool(form_err)
    W = L + side + gap + g2 + w2 + vw + (gap + side if right_side else 0.0) + R
    H = top_off + body_h + bottom_off
    fig = plt.figure(figsize=(W, H))
    x1 = L + g1
    x2 = L + side + gap + g2
    x3 = x2 + w2 + vw + gap
 
    def rect(x0, w, h, top=top_off):   # inches (from the left, from the top) -> figure fractions
        return [x0 / W, (H - top - h) / H, w / W, h / H]
 
    # ---- header ----
    fig.text(L / W, 1 - 0.40 / H, title, fontsize=17, fontweight="bold", color=ink, ha="left", va="center")
    line = _card_subheader(team_wide, team_id, cluster_cols, similarity=similarity, margin_cut=margin_cut)
    if line:
        fig.text(L / W, 1 - 0.80 / H, line, fontsize=10, color=ink2, ha="left", va="center")
    fig.text((L + side / 2) / W, 1 - 1.22 / H, "How the squad is built", fontsize=11.5, fontweight="bold", color=ink,
             ha="center", va="center")
    fig.text((x2 + (w2 + vw - g2) / 2) / W, 1 - 1.22 / H, "How it plays", fontsize=11.5, fontweight="bold", color=ink,
             ha="center", va="center")
    for i, ln in enumerate(so_wrapped):                           # stand-out lines under the heading
        fig.text((x2 - g2) / W, 1 - (1.52 + 0.2 * i) / H, ln, fontsize=8.5, color=ink2, ha="left", va="center")
 
    # ---- left: how the squad is built (the average in a strip in the middle, bars = team minus average) ----
    ax = fig.add_axes(rect(x1, w1, total1 * row_in, top=1.45))     # the squad panel stays right under its heading
    avg = team_wide[type_cols].mean()
    v = team_wide.loc[team_id, type_cols].astype(float)
    lean = (v - avg) * 100
    top = max(float(np.nanmax(np.abs(lean.values))) if lean.notna().any() else 5.0, 5.0) * 1.35
    off = 0.3 * 2 * top / (w1 - 0.6)                      # half-width of the middle strip in axis units (0.6 inches wide)
    for p, yy in heads1.items():
        ax.text(-(g1 - 0.05) / w1, yy, p, transform=ax.get_yaxis_transform(), ha="left", va="center", fontsize=9.5,
                fontweight="bold", color=ink, clip_on=False)
    ax.axvspan(-off, off, color=axis_colour, alpha=0.15, linewidth=0, zorder=1)
    for c in type_cols:
        ax.text(0.0, ys1[c], f"{avg[c]:.0%}", ha="center", va="center", fontsize=8, color=ink2, zorder=5)
        if pd.isna(lean[c]):
            ax.text(off + top * 0.04, ys1[c], "no classified players", ha="left", va="center", fontsize=7.5, color=muted,
                    style="italic")
            continue
        sg = 1.0 if lean[c] >= 0 else -1.0
        ax.barh(ys1[c], lean[c], left=sg * off, height=0.62, color=pos if sg > 0 else neg,
                alpha=1.0 if abs(lean[c]) >= 5 else 0.45, zorder=3)
        ax.text(sg * off + lean[c] + sg * top * 0.03, ys1[c], f"{round(float(lean[c])) + 0.0:+.0f}",
                ha="left" if sg > 0 else "right", va="center", fontsize=8, color=ink, zorder=4)
    step = 5 if top <= 20 else (10 if top <= 45 else 20)
    marks = [t for t in range(-int(top // step) * step, int(top // step) * step + 1, step) if t != 0]
    ax.set_xticks([np.sign(t) * off + t for t in marks])
    ax.set_xticklabels([f"{t:+d}" for t in marks])
    ax.grid(axis="x", color=axis_colour, alpha=0.25, linewidth=0.6)
    ax.set_axisbelow(True)
    ax.set_xlim(-(top + off), top + off)
    ax.set_ylim(total1, 0)
    ax.set_yticks([ys1[c] for c in type_cols])
    ax.set_yticklabels(["Type " + str(c).split("__soft_")[-1] for c in type_cols], fontsize=8.5, color=ink2)
    ax.tick_params(axis="y", length=0)
    ax.tick_params(axis="x", labelsize=8, colors=muted)
    ax.set_xlabel(f"bars: percentage points above or below the average\nmiddle strip: average share of minutes over {n_teams} teams",
                  fontsize=8, color=muted)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(axis_colour)
 
    # ---- middle: how it plays (bar = z-score, value column = raw value) ----
    ax = fig.add_axes(rect(x2, w2, total2 * row_in))
    yax = ax.get_yaxis_transform()
    for k, yy in heads2.items():
        ax.text(-(g2 - 0.05) / w2, yy, k, transform=yax, ha="left", va="center", fontsize=9.5, fontweight="bold",
                color=ink, clip_on=False)
    xv = 1 + vw / w2                                               # right edge of the value column, in axes fraction
    ax.text(xv, -0.15, "value", transform=yax, ha="right", va="bottom", fontsize=7.5, color=muted, clip_on=False)
    for c in style_cols:
        rc = c                                                     # the raw column whose value is printed
        if adj_suffix and str(c).endswith(adj_suffix):             # an '_adj' column was passed: print its raw partner
            base = str(c)[: -len(adj_suffix)]
            rc = base if base in team_wide.columns else None
        if rc is not None:
            ax.text(xv, ys2[c], _fmt_raw(rc, team_wide.loc[team_id, rc], team_wide[rc]), transform=yax, ha="right",
                    va="center", fontsize=8, color=ink2, clip_on=False)
        if pd.isna(z[c]):
            ax.text(0.0, ys2[c], "n/a", ha="center", va="center", fontsize=7.5, color=muted, style="italic")
            continue
        zc = float(np.clip(z[c], -3, 3))
        ax.barh(ys2[c], zc, height=0.62, color=pos if zc >= 0 else neg, alpha=1.0 if abs(zc) >= 1 else 0.45, zorder=3)
        ax.text(zc + (0.08 if zc >= 0 else -0.08), ys2[c], f"{round(float(z[c]), 3) + 0.0:+.3f}",
                ha="left" if zc >= 0 else "right", va="center", fontsize=8, color=ink, zorder=4)
        if np.isfinite(zraw[c]):
            ax.scatter([float(np.clip(zraw[c], -3.3, 3.3))], [ys2[c]], marker="|", s=110, color=ink, linewidths=1.5,
                       zorder=5)
    ax.axvline(0, color=axis_colour, linewidth=0.9, zorder=2)
    ax.grid(axis="x", color=axis_colour, alpha=0.25, linewidth=0.6)
    ax.set_axisbelow(True)
    ax.set_xlim(-3.6, 3.6)
    ax.set_xticks([-3, -2, -1, 0, 1, 2, 3])
    ax.set_ylim(total2, 0)
    ax.set_yticks([ys2[c] for c in style_cols])
    ax.set_yticklabels([def_labels[c] for c in style_cols], fontsize=8, color=ink2, linespacing=0.95)
    ax.tick_params(axis="y", length=0)
    ax.tick_params(axis="x", labelsize=8, colors=muted)
    ax.set_xlabel(xlab, fontsize=8, color=muted)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(axis_colour)
 
    # ---- right: the lists, one under the other, then the formations ----
    if right_side:
        top3 = 1.07
        h3 = H - top3 - bottom_off
        ax = fig.add_axes(rect(x3, w3, h3, top=top3))
        ax.axis("off")
        ax.set_xlim(0, w3)
        ax.set_ylim(h3, 0)
        yy = 0.15
        wrap_at = int((w3 - 1.1) / 0.075)
        for L_ in lists:
            head = L_["head"] + (f"  ·  {L_['n_close']} close" if L_["n_close"] is not None else "")
            ax.text(w3 / 2, yy, head, ha="center", va="center", fontsize=11.5, fontweight="bold", color=ink)
            if L_["caption"]:
                ax.text(w3 / 2, yy + 0.3, L_["caption"], ha="center", va="center", fontsize=8, color=muted)
            ax.text(w3, yy + 0.58, "distance", ha="right", va="center", fontsize=7.5, color=muted)
            yy += LIST_HEAD
            if not L_["rows"]:
                ax.text(0.0, yy, "team not in this table", ha="left", va="center", fontsize=8.5, color=muted,
                        style="italic")
                yy += ROW_L
            for rank, nid, dist, is_close in L_["rows"]:
                colr = ink if is_close else muted
                nm = name_of(nid) + ("  ◆" if nid in shared else "")
                ax.text(0.0, yy, f"{rank}", ha="left", va="center", fontsize=9, color=muted)
                ax.text(0.3, yy, "\n".join(textwrap.wrap(nm, wrap_at)), ha="left", va="center", fontsize=9, color=colr,
                        linespacing=1.0)
                ax.text(w3, yy, f"{dist:.2f}", ha="right", va="center", fontsize=8.5, color=ink2 if is_close else muted)
                yy += ROW_L
            yy += LIST_END
        if form is not None or form_err:
            ax.text(w3 / 2, yy, "Formations", ha="center", va="center", fontsize=11.5, fontweight="bold", color=ink)
            ax.text(w3 / 2, yy + 0.3, "share of minutes", ha="center", va="center", fontsize=8, color=muted)
            yy += 0.65
            if form_err:
                ax.text(0.0, yy, form_err, ha="left", va="center", fontsize=8.5, color=muted, style="italic")
            else:
                rows_f, n_main, binary, b3_given = form
                cols_f = [plt.matplotlib.colors.to_rgba(slots[0], 1.0 - 0.65 * i / max(n_main - 1, 1))
                          for i in range(n_main)] + ["#d9d9d9"] * (len(rows_f) - n_main)
                for (lab, s, m), cf in zip(rows_f, cols_f):           # same colours and text as the formations legend
                    ax.scatter([0.1], [yy], marker="s", s=55, color=cf, linewidths=0)
                    ax.text(0.3, yy, f"{lab}   {s:.0%}" + (f"  ·  {m:,.0f} min" if m is not None else ""), ha="left",
                            va="center", fontsize=9, color=ink)
                    yy += ROW_L
                ax.text(0.0, yy, "   ·   ".join(f"{lab} {v:.0%}" for lab, v in binary), ha="left", va="center",
                        fontsize=9, color=ink2)
                if not b3_given:
                    ax.text(0.0, yy + 0.3, "Back three: formations with three or five at the back.", ha="left",
                            va="center", fontsize=7.5, color=muted)
 
    # ---- footnote ----
    foot = ["Left: the strip is the average share of minutes in each player type over all teams; the bar is this team's "
            "share minus that average (pale within 5 points)."]
    mid = "Middle: bars are z-scores"
    if has_adj:
        mid += f" of the strength-adjusted style columns against {ref_txt}"
    if mixed:
        mid += f"; rows marked ° have no adjusted version and are raw against {lg_name}"
    elif not has_adj:
        mid += f" against {lg_name}"
    mid += "; the number on the right is the raw value"
    if show_raw_tick and has_adj:
        mid += f"; | marks the raw z-score against {lg_name}, so its distance from the bar is what strength changes"
    foot.append(mid + " (pale within 1).")
    if lists and any(L_["n_close"] is not None for L_ in lists):
        foot.append(f"Right: distance in each table, 1 = a typical pair; 'close' = among the closest {close_share:.0%} of "
                    "pairs in that table, names in grey are outside it" + ("; ◆ = in more than one list." if shared else "."))
    elif shared:
        foot.append("Right: ◆ = in more than one list.")
    stripped = [s for s in label_strip if s]
    if stripped:
        foot.append("Labels leave out " + ", ".join(stripped) + ".")
    fig.text(L / W, 0.12 / H, "\n".join(textwrap.wrap(" ".join(foot), int(W * 16))), fontsize=7.5, color=muted,
             ha="left", va="bottom")
    return fig

def export_team_cards(team_wide, team_id_to_team, team_id_to_league, card_style_cols, team_ids=None,
                      fig_dir=player_fig_dir, position="teams", filename="team_card.png", dpi=200, **kwargs):
    """One card per team -> <...>/all_k/<Team>_<League>/team_card.png (folder name from your get_folder_name).
    kwargs go to team_card (e.g. D_squad=D_comp, D_style=D_style_adj, D_overall=D_adj, row_in=0.25, nb=..., nb_resid=...).
    A team that fails is reported at the end instead of stopping the run. Returns the saved paths in a list."""
    paths, failed = [], {}
    for t in (team_ids if team_ids is not None else team_wide.index):
        try:
            fig = team_card(team_wide, t, team_id_to_team, team_id_to_league, card_style_cols, **kwargs)
        except Exception as e:                                     # keep going, report at the end
            failed[t] = f"{type(e).__name__}: {e}"
            plt.close("all")
            continue
        out_dir = os.path.join(fig_dir, position, "all_k", get_folder_name(t, t, team_id_to_team, team_id_to_league))
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, filename)
        fig.savefig(path, dpi=dpi, bbox_inches="tight")
        plt.close(fig)
        paths.append(path)
    print(f"saved {len(paths)} team cards under {os.path.abspath(os.path.join(fig_dir, position, 'all_k'))}")
    for t, err in failed.items():
        print(f"  failed  {team_id_to_team.get(t, t)}: {err}")
    return paths

def _contents_page(entries, title="Team cards"):
    """First page of the PDF: teams grouped by league (one column per league), each row a link target.
    entries: [(team_id, name, league, page_number)] in page order. Returns (fig, [(team_id, rect in points)])."""
    leagues = list(dict.fromkeys(e[2] for e in entries))
    by_lg = {lg: [e for e in entries if e[2] == lg] for lg in leagues}
    COL, ROW = 4.3, 0.3
    n_rows = max(len(v) for v in by_lg.values())
    W = max(0.6 + len(leagues) * COL, 8.0)
    H = 1.75 + (n_rows + 0.5) * ROW + 0.4
    fig = plt.figure(figsize=(W, H))
    fig.set_facecolor(surface)
    fig.text(0.3 / W, 1 - 0.45 / H, title, fontsize=18, fontweight="bold", color=ink, va="center")
    fig.text(0.3 / W, 1 - 0.85 / H, "Click a team to open its card; every card has a link back to this page. "
             "Ordered by league, then team id.", fontsize=9.5, color=ink2, va="center")
    rects = []
    for j, lg in enumerate(leagues):
        x = 0.3 + j * COL
        y = H - 1.45
        fig.text(x / W, y / H, f"{lg} ({len(by_lg[lg])})", fontsize=11, fontweight="bold", color=ink, va="center")
        for i, (t, name, _, page) in enumerate(by_lg[lg]):
            yy = y - (i + 1) * ROW
            fig.text(x / W, yy / H, name, fontsize=9.5, color=slots[0], va="center")
            fig.text((x + COL - 0.4) / W, yy / H, f"p. {page}", fontsize=8.5, color=muted, va="center", ha="right")
            rects.append((t, (x * 72, (yy - ROW / 2) * 72, (x + COL - 0.35) * 72, (yy + ROW / 2) * 72)))
    return fig, rects

def _back_link(fig, text="← Back to contents"):
    """Draw the back link in the top-right corner of a page and return its rectangle in points."""
    W, H = fig.get_size_inches()
    t = fig.text(1 - 0.3 / W, 1 - 0.35 / H, text, fontsize=10.5, color=slots[0], ha="right", va="center")
    fig.canvas.draw()
    bb = t.get_window_extent(fig.canvas.get_renderer())
    k = 72 / fig.dpi                                              # display pixels -> PDF points
    return (bb.x0 * k - 4, bb.y0 * k - 4, bb.x1 * k + 4, bb.y1 * k + 4)
   
def team_cards_pdf(team_wide, team_id_to_team, team_id_to_league, card_style_cols, team_ids=None, nb=None,
                   nb_resid=None, fig_dir=player_fig_dir, position="teams", filename="team_cards.pdf", fit_page=False,
                   **kwargs):
    """Every team card as one page of a single PDF -> <...>/all_k/team_cards.pdf.
    Links and bookmarks open the top of the target page and keep the viewer's current zoom; fit_page=True makes them
    zoom to fit the whole page instead.
    Page 1 is a contents page: teams grouped by league, each name a link to its card. Every card has a
    '<- Back to contents' link in its top-right corner, and the PDF has bookmarks (league > team) in the sidebar.
    Teams are ordered by league, then team id (team_ids, if given, are ordered the same way).
    kwargs go to team_card (D_squad=..., D_style=..., fm=..., ...). A card that fails gets a placeholder page, so
    the page numbers stay right, and is reported at the end. The links need the pypdf package (pip install pypdf);
    without it the PDF is still made, with page numbers on the contents page but no clickable links.
    Returns the path."""
    out_dir = os.path.join(fig_dir, position, "all_k")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, filename)
    ids = list(team_ids) if team_ids is not None else [t for t in team_id_to_team if t in team_wide.index]
    ids = sorted(ids, key=lambda t: (str(team_id_to_league.get(t, "")), t))
    entries = [(t, str(team_id_to_team.get(t, t)), str(team_id_to_league.get(t, "")), i + 2) for i, t in enumerate(ids)]
    contents_rects, back_rects, failed = [], [], {}
    with PdfPages(path) as pdf:
        fig, contents_rects = _contents_page(entries)
        pdf.savefig(fig)                                          # no bbox_inches="tight": link positions must not move
        plt.close(fig)
        for t in ids:
            try:
                fig = team_card(team_wide, t, team_id_to_team, team_id_to_league, card_style_cols, nb=nb,
                                nb_resid=nb_resid, **kwargs)
            except Exception as e:                                # placeholder page keeps the page numbers right
                failed[t] = f"{type(e).__name__}: {e}"
                plt.close("all")
                fig = plt.figure(figsize=(11, 3))
                fig.set_facecolor(surface)
                fig.text(0.03, 0.6, str(team_id_to_team.get(t, t)), fontsize=17, fontweight="bold", color=ink)
                fig.text(0.03, 0.35, f"The card could not be made: {failed[t]}", fontsize=9.5, color=muted)
            back_rects.append(_back_link(fig))
            pdf.savefig(fig)
            plt.close(fig)
 
    try:                                                          # links and bookmarks
        from pypdf import PdfReader, PdfWriter
        from pypdf.annotations import Link
        from pypdf.generic import ArrayObject, NumberObject, NameObject, NullObject, FloatObject, Fit
    except ImportError:
        warnings.warn("pypdf is not installed (pip install pypdf): the PDF has no clickable links.", stacklevel=2)
    else:
        reader = PdfReader(path)
        writer = PdfWriter()
        for p in reader.pages:
            writer.add_page(p)
        no_border = ArrayObject([NumberObject(0), NumberObject(0), NumberObject(0)])
        page_of = {t: i + 1 for i, t in enumerate(ids)}            # 0-based page index of each card
 
        def top_of(target):
            return float(writer.pages[target].mediabox.top)
 
        def goto(on_page, rect, target):                          # link whose target is the page object (all viewers)
            a = writer.add_annotation(on_page, Link(rect=rect, target_page_index=target, border=no_border))
            ref = writer.pages[target].indirect_reference
            a[NameObject("/Dest")] = (ArrayObject([ref, NameObject("/Fit")]) if fit_page else   # zoom to fit the page
                                      ArrayObject([ref, NameObject("/XYZ"), NullObject(),       # top of the page,
                                                   FloatObject(top_of(target)), NullObject()]))  # zoom unchanged
 
        for t, rect in contents_rects:
            goto(0, rect, page_of[t])
        for i, rect in enumerate(back_rects):
            goto(i + 1, rect, 0)
        fit_of = lambda target: Fit.fit() if fit_page else Fit.xyz(left=None, top=top_of(target), zoom=None)
        writer.add_outline_item("Contents", 0, fit=fit_of(0))
        parents = {}
        for t, name, lg, page in entries:
            if lg not in parents:
                parents[lg] = writer.add_outline_item(lg, page - 1, is_open=False, fit=fit_of(page - 1))
            writer.add_outline_item(name, page - 1, parent=parents[lg], fit=fit_of(page - 1))
        tmp = path + ".tmp"
        with open(tmp, "wb") as fh:
            writer.write(fh)
        os.replace(tmp, path)
    print(f"saved {len(ids)} team cards (+ contents page) to {os.path.abspath(path)}")
    for t, err in failed.items():
        print(f"  failed  {team_id_to_team.get(t, t)}: {err}")
    return path

def league_mix(team_wide, cluster_col, league_col="league", group_colours=None, title=None, league_colours=None):
    """How the groups and the leagues overlap. cluster_col: the group of every team (teams without one are left out);
    league_col: its league. group_colours: {group: colour}, default your slots in group order.
    league_colours: {league: colour} for the bottom block, default slots 5-8 (index 4-7) in league-name order; more than four
    leagues wrap round to the first slots, so pass your own colours then."""
    if league_col not in team_wide.columns:
        raise KeyError(f"no '{league_col}' column in team_wide")
    df = team_wide[[cluster_col, league_col]].dropna()
    groups = sorted(df[cluster_col].unique())
    leagues = sorted(df[league_col].unique(), key=str)
    colours = group_colours or {}
    fill_g = {g: colours.get(g, slots[i % len(slots)]) for i, g in enumerate(groups)}
    cnt = pd.crosstab(df[league_col], df[cluster_col]).reindex(index=leagues, columns=groups, fill_value=0)
    n_all = int(cnt.to_numpy().sum())
    lcol = league_colours or {}
    fill_l = {lg: lcol.get(lg, slots[(4 + i) % len(slots)]) for i, lg in enumerate(leagues)}
    # ---- rows (y in row units, growing downwards) ----
    top_rows = [("All teams", n_all, cnt.sum(axis=0), None)] + \
               [(str(lg), int(cnt.loc[lg].sum()), cnt.loc[lg], lg) for lg in leagues]
    bot_rows = [(f"Cluster {int(g)}", int(cnt[g].sum()), cnt[g], g) for g in groups] + \
               [("All teams", n_all, cnt.sum(axis=1), None)]
    y = 0.0
    layout = []                                        # (kind, payload, y)
    layout.append(("head", "How each league's teams split between the groups", y)); y += 1.05
    for j, r in enumerate(top_rows):
        layout.append(("top", r, y)); y += 1.0 if j else 1.18
    y += 0.55
    layout.append(("head", "Which leagues each group's teams come from", y)); y += 1.0
    layout.append(("key", None, y)); y += 1.0
    for j, r in enumerate(bot_rows):
        y += 0.18 if j == len(bot_rows) - 1 else 0.0
        layout.append(("bot", r, y)); y += 1.0
    y_end = y - 0.4
 
    # ---- width of the row labels, measured, so the figure is only as wide as it needs to be ----
    def row_label(r):
        label, n, _, g = r
        return f"{label} ({n} teams)" if g is not None and g in groups else f"{label} ({n})"
    probe = plt.figure(figsize=(4, 1))
    rend = probe.canvas.get_renderer()
    lab_w = max(probe.text(0, 0, row_label(r), fontsize=8.5).get_window_extent(rend).width
                for kind_, r, _ in layout if kind_ in ("top", "bot")) / probe.dpi
    plt.close(probe)
    LEFT, AX_W, RIGHT, TOP, BOTTOM, ROW = max(1.5, lab_w + 0.5), 6.3, 0.35, 1.0, 0.75, 0.40
    plot_h = ROW * y_end
    W, H = LEFT + AX_W + RIGHT, TOP + plot_h + BOTTOM
    fig = plt.figure(figsize=(W, H))
    fig.set_facecolor(surface)
    ax = fig.add_axes([LEFT / W, BOTTOM / H, AX_W / W, plot_h / H])
    ax.set_facecolor(surface)
    ax.set_xlim(0, 1); ax.set_ylim(y_end, -0.3)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_xticklabels(["0%", "25%", "50%", "75%", "100%"], fontsize=8.5, color=muted)
    ax.set_yticks([]); ax.grid(axis="x"); ax.set_axisbelow(True)
    for s in ("top", "right", "left", "bottom"):
        ax.spines[s].set_visible(False)
 
    def draw_bar(yy, counts, fills, over=False):          # over: the dashed lines run across this bar, labels sit on top of them
        tot = float(counts.sum())
        left = 0.0
        for c, f in zip(counts.to_numpy(), fills):
            if c <= 0 or tot <= 0:
                continue
            w = c / tot
            ax.barh(yy, w, left=left, height=0.72, color=f, edgecolor=surface, linewidth=1.2, zorder=3)
            if w >= 0.055:
                ax.text(left + w / 2, yy, f"{w:.0%} ({int(c)})", ha="center", va="center", fontsize=7.5, zorder=7,
                        color=_text_on(plt.matplotlib.colors.to_hex(f)),
                        bbox=dict(boxstyle="square,pad=0.12", facecolor=f, edgecolor="none") if over else None)
            left += w
 
    all_edges = np.cumsum(cnt.sum(axis=0).to_numpy() / max(n_all, 1))[:-1]
    y_top_first = y_top_last = None
    for kind, r, yy in layout:
        if kind == "head":
            ax.text(0, yy, r, ha="left", va="center", fontsize=9.5, fontweight="bold", color=ink)
        elif kind == "top":
            label, n, counts, lg = r
            ax.text(-0.012, yy, row_label(r), ha="right", va="center", fontsize=8.5, color=ink if lg is None else ink2,
                    fontweight="bold" if lg is None else "normal")
            draw_bar(yy, counts, [fill_g[g] for g in groups], over=True)
            y_top_first = yy if y_top_first is None else y_top_first
            y_top_last = yy
        elif kind == "bot":
            label, n, counts, g = r
            if g is None:                                              # the All teams row
                ax.text(-0.012, yy, row_label(r), ha="right", va="center", fontsize=8.5, color=ink, fontweight="bold")
            else:                                                      # a group: its colour dot, then its name
                ax.text(-0.040, yy, row_label(r), ha="right", va="center", fontsize=8.5, color=ink2)
                ax.plot([-0.022], [yy], marker="o", markersize=7, color=fill_g[g], markeredgecolor=surface, linestyle="",
                        transform=ax.get_yaxis_transform(), clip_on=False)
            draw_bar(yy, counts, [fill_l[lg] for lg in leagues])
    # dashed lines: the all-teams split carried through every league bar
    for e in all_edges:
        ax.plot([e, e], [y_top_first + 0.36, y_top_last + 0.46], color=ink, linewidth=0.9, linestyle=(0, (3, 2)), alpha=0.65,
                zorder=6)
 
    # key for the neutral league shades, written after the figure is laid out so the widths are real
    fig.canvas.draw()
    rend = fig.canvas.get_renderer()
    key_y = [yy for k_, _, yy in layout if k_ == "key"][0]
    px = lambda x: ax.transData.transform((x, 0))[0]
    dx = lambda p: ax.transData.inverted().transform((p, 0))[0]
    x_px = px(0)
    for lg in leagues:
        sw = ax.add_patch(Rectangle((dx(x_px), key_y - 0.3), dx(x_px + 0.16 * fig.dpi) - dx(x_px), 0.6, facecolor=fill_l[lg],
                                    edgecolor="none", clip_on=False))
        t = ax.text(dx(x_px + 0.22 * fig.dpi), key_y, str(lg), ha="left", va="center", fontsize=8, color=ink2)
        x_px += 0.22 * fig.dpi + t.get_window_extent(rend).width + 0.25 * fig.dpi
 
    # ---- title and reading notes ----
    ttl = title or f"League mix per group (k = {len(groups)})"
    t_title = fig.text(0.15 / W, 1 - 0.15 / H, ttl, ha="left", va="top", fontsize=15, fontweight="bold", color=ink)
    bb = t_title.get_window_extent(rend)
    room = W * fig.dpi - bb.x0 - 0.15 * fig.dpi
    if bb.width > room:
        t_title.set_fontsize(max(10.0, 15 * room / bb.width))
    fig.text(0.15 / W, 1 - 0.58 / H, "Labels: share of the bar (number of teams).  Dashed lines carry the all-teams split through "
             "every league: a league on the lines has no group bias.", fontsize=8.5, color=ink2, va="center")
    return fig

def export_league_mix(team_wide, cluster_col, n_clusters, fig_dir=player_fig_dir, position="teams", dpi=200, **kwargs):
    """-> <...>/k<n>/league_mix.png. kwargs go to league_mix (league_col, group_colours, title). Returns the path in a list."""
    out_dir = os.path.join(fig_dir, position, f"k{n_clusters}")
    os.makedirs(out_dir, exist_ok=True)
    fig = league_mix(team_wide, cluster_col, **kwargs)
    path = os.path.join(out_dir, "league_mix.png")
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    print(f"saved league mix (k = {n_clusters}) to {os.path.abspath(path)}")
    return [path]

def close_team_strip(D, team_wide, cluster_col, team_id_to_team, group_colours=None, close_share=0.10, max_per_row=None,
                     normalize=True, label_size=6.6, title=None):
    """One row per team: its lead for its own group (filled marker) and every team close to it in D (open markers, scored on
    the row team's group), grouped by cluster.
    D: team x team distance matrix (DataFrame indexed by team id, e.g. D_style_adj).
    cluster_col: the group of every team in team_wide; the similarity columns sim_cluster_<g>_k<k> (k = number of groups)
    must be in team_wide too.
    team_id_to_team: {team_id: team name}.
    group_colours: {group: colour}, default your group_colours_list in group order; markers are your group_markers.
    close_share: a pair counts as close when its distance is among this share of all pairs (0.10 = the closest 10%).
    max_per_row: draw at most this many close teams per row (the closest ones); the counts on the right still include all.
    normalize: divide D by its median pair distance, so a typical pair = 1 (only changes the number quoted in the footnote)."""
    if not isinstance(D, pd.DataFrame):
        raise TypeError("D must be a DataFrame indexed by team id (rows and columns = teams)")
    if not 0 < close_share < 1:
        raise ValueError("close_share must be between 0 and 1 (e.g. 0.10 = the closest 10% of pairs)")
    ids = [t for t in D.index if t in team_wide.index and pd.notna(team_wide.loc[t, cluster_col]) and t in D.columns]
    groups = sorted(team_wide.loc[ids, cluster_col].unique())
    K = len(groups)
    if K < 2:
        raise ValueError("need at least 2 groups")
    sim_cols = [f"sim_cluster_{int(g)}_k{K}" for g in groups]
    missing = [c for c in sim_cols if c not in team_wide.columns]
    if missing:
        raise KeyError(f"similarity columns not in team_wide: {missing} (expected sim_cluster_<g>_k{K} for every group)")
    no_sim = [t for t in ids if not np.isfinite(team_wide.loc[t, sim_cols].to_numpy(float)).all()]
    dropped = [t for t in D.index if t not in ids] + no_sim
    ids = [t for t in ids if t not in no_sim]
    if dropped:
        warnings.warn(f"{len(dropped)} team(s) in D left out (not in team_wide, no group or missing similarity scores): "
                      f"{dropped[:6]}{' ...' if len(dropped) > 6 else ''}", stacklevel=2)
    n = len(ids)
    if n < 3:
        raise ValueError("need at least 3 teams that are in D and have a group and similarity scores")
    M = D.loc[ids, ids].to_numpy(float)
    if not np.isfinite(M).all():
        raise ValueError("D has missing or infinite distances among the teams drawn")
    M = (M + M.T) / 2
    np.fill_diagonal(M, 0.0)
    off = np.triu_indices(n, 1)
    if normalize:
        M = M / np.median(M[off])
    labels = team_wide.loc[ids, cluster_col]
    gi = np.array([groups.index(g) for g in labels])
    S = team_wide.loc[ids, sim_cols].to_numpy(float)
    name_of = lambda t: str(team_id_to_team.get(t, t))
    lim_style = min(len(group_markers), len(group_colours_list))
    if K > lim_style and not group_colours:
        warnings.warn(f"{K} groups but group_markers / group_colours_list have {lim_style} entries: the extra "
                      "groups reuse an earlier marker and colour. Extend the lists (or pass group_colours).", stacklevel=2)
    gcol = group_colours or {}
    colour = [gcol.get(g, group_colours_list[i % len(group_colours_list)]) for i, g in enumerate(groups)]
    marker = [group_markers[i % len(group_markers)] for i in range(K)]
 
    # ---- lead of every team for every group; L[i, j] = lead of team j for team i's group ----
    lead_g = np.column_stack([S[:, g] - np.delete(S, g, axis=1).max(axis=1) for g in range(K)])     # n x K
    L = lead_g[:, gi].T
    own = np.diag(L).copy()
    cut = float(np.quantile(M[off], close_share))
    close = [c[np.argsort(M[i, c])] for i, c in
             ((i, np.where((M[i] <= cut) & (np.arange(n) != i))[0]) for i in range(n))]          # closest first
    d_lo = float(M[off].min())
 
    # ---- rows: a header per group, then its teams, firmest first ----
    rows = []
    for g in range(K):
        m = np.where(gi == g)[0]
        rows += [("head", g, len(m))] + [("team", i) for i in m[np.argsort(-own[m], kind="stable")]]
    shown = [c[:max_per_row] if max_per_row else c for c in close]
    vals = np.r_[own, np.concatenate([L[i, c] for i, c in enumerate(shown)] or [np.empty(0)])]
    span = max(np.ptp(vals), 0.1)
    lo, hi = min(vals.min(), -0.05) - 0.06 * span, max(vals.max(), 0.05) + 0.04 * span
 
    # ---- summary numbers ----
    pairs = [(i, j) for i, j in zip(*off) if M[i, j] <= cut]
    n_same = sum(gi[i] == gi[j] for i, j in pairs)
    sizes = np.bincount(gi, minlength=K)
    chance = (sizes * (sizes - 1) / 2).sum() / len(off[0])
    gap_close = [abs(L[i, i] - L[i, j]) for i in range(n) for j in close[i]]
    gap_any = np.abs(own[:, None] - L)[~np.eye(n, dtype=bool)]
    n_none = sum(len(c) == 0 for c in close)
    n_left = int((own < 0).sum())
    capped = bool(max_per_row) and any(len(c) > max_per_row for c in close)
 
    # ---- figure: sizes in inches ----
    from matplotlib.textpath import TextPath
    from matplotlib.font_manager import FontProperties
    fp = FontProperties(family=plt.rcParams["font.family"])
    text_w = lambda s, size: TextPath((0, 0), s, size=size, prop=fp).get_extents().width / 72
    right_txt = {i: (f"{len(close[i])} close" + (f" · {int((gi[close[i]] != gi[i]).sum())} other group"
                                                 if (gi[close[i]] != gi[i]).any() else "")) if len(close[i]) else
                 "no close team" for i in range(n)}
    ROW = 0.165
    notes = [f"Close = among the closest {close_share:.0%} of all {len(off[0])} team pairs (distance {cut:.2f} or less"
             + ("; 1 = a typical pair)." if normalize else ").")
             + (f" {n_none} team{'s have' if n_none != 1 else ' has'} no close team." if n_none else "")
             + (f" Rows show at most the {max_per_row} closest; the counts on the right include all." if capped else ""),
             f"Close pairs in the same group: {n_same} of {len(pairs)} ({n_same / max(len(pairs), 1):.0%}; "
             f"{chance:.0%} if the groups were random). Typical gap in lead between close teams: "
             f"{np.median(gap_close) if gap_close else float('nan'):.2f} (any two teams: {np.median(gap_any):.2f})."]
    if n_left:
        notes.append(f"{n_left} team{'s sit' if n_left != 1 else ' sits'} left of the border: its similarity scores favour "
                     "another group than the one it is assigned to.")
    LEFT = 0.25 + max(text_w(name_of(t), label_size) for t in ids)
    RIGHT = 0.25 + max(text_w(s, 6.5) for s in right_txt.values())
    AX_W, TOP = 6.4, 1.35
    BOTTOM = 0.75 + 0.18 * len(notes)
    AX_H = ROW * len(rows) + 0.25
    W, H = LEFT + AX_W + RIGHT, TOP + AX_H + BOTTOM
    fig = plt.figure(figsize=(W, H))
    fig.set_facecolor(surface)
    ax = fig.add_axes([LEFT / W, BOTTOM / H, AX_W / W, AX_H / H])
    ax.set_facecolor(surface)
    ax.set_xlim(lo, hi)
    ax.set_ylim(-len(rows) + 0.4, 0.75)
    ax.axvline(0, color=muted, linewidth=1, linestyle=(0, (3, 3)), zorder=0)
    yax = ax.get_yaxis_transform()                         # x in axes fraction, y in data
    yt, yl = [], []
    for r, row in enumerate(rows):
        y = -r
        if row[0] == "head":
            g = row[1]
            ax.scatter([0.008], [y - 0.08], s=34, marker=marker[g], color=colour[g], edgecolors=surface, linewidths=0.6,
                       transform=yax, clip_on=False, zorder=3)
            ax.text(0.022, y - 0.08, f"Cluster {int(groups[g])}  ({row[2]} teams)", transform=yax, fontsize=9,
                    fontweight="bold", color=colour[g], va="center")
            continue
        i = row[1]
        c = shown[i]
        if len(c):
            xs = L[i, c]
            ax.plot([min(xs.min(), own[i]), max(xs.max(), own[i])], [y, y], color="#d3d2cb", linewidth=1.0, zorder=1)
            size = 12 + 30 * np.clip((cut - M[i, c]) / max(cut - d_lo, 1e-9), 0, 1)
            for g in np.unique(gi[c]):
                m = gi[c] == g
                ax.scatter(xs[m], np.full(m.sum(), y), s=size[m], marker=marker[g], facecolors=surface,
                           edgecolors=colour[g], linewidths=1.2, zorder=2)
        ax.scatter([own[i]], [y], s=34, marker=marker[gi[i]], color=colour[gi[i]], edgecolors=surface, linewidths=0.6,
                   zorder=3)
        other = len(close[i]) and (gi[close[i]] != gi[i]).any()
        ax.text(1.012, y, right_txt[i], transform=yax, fontsize=6.5, color=ink if other else muted, va="center")
        yt.append(y)
        yl.append(name_of(ids[i]))
    ax.set_yticks(yt, yl, fontsize=label_size, color=ink2)
    ax.tick_params(axis="y", length=0, pad=3)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(muted)
    ax.tick_params(axis="x", colors=ink2, labelsize=7.5)
    ax.set_xlabel("Lead for the row team's group: similarity share for that group minus the best other group (0.10 = 10 points)",
                  fontsize=8.5, color=ink2)
    ax.text(0, 0.8, "group border", fontsize=7, color=muted, ha="center", va="bottom")
    ax.text(1.012, 0.8, "teams close to it", transform=yax, fontsize=7, color=muted, va="bottom")
 
    # ---- title, reading note, key, footnotes ----
    fig.canvas.draw()
    rend = fig.canvas.get_renderer()
    ttl = title or f"Each team and the teams close to it: group and similarity (k = {K})"
    t_title = fig.text(0.15 / W, 1 - 0.15 / H, ttl, ha="left", va="top", fontsize=15, fontweight="bold", color=ink)
    bb = t_title.get_window_extent(rend)
    room = W * fig.dpi - bb.x0 - 0.15 * fig.dpi
    if bb.width > room:
        t_title.set_fontsize(max(10.0, 15 * room / bb.width))
    fig.text(0.15 / W, 1 - 0.55 / H, "Position = how far a team's similarity to its group leads the next group (0 = the border). "
             "Open markers = teams close to it in style, scored on the same group.", fontsize=8.5, color=ink2, va="center")
    key = [Line2D([0], [0], marker="o", linestyle="", markersize=6, color=muted, markeredgecolor=surface, label="team"),
           Line2D([0], [0], marker="o", linestyle="", markersize=5.5, markerfacecolor=surface, markeredgecolor=muted,
                  markeredgewidth=1.2, label="a team close to it (colour and marker = its group; bigger = closer)")]
    fig.legend(handles=key, loc="center left", bbox_to_anchor=(0.15 / W, 1 - 0.92 / H), ncol=2, frameon=False, fontsize=8,
               labelcolor=ink2)
    for k_, txt in enumerate(notes):
        fig.text(0.15 / W, (0.15 + 0.18 * (len(notes) - 1 - k_)) / H, txt, fontsize=7.5, color=muted, va="center")
    return fig

def export_close_team_strip(D, team_wide, cluster_col, n_clusters, team_id_to_team, fig_dir=player_fig_dir,
                            position="teams", dpi=200, **kwargs):
    """-> <...>/k<n>/close_teams.png. kwargs go to close_team_strip. Returns the path in a list."""
    out_dir = os.path.join(fig_dir, position, f"k{n_clusters}")
    os.makedirs(out_dir, exist_ok=True)
    fig = close_team_strip(D, team_wide, cluster_col, team_id_to_team, **kwargs)
    path = os.path.join(out_dir, "close_teams.png")
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    print(f"saved close-teams strip (k = {n_clusters}) to {os.path.abspath(path)}")
    return [path]

def similarity_gap_vs_distance(D, team_wide, cluster_col, team_id_to_team, group_colours=None, close_share=0.10,
                               normalize=True, label_pairs=0, title=None):
    """Every pair of teams: distance in D (across) against the gap between their similarity scores (up).
    D: team x team distance matrix (DataFrame indexed by team id, e.g. D_style_adj).
    cluster_col: the group of every team in team_wide; sim_cluster_<g>_k<k> (k = number of groups) must be in team_wide too.
    team_id_to_team: {team_id: team name} (used to name pairs when label_pairs > 0).
    group_colours: {group: colour}, default your group_colours_list in group order.
    close_share: where to draw the "close" line (0.10 = the closest 10% of pairs, as on the close-teams strip).
    label_pairs: name this many close pairs with the biggest similarity gap (close in style, different scores); 0 = none."""
    if not isinstance(D, pd.DataFrame):
        raise TypeError("D must be a DataFrame indexed by team id (rows and columns = teams)")
    if not 0 < close_share < 1:
        raise ValueError("close_share must be between 0 and 1 (e.g. 0.10 = the closest 10% of pairs)")
    ids = [t for t in D.index if t in team_wide.index and pd.notna(team_wide.loc[t, cluster_col]) and t in D.columns]
    groups = sorted(team_wide.loc[ids, cluster_col].unique())
    K = len(groups)
    if K < 2:
        raise ValueError("need at least 2 groups")
    sim_cols = [f"sim_cluster_{int(g)}_k{K}" for g in groups]
    missing = [c for c in sim_cols if c not in team_wide.columns]
    if missing:
        raise KeyError(f"similarity columns not in team_wide: {missing} (expected sim_cluster_<g>_k{K} for every group)")
    no_sim = [t for t in ids if not np.isfinite(team_wide.loc[t, sim_cols].to_numpy(float)).all()]
    dropped = [t for t in D.index if t not in ids] + no_sim
    ids = [t for t in ids if t not in no_sim]
    if dropped:
        warnings.warn(f"{len(dropped)} team(s) in D left out (not in team_wide, no group or missing similarity scores): "
                      f"{dropped[:6]}{' ...' if len(dropped) > 6 else ''}", stacklevel=2)
    n = len(ids)
    if n < 6:
        raise ValueError("need at least 6 teams that are in D and have a group and similarity scores")
    M = D.loc[ids, ids].to_numpy(float)
    if not np.isfinite(M).all():
        raise ValueError("D has missing or infinite distances among the teams drawn")
    M = (M + M.T) / 2
    np.fill_diagonal(M, 0.0)
    iu = np.triu_indices(n, 1)
    if normalize:
        M = M / np.median(M[iu])
    S = team_wide.loc[ids, sim_cols].to_numpy(float)
    rs = S.sum(axis=1)
    if np.abs(rs - 1).max() > 0.02:                        # shares should add up to 1; rescale so the gap stays on a 0-1 scale
        warnings.warn(f"similarity scores do not add up to 1 per team (from {rs.min():.2f} to {rs.max():.2f}); "
                      "rescaled to shares for the gap.", stacklevel=2)
        S = S / rs[:, None]
    gi = np.array([groups.index(g) for g in team_wide.loc[ids, cluster_col]])
    name_of = lambda t: str(team_id_to_team.get(t, t))
    gcol = group_colours or {}
    colour = [gcol.get(g, group_colours_list[i % len(group_colours_list)]) for i, g in enumerate(groups)]
    if K > len(group_colours_list) and not group_colours:
        warnings.warn(f"{K} groups but group_colours_list has {len(group_colours_list)} entries: the extra groups reuse an "
                      "earlier colour. Extend the list (or pass group_colours).", stacklevel=2)
 
    d = M[iu]
    gap = 0.5 * np.abs(S[iu[0]] - S[iu[1]]).sum(axis=1)
    same = gi[iu[0]] == gi[iu[1]]
    cut = float(np.quantile(d, close_share))
    edges = np.quantile(d, np.linspace(0, 1, 11))
    band = np.clip(np.searchsorted(edges, d, side="right") - 1, 0, 9)      # 10 distance bands, same number of pairs each
    mid = np.array([np.median(d[band == b]) for b in range(10)])
    med = np.array([np.median(gap[band == b]) for b in range(10)])
    q1 = np.array([np.quantile(gap[band == b], 0.25) for b in range(10)])
    q3 = np.array([np.quantile(gap[band == b], 0.75) for b in range(10)])
    typical = float(np.median(gap))
    close = d <= cut
    n_close_far = int((gap[close] > typical).sum())
 
    fig, ax = plt.subplots(figsize=(9.4, 6.8))
    fig.set_facecolor(surface)
    ax.set_facecolor(surface)
    ax.scatter(d[~same], gap[~same], s=10, color="#a9a8a0", alpha=0.5, linewidths=0, zorder=2)
    for g in range(K):
        m = same & (gi[iu[0]] == g)
        ax.scatter(d[m], gap[m], s=10, color=colour[g], alpha=0.6, linewidths=0, zorder=2)
    ax.fill_between(mid, q1, q3, color=ink, alpha=0.08, linewidth=0, zorder=1)
    ax.plot(mid, med, color=ink, linewidth=2, zorder=3)
    ax.axvline(cut, color=muted, linewidth=1, linestyle=(0, (3, 3)), zorder=0)
    ytop = max(gap.max(), 0.05) * 1.06
    ax.set_ylim(-0.02 * ytop, ytop)
    ax.text(cut, ytop, f" ← close pairs (closest {close_share:.0%})", color=muted, fontsize=7.5, ha="left", va="top")
    if label_pairs:                                        # names stacked in the empty top-left corner, a thin line to each pair
        idx = np.where(close)[0]
        for r, p in enumerate(idx[np.argsort(-gap[idx])][:int(label_pairs)]):
            a, b = ids[iu[0][p]], ids[iu[1][p]]
            ax.scatter([d[p]], [gap[p]], s=34, facecolors="none", edgecolors=ink, linewidths=1, zorder=4)
            ax.annotate(f"{name_of(a)} – {name_of(b)}", (d[p], gap[p]), xytext=(0.015, 0.90 - 0.045 * r),
                        textcoords="axes fraction", fontsize=7, color=ink, va="center", zorder=5,
                        arrowprops=dict(arrowstyle="-", color=muted, linewidth=0.6, shrinkA=2, shrinkB=3))
        ax.text(0.015, 0.95, "close in style, different scores:", transform=ax.transAxes, fontsize=7, color=muted,
                va="center")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(muted)
    ax.tick_params(colors=ink2, labelsize=8)
    ax.set_xlabel("Distance between the two teams" + (" (1 = a typical pair; further right = play less alike)" if normalize
                                                       else " (further right = play less alike)"), fontsize=9, color=ink2)
    ax.set_ylabel("Similarity gap (share of similarity that differs)" if K > 2 else
                  f"Similarity gap (difference in Cluster {int(groups[0])} share)", fontsize=9, color=ink2)
    handles = [Line2D([0], [0], marker="o", linestyle="", markersize=5, color=colour[g],
                      label=f"both Cluster {int(groups[g])} ({int((same & (gi[iu[0]] == g)).sum())} pairs)") for g in range(K)]
    handles += [Line2D([0], [0], marker="o", linestyle="", markersize=5, color="#a9a8a0",
                       label=f"different clusters ({int((~same).sum())} pairs)"),
                Line2D([0], [0], color=ink, linewidth=2, label="typical gap at that distance"),
                plt.Rectangle((0, 0), 1, 1, color=ink, alpha=0.08, linewidth=0, label="middle half of pairs")]
    ax.legend(handles=handles, loc="lower left", bbox_to_anchor=(0, 1.0), ncol=3, frameon=False, fontsize=8,
              labelcolor=ink2)
    key_rows = -(-len(handles) // 3)
 
    W, H = fig.get_size_inches()
    fig.canvas.draw()
    rend = fig.canvas.get_renderer()
    ttl = title or f"Do teams that play more alike have more similar similarity scores? (k = {K})"
    t_title = fig.text(0.15 / W, 1 - 0.15 / H, ttl, ha="left", va="top", fontsize=15, fontweight="bold", color=ink)
    bb = t_title.get_window_extent(rend)
    room = W * fig.dpi - bb.x0 - 0.15 * fig.dpi
    if bb.width > room:
        t_title.set_fontsize(max(10.0, 15 * room / bb.width))
    fig.text(0.15 / W, 1 - 0.55 / H, f"Every pair of teams once ({len(d)} pairs). Higher = their similarity scores lean "
             "further apart.", fontsize=8.5, color=ink2, va="center")
    notes = [f"Typical gap: closest tenth of pairs {med[0]:.2f} (middle half {q1[0]:.2f}–{q3[0]:.2f}), "
             f"furthest tenth {med[-1]:.2f}, all pairs {typical:.2f}. {n_close_far} of {int(close.sum())} close pairs "
             "still differ by more than a typical pair.",
             "Gap = share of similarity that would have to move to turn one team's scores into the other's (0 = same leaning, "
             "1 = opposite)" + (f"; at k = 2 the difference in Cluster {int(groups[0])} share = half the gap in lead on the "
                                "close-teams strip." if K == 2 else ".")]
    for k_, txt in enumerate(notes):
        fig.text(0.15 / W, (0.15 + 0.18 * (len(notes) - 1 - k_)) / H, txt, fontsize=7.5, color=muted, va="center")
    fig.subplots_adjust(left=0.08, right=0.98, top=1 - (0.85 + 0.2 * key_rows) / H, bottom=0.95 / H)
    return fig
 
def export_similarity_gap_vs_distance(D, team_wide, cluster_col, n_clusters, team_id_to_team, fig_dir=player_fig_dir,
                                      position="teams", dpi=200, **kwargs):
    """-> <...>/k<n>/similarity_gap_vs_distance.png. kwargs go to similarity_gap_vs_distance. Returns the path in a list."""
    out_dir = os.path.join(fig_dir, position, f"k{n_clusters}")
    os.makedirs(out_dir, exist_ok=True)
    fig = similarity_gap_vs_distance(D, team_wide, cluster_col, team_id_to_team, **kwargs)
    path = os.path.join(out_dir, "similarity_gap_vs_distance.png")
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    print(f"saved similarity gap vs distance (k = {n_clusters}) to {os.path.abspath(path)}")
    return [path]

_k_cols = ("kmeans_2_cluster", "kmeans_3_cluster", "kmeans_4_cluster")

def team_paths_table(team_wide, cluster_cols=_k_cols, margin_cut=0.10):
    """One row per team (teams with a group in every column): group_k<k>, lead_k<k>, between_k<k> (lead < margin_cut)
    and moves_k<k> (from the second column on: the team's new group mostly holds teams that were in another group at the
    previous k). Columns in cluster_cols order; k = number of groups in each column."""
    cluster_cols = list(cluster_cols)
    missing = [c for c in cluster_cols if c not in team_wide.columns]
    if missing:
        raise KeyError(f"cluster columns not in team_wide: {missing}")
    tw = team_wide.dropna(subset=cluster_cols)
    if len(tw) < len(team_wide):
        warnings.warn(f"{len(team_wide) - len(tw)} team(s) without a group in every column left out", stacklevel=2)
    out = pd.DataFrame(index=tw.index)
    ks = []
    for j, col in enumerate(cluster_cols):
        lab = tw[col].astype(int)
        groups = sorted(lab.unique())
        k = len(groups)
        ks.append(k)
        out[f"group_k{k}"] = lab
        sim_cols = [f"sim_cluster_{g}_k{k}" for g in groups]
        if all(c in tw.columns for c in sim_cols):
            S = tw[sim_cols].to_numpy(float)
            gi = np.array([groups.index(g) for g in lab])
            S_other = S.copy()
            S_other[np.arange(len(S)), gi] = -np.inf
            out[f"lead_k{k}"] = S[np.arange(len(S)), gi] - S_other.max(axis=1)
        else:
            warnings.warn(f"no {sim_cols[0]}, ... columns: no lead shown for k = {k}", stacklevel=2)
            out[f"lead_k{k}"] = np.nan
        out[f"between_k{k}"] = out[f"lead_k{k}"] < margin_cut
        if j > 0:
            prev = out[f"group_k{ks[j - 1]}"]
            parent = {g: int(prev[lab == g].value_counts().sort_index().idxmax()) for g in groups}   # ties -> lower number
            out[f"moves_k{k}"] = lab.map(parent) != prev
    if len(set(ks)) < len(ks):
        raise ValueError(f"two cluster columns have the same number of groups ({ks}); give one column per k")
    return out
 
def team_paths(team_wide, team_id_to_team, cluster_cols=_k_cols, group_colours=None, margin_cut=0.10, label_size=7,
               title=None):
    """One row per team, one cell per k: group colour, group number and lead; pale = between groups; outlined = moves.
    team_id_to_team: {team_id: team name}. group_colours: {group: colour}, default your group_colours_list in group order
    (the same colour for the same group NUMBER at every k, as in your per-k figures)."""
    tab = team_paths_table(team_wide, cluster_cols, margin_cut)
    ks = [int(c.split("_k")[1]) for c in tab.columns if c.startswith("group_k")]
    k_max = max(ks)
    if k_max > len(group_colours_list) and not group_colours:
        warnings.warn(f"{k_max} groups but group_colours_list has {len(group_colours_list)} entries: the extra groups reuse "
                      "an earlier colour. Extend the list (or pass group_colours).", stacklevel=2)
    gcol = group_colours or {}
    colour_of = lambda g: gcol.get(g, group_colours_list[int(g) % len(group_colours_list)])
    to_rgb = plt.matplotlib.colors.to_rgb
    pale = lambda c: tuple(0.38 * a + 0.62 * b for a, b in zip(to_rgb(c), to_rgb(surface)))
    name_of = lambda t: str(team_id_to_team.get(t, t))
 
    # order: k=2 group, then the path, then the k=2 lead (firmest first)
    k0 = ks[0]
    sort_cols = [f"group_k{k}" for k in ks]
    tab = tab.assign(_lead0=-tab[f"lead_k{k0}"].fillna(0)).sort_values(sort_cols + ["_lead0"], kind="stable")
    rows = []
    for g in sorted(tab[f"group_k{k0}"].unique()):
        sub = tab[tab[f"group_k{k0}"] == g]
        rows += [("head", g, len(sub))] + [("team", t) for t in sub.index]
 
    def note_of(t):
        mv = [k for k in ks[1:] if tab.loc[t, f"moves_k{k}"]]
        if mv:
            return "moves at " + " and ".join(f"k={k}" for k in mv), True
        if all(tab.loc[t, f"between_k{k}"] for k in ks):
            return "between groups at every k", False
        return "", False
 
    notes = {t: note_of(t) for t in tab.index}
 
    # ---- figure: sizes in inches ----
    from matplotlib.textpath import TextPath
    from matplotlib.font_manager import FontProperties
    fp = FontProperties(family=plt.rcParams["font.family"])
    text_w = lambda s, size: TextPath((0, 0), s, size=size, prop=fp).get_extents().width / 72 if s.strip() else 0.0
    ROW, CELL, GAP = 0.19, 0.95, 0.08
    LEFT = 0.25 + max(text_w(name_of(t), label_size) for t in tab.index)
    RIGHT = 0.3 + max([text_w(s, 7) for s, _ in notes.values()] + [1.2])
    body_w = len(ks) * CELL + (len(ks) - 1) * GAP
    W = max(LEFT + body_w + RIGHT, 7.6)
    # footnotes, wrapped to the figure width
    import textwrap
    pale_n = ", ".join(f"k={k}: {int(tab[f'between_k{k}'].sum())}" for k in ks)
    mv_txt = []
    for k in ks[1:]:
        names_k = [name_of(t) for t in tab.index if tab.loc[t, f"moves_k{k}"]]
        if names_k:
            mv_txt.append(f"k={k}: {', '.join(names_k)}")
    foot = [f"Pale: lead under {margin_cut:.2f}, i.e. between groups ({pale_n} teams).",
            "Outlined: the team moves - its new group's teams were mostly in another group at the previous k"
            + (f" ({'; '.join(mv_txt)})." if mv_txt else " (no team moves).")]
    per_line = max(40, int((W - 0.3) * 72 / (7.5 * 0.52)))
    foot_lines = [ln for s in foot for ln in textwrap.wrap(s, per_line)]
    TOP, BOTTOM = 1.55, 0.45 + 0.17 * len(foot_lines)
    H = TOP + ROW * (len(rows) + 0.5) + BOTTOM
    fig = plt.figure(figsize=(W, H))
    fig.set_facecolor(surface)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.axis("off")
    x0 = LEFT
    xs = [x0 + j * (CELL + GAP) for j in range(len(ks))]
    y = H - TOP
    # column headers: k and the groups at that k with their sizes
    for j, k in enumerate(ks):
        ax.text(xs[j] + CELL / 2, y + 0.42, f"k = {k}", ha="center", va="bottom", fontsize=9, fontweight="bold", color=ink)
        counts = tab[f"group_k{k}"].value_counts().sort_index()
        n = len(counts)
        sw = CELL / n
        for q, (g, c) in enumerate(counts.items()):
            ax.add_patch(Rectangle((xs[j] + q * sw + 0.01, y + 0.17), sw - 0.02, 0.2, facecolor=colour_of(g), edgecolor="none"))
            ax.text(xs[j] + (q + 0.5) * sw, y + 0.27, f"{int(g)}:{int(c)}", ha="center", va="center", fontsize=6,
                    color="white")
    ax.text(xs[-1] + CELL + 0.2, y + 0.27, "group : teams", fontsize=6.5, color=muted, va="center")
    for row in rows:
        y -= ROW
        if row[0] == "head":
            g = row[1]
            ax.text(0.15, y - ROW * 0.35, f"Cluster {int(g)} at k = {k0}  ({row[2]} teams)", fontsize=8.5,
                    fontweight="bold", color=colour_of(g), va="center")
            ax.plot([0.15, W - 0.15], [y + ROW * 0.12, y + ROW * 0.12], color=muted, linewidth=0.5, alpha=0.5)
            continue
        t = row[1]
        ax.text(LEFT - 0.12, y - ROW * 0.45, name_of(t), ha="right", va="center", fontsize=label_size, color=ink2)
        for j, k in enumerate(ks):
            g = int(tab.loc[t, f"group_k{k}"])
            lead = tab.loc[t, f"lead_k{k}"]
            weak = bool(tab.loc[t, f"between_k{k}"])
            moved = j > 0 and bool(tab.loc[t, f"moves_k{k}"])
            face = pale(colour_of(g)) if weak else colour_of(g)
            ax.add_patch(Rectangle((xs[j], y - ROW * 0.92), CELL, ROW * 0.84, facecolor=face,
                                   edgecolor=ink if moved else "none", linewidth=1.4 if moved else 0, zorder=2))
            txt = f"{g}" + (f"   {lead:.2f}" if np.isfinite(lead) else "")
            ax.text(xs[j] + CELL / 2, y - ROW * 0.5, txt, ha="center", va="center", fontsize=6.6,
                    color=ink if weak else "white", fontweight="bold" if moved else "normal", zorder=3)
        s, is_move = notes[t]
        if s:
            ax.text(xs[-1] + CELL + 0.2, y - ROW * 0.5, s, fontsize=7, va="center", color=ink if is_move else muted)
 
    # ---- title, reading note, footnotes ----
    ttl = title or "How each team's group changes as k grows"
    fig.text(0.15 / W, 1 - 0.15 / H, ttl, ha="left", va="top", fontsize=15, fontweight="bold", color=ink)
    fig.text(0.15 / W, 1 - 0.55 / H, "Each cell: the team's group at that k and its lead (similarity to its group minus the next "
             "group; 0.10 = 10 points).", fontsize=8.5, color=ink2, va="center")
    fig.text(0.15 / W, 1 - 0.75 / H, "Colours follow each k's own numbering, as in the other figures: the same colour at two k "
             "is not the same group.", fontsize=8.5, color=ink2, va="center")
    for q, s in enumerate(foot_lines):
        fig.text(0.15 / W, (0.15 + 0.17 * (len(foot_lines) - 1 - q)) / H, s, fontsize=7.5, color=muted, va="center")
    return fig
 
 
def export_team_paths(team_wide, team_id_to_team, fig_dir=player_fig_dir, position="teams", dpi=200, **kwargs):
    """-> <...>/all_k/team_paths.png. kwargs go to team_paths. Returns the path in a list."""
    out_dir = os.path.join(fig_dir, position, "all_k")
    os.makedirs(out_dir, exist_ok=True)
    fig = team_paths(team_wide, team_id_to_team, **kwargs)
    path = os.path.join(out_dir, "team_paths.png")
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    print(f"saved team paths across k to {os.path.abspath(path)}")
    return [path]

_pos_short = {"Goalkeeper": "GK", "Center Back": "CB", "FullWing Back": "FWB", "Center Midfield": "CM",
              "Winger": "W", "Center Forward": "CF"}
 
def _split_type(col):
    p, n = str(col).split("__soft_")
    return p, n
 
def _trait_label(col, strip=("_adj",)):
    s = str(col)
    for w in strip:
        s = s.removesuffix(w)
    return s.replace("_", " ")

def composition_link_table(team_wide, share_cols, style_cols, league_col="league", n_perm=5000, seed=42, min_n=5,
                           drop_mirrored=True):
    """Long table, one row per (share column, style column): rho (strength, -1..1), p from your
    composition_context_correlations, called ONCE PER POSITION so each position counts only the teams with classified
    players there (a team without classified wingers still counts for the goalkeeper, centre-back, ... rows);
    p_bh = one multiple-testing adjustment (your _bh) across all pairs together; n_teams = teams behind the row;
    r_<league> per league and n_same (leagues whose link points the same way as the pooled one) / n_leagues from your
    league_sign_consistency. drop_mirrored keeps one type of every two-type position."""
    share_cols = [c for c in share_cols if c in team_wide.columns]
    style_cols = [c for c in style_cols if c in team_wide.columns]
    by_pos = {}
    for c in share_cols:
        by_pos.setdefault(_split_type(c)[0], []).append(c)
    if drop_mirrored:
        by_pos = {p_: (cs[:1] if len(cs) == 2 else cs) for p_, cs in by_pos.items()}
    rho_parts, p_parts, n_pos = [], [], {}
    for p_, cols in by_pos.items():                                # one call per position: only its own teams
        r_, pv, _ = composition_context_correlations(team_wide, cols, style_cols, n_perm=n_perm, seed=seed)
        rho_parts.append(r_)
        p_parts.append(pv)
        n_pos[p_] = int(len(team_wide[cols + style_cols].dropna()))
    rho = pd.concat(rho_parts).reindex(columns=style_cols)
    p = pd.concat(p_parts).reindex(columns=style_cols)
    flat = p.stack()                                               # one adjustment across all pairs (missing pairs skipped)
    p_bh = pd.Series(_bh(flat.to_numpy(float)), index=flat.index).unstack().reindex(index=p.index, columns=p.columns)
    league = team_wide[league_col]
    rows = []
    for s in rho.index:
        for c in rho.columns:
            if pd.isna(rho.loc[s, c]):
                continue
            lg = league_sign_consistency(team_wide, league, s, c, min_n=min_n)
            r_all = rho.loc[s, c]
            valid = lg["spearman_r"].dropna()
            row = dict(share=s, style=c, rho=r_all, p=p.loc[s, c], p_bh=p_bh.loc[s, c],
                       n_teams=n_pos[_split_type(s)[0]],
                       n_same=int((np.sign(valid) == np.sign(r_all)).sum()), n_leagues=int(len(valid)))
            row.update({f"r_{l}": r for l, r in zip(lg["league"], lg["spearman_r"])})
            rows.append(row)
    out = pd.DataFrame(rows)
    out["position"] = [_split_type(s)[0] for s in out["share"]]
    out["type"] = [_split_type(s)[1] for s in out["share"]]
    n_types = {p_: sum(_split_type(c)[0] == p_ for c in team_wide.columns if "__soft_" in str(c)
                       and str(c).split("__soft_")[-1].isdigit()) for p_ in out["position"].unique()}
    out["mirrored"] = [n_types.get(p_, 0) == 2 for p_ in out["position"]]
    return out
 
def composition_link_map(links, style_groups=None, alpha=0.05, min_leagues=3, gk_note=True, title=None):
    """Overview grid of the consistent links (see the top of the file). style_groups = your feature-group dict
    ({category: [columns]}) to order and head the columns; style columns named with '_adj' match their raw name."""
    ok = (links["p_bh"] < alpha) & (links["n_same"] >= min_leagues)
    shown = links[ok]
    base = lambda c: str(c).removesuffix("_adj")
    traits = list(dict.fromkeys(shown["style"]))
    groups = []
    if style_groups:
        used = set()
        for cat, cols in style_groups.items():
            cs = [t for t in traits if base(t) in {base(x) for x in cols}]
            if cs:
                groups.append((str(cat).replace("_", " ").capitalize(), cs))
                used |= set(cs)
        rest = [t for t in traits if t not in used]
        if rest:
            groups.append(("Other", rest))
    else:
        groups = [(None, traits)]
    cols = [t for _, cs in groups for t in cs]
    rows_ = list(dict.fromkeys(links["share"]))                    # every type stays, so empty rows show "nothing"
    positions = list(dict.fromkeys(_split_type(s)[0] for s in rows_))
    ylist, heads, y = {}, {}, 0.0
    for p_ in positions:
        heads[p_] = y
        y += 1
        for s in [s for s in rows_ if _split_type(s)[0] == p_]:
            ylist[s] = y
            y += 1
        y += 0.3
    n_rows = y
    CW, RH = 0.34, 0.3
    xlist, cheads, x = {}, {}, 0.0
    for cat, cs in groups:
        span = max(len(cs), (len(cat) * 0.075 + 0.3) / CW if cat else 0)   # room for the heading, even over one column
        x0 = x + (span - len(cs)) / 2
        cheads[cat] = (x0, x0 + len(cs) - 1, x, x + span - 1)
        for i, t in enumerate(cs):
            xlist[t] = x0 + i
        x += span + 0.6
    n_cols = max(x - 0.6, 1)
    LEFT, RIGHT, TOP, BOTTOM = 2.0, 0.4, 1.35, 2.9
    W = max(LEFT + n_cols * CW + RIGHT, 7.5)
    H = TOP + n_rows * RH + BOTTOM
    fig = plt.figure(figsize=(W, H))
    fig.set_facecolor(surface)
    ax = fig.add_axes([LEFT / W, BOTTOM / H, n_cols * CW / W, n_rows * RH / H])
    ax.set_xlim(-0.5, n_cols - 0.5)
    ax.set_ylim(n_rows - 0.5, -0.8)
    ax.axis("off")
    rmax = max(shown["rho"].abs().max(), 0.3) if len(shown) else 1.0
    for s, yy in ylist.items():                                    # faint row guides
        ax.plot([-0.5, n_cols - 0.5], [yy, yy], color=muted, alpha=0.15, linewidth=0.6, zorder=0)
        mir = links.loc[links["share"] == s, "mirrored"].iloc[0]
        lab = f"Type {_split_type(s)[1]}" + (" (vs the other type)" if mir else "")
        ax.text(-0.8, yy, lab, ha="right", va="center", fontsize=8.5, color=ink2)
    for p_, yy in heads.items():
        note = " †" if gk_note and "goal" in p_.lower() else ""
        n_t = links.loc[links["position"] == p_, "n_teams"].iloc[0] if "n_teams" in links.columns else None
        ax.text(-0.8 - (LEFT - 0.25) / CW, yy, p_ + note, ha="left", va="center", fontsize=9.5, fontweight="bold",
                color=ink)
        if n_t is not None:                                        # how many teams this position's rows rest on
            ax.text(-0.8, yy, f"{int(n_t)} teams", ha="right", va="center", fontsize=7.5, color=muted)
    for t, xx in xlist.items():
        ax.plot([xx, xx], [0, n_rows - 1], color=muted, alpha=0.08, linewidth=0.6, zorder=0)
        ax.text(xx, n_rows - 0.2, _trait_label(t), rotation=60, ha="right", va="top", fontsize=7.8, color=ink2,
                rotation_mode="anchor")
    for cat, (x0, x1, s0, s1) in cheads.items():
        if cat is None:
            continue
        ax.plot([s0 - 0.2, s1 + 0.2], [-0.55, -0.55], color=ink, linewidth=1)
        ax.text((s0 + s1) / 2, -0.7, cat, ha="center", va="bottom", fontsize=9, fontweight="bold", color=ink)
    for _, r in shown.iterrows():
        ax.scatter(xlist[r["style"]], ylist[r["share"]], s=40 + 260 * (abs(r["rho"]) / rmax) ** 1.5,
                   color=pos if r["rho"] > 0 else neg, alpha=0.9 if r["n_same"] == r["n_leagues"] else 0.6,
                   edgecolors=surface, linewidths=0.8, zorder=3)
    fig.text(0.15 / W, 1 - 0.3 / H, title or "Which player types go with which style traits", fontsize=15,
             fontweight="bold", color=ink, va="top")
    fig.text(0.15 / W, 1 - 0.7 / H, "A dot = teams that give more minutes to this type also do more (blue) or less (red) "
             "of this trait, in the same direction in at least "
             f"{min_leagues} of the 4 leagues. Bigger = stronger. Solid = all leagues agree.", fontsize=8.5,
             color=ink2, va="top")
    foot = [f"{int(ok.sum())} of {len(links)} type-trait pairs pass the multiple-testing check and the league check; "
            "traits without any such link are left out. Style traits are strength-adjusted.",
            "A link does not say whether clubs recruit these types to play this way or coach them into it."]
    if gk_note and any("goal" in p_.lower() for p_ in positions):
        foot.append("† Goalkeeper links: the long-distribution type is drawn from both ends of the table, read with care.")
    for q, s in enumerate(foot):
        fig.text(0.15 / W, (0.15 + 0.18 * (len(foot) - 1 - q)) / H, s, fontsize=7.5, color=muted, va="center")
    return fig
 
def composition_link_scatter(team_wide, links, top=6, alpha=0.05, min_leagues=3, max_per_type=2, league_col="league",
                             ncols=3, title=None, pairs=None, max_per_trait=None):
    """The strongest consistent links, one panel each: every team's share of the position's minutes going to the type
    (across) against the style trait (up), coloured by league, one trend line per league.
    pairs: [(share column, style column), ...] draws exactly these panels in this order (top / max_per_* are ignored);
    a pair that does not pass the checks is still drawn, and its panel says so.
    max_per_trait: in the automatic pick, at most this many panels per style trait (None = no limit), so the strongest
    links are spread over different traits instead of one trait repeated for several types."""
    passes = (links["p_bh"] < alpha) & (links["n_same"] >= min_leagues)
    if pairs is not None:
        picks = []
        for s, c in pairs:
            m = links[(links["share"] == s) & (links["style"] == c)]
            if m.empty:
                raise KeyError(f"pair not in the link table: ({s}, {c})")
            picks.append(m.iloc[0].copy())
            picks[-1]["passes"] = bool(passes.loc[m.index[0]])
    else:
        ok = links[passes].copy()
        ok = ok.reindex(ok["rho"].abs().sort_values(ascending=False).index)
        picks, per_type, per_trait = [], {}, {}
        for _, r in ok.iterrows():
            if per_type.get(r["share"], 0) >= max_per_type:
                continue
            if max_per_trait is not None and per_trait.get(r["style"], 0) >= max_per_trait:
                continue
            r = r.copy()
            r["passes"] = True
            picks.append(r)
            per_type[r["share"]] = per_type.get(r["share"], 0) + 1
            per_trait[r["style"]] = per_trait.get(r["style"], 0) + 1
            if len(picks) == top:
                break
    if not picks:
        raise ValueError("no link passes the checks; lower alpha or min_leagues")
    leagues = sorted(team_wide[league_col].dropna().unique())
    lcol = {l: slots[-4:][i % 4] for i, l in enumerate(leagues)}  # the league colours of your league_mix
    ncols = min(ncols, len(picks))
    nrow = -(-len(picks) // ncols)
    fig, axs = plt.subplots(nrow, ncols, figsize=(4.3 * ncols, 3.6 * nrow + 1.3), squeeze=False)
    fig.set_facecolor(surface)
    for ax, r in zip(axs.ravel(), picks):
        d = team_wide[[r["share"], r["style"], league_col]].dropna()
        ax.set_facecolor(surface)
        for l in leagues:
            g = d[d[league_col] == l]
            ax.scatter(g[r["share"]] * 100, g[r["style"]], s=22, color=lcol[l], alpha=0.85, edgecolors=surface,
                       linewidths=0.5, zorder=3)
            if len(g) >= 3 and g[r["share"]].nunique() > 1:
                b, a = np.polyfit(g[r["share"]] * 100, g[r["style"]], 1)
                xs = np.array([g[r["share"]].min(), g[r["share"]].max()]) * 100
                ax.plot(xs, a + b * xs, color=lcol[l], linewidth=1.4, zorder=2)
        p_, n_ = _split_type(r["share"])
        ax.set_title(f"{_pos_short.get(p_, p_)} type {n_}  →  {_trait_label(r['style'])}", fontsize=9.5,
                     color=ink, loc="left", pad=16)
        ax.text(0.0, 1.02, f"same direction in {r['n_same']} of {r['n_leagues']} leagues"
                + (f" · {int(r['n_teams'])} teams" if "n_teams" in r.index else "")
                + ("" if r.get("passes", True) else " · not a consistent link")
                + ("   †" if "goal" in p_.lower() else ""), transform=ax.transAxes, fontsize=7.8, color=muted,
                va="bottom")
        ax.set_xlabel(f"% of {p_.lower()} minutes to type {n_}", fontsize=8, color=ink2)
        ax.set_ylabel("trait (strength-adjusted)", fontsize=8, color=ink2)
        ax.tick_params(labelsize=7.5, colors=ink2)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        for s in ("left", "bottom"):
            ax.spines[s].set_color(muted)
    for ax in axs.ravel()[len(picks):]:
        ax.axis("off")
    handles = [plt.Line2D([0], [0], marker="o", linestyle="-", color=lcol[l], label=l) for l in leagues]
    fig.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.01, 1 - 0.75 / fig.get_size_inches()[1]),
               ncol=len(leagues), frameon=False, fontsize=8.5)
    fig.suptitle(title or "The strongest links between squad and style, team by team", x=0.01, ha="left",
                 y=1 - 0.12 / fig.get_size_inches()[1], fontsize=15, fontweight="bold", color=ink)
    fig.text(0.01, 0.01, "One dot per team; one line per league. Lines sloping the same way = the link holds in every "
             "league." + (" † Goalkeeper links: read with care." if any("goal" in _split_type(r['share'])[0].lower()
                                                                             for r in picks) else ""),
             fontsize=7.5, color=muted)
    fig.tight_layout(rect=(0, 0.03, 1, 1 - 1.0 / fig.get_size_inches()[1]))
    return fig
 
def export_composition_link_map(links, fig_dir=player_fig_dir, position="teams", filename="composition_links_map.png",
                                dpi=200, **kwargs):
    """-> <...>/all_k/<filename>. links: the table from composition_link_table.
    kwargs go to composition_link_map (style_groups, alpha, min_leagues, gk_note, title). Returns the path in a list."""
    out_dir = os.path.join(fig_dir, position, "all_k")
    os.makedirs(out_dir, exist_ok=True)
    fig = composition_link_map(links, **kwargs)
    path = os.path.join(out_dir, filename)
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    print(f"saved C5 link map to {os.path.abspath(path)}")
    return [path]

def export_composition_link_scatter(team_wide, links, fig_dir=player_fig_dir, position="teams",
                                    filename="composition_links_top.png", dpi=200, **kwargs):
    """-> <...>/all_k/<filename>. links: the table from composition_link_table.
    kwargs go to composition_link_scatter (top, alpha, min_leagues, max_per_type, max_per_trait, pairs, ncols, title).
    Give each panel set its own filename (e.g. the automatic top-15 and a hand-picked pairs= set). Returns the path in a
    list, or [] if no link passes the checks."""
    out_dir = os.path.join(fig_dir, position, "all_k")
    os.makedirs(out_dir, exist_ok=True)
    try:
        fig = composition_link_scatter(team_wide, links, **kwargs)
    except ValueError as e:
        warnings.warn(str(e), stacklevel=2)
        return []
    path = os.path.join(out_dir, filename)
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    print(f"saved C5 link panels to {os.path.abspath(path)}")
    return [path]

def close_pair_groups(D, team_wide, cluster_col, close_share=0.10):
    ids = [t for t in D.index if t in team_wide.index and pd.notna(team_wide.loc[t, cluster_col])]
    M = D.loc[ids, ids].to_numpy(float); M = (M + M.T) / 2
    iu = np.triu_indices(len(ids), 1)
    d = M[iu]; close = d <= np.quantile(d, close_share)
    g = team_wide.loc[ids, cluster_col].astype(int).to_numpy()
    return pd.Series([tuple(sorted(p)) for p in zip(g[iu[0]][close], g[iu[1]][close])]).value_counts()

def league_direction_all(team_wide, share_cols, cluster_col="kmeans_3_cluster", league_col="league"):
    """For every cluster: its share minus the rest of the teams' (pts), pooled, and how many leagues point the same way."""
    out = {}
    for g in sorted(team_wide[cluster_col].dropna().unique()):
        is_g = team_wide[cluster_col] == g
        diff = team_wide.loc[is_g, share_cols].mean() - team_wide.loc[~is_g, share_cols].mean()
        lg = (team_wide.loc[is_g].groupby(league_col)[share_cols].mean()
              - team_wide.loc[~is_g].groupby(league_col)[share_cols].mean())
        out[(f"Cluster {int(g)}", "gap_pts")] = (diff * 100).round(1)
        out[(f"Cluster {int(g)}", "leagues")] = ((np.sign(lg) == np.sign(diff)).sum().astype(str)
                                                 + "/" + lg.notna().sum().astype(str))
    return pd.DataFrame(out)

# Team report functions

report_order = [
    # all_k/<Team>_<League>/
    r"^team_card", r"^typical_xi", r"^formations", r"^type_shares$", r"^pitch_profile$",
    # k<n>/<Team>_<League>/ : profile vs its cluster first, then the radars in the group-profile order
    r"^team_profile", r"^pitch_profile_vs_group", r"^type_shares_vs_group",
    r"^build_up_channels", r"^chance_creation_pressing_transitions",
    r"^pull", r"^distance",
]
 
# Readable names for the figures you export (anything else gets a name made from its file name).
report_names = {
    "team_card": "Team card", "typical_xi": "Typical XI", "formations": "Formations",
    "type_shares": "Player-type shares", "pitch_profile": "Pitch profile",
    "team_profile": "Team profile vs its cluster", "pitch_profile_vs_group": "Pitch profile vs its cluster",
    "type_shares_vs_group": "Player-type shares vs its cluster",
    "build_up_channels": "Radar: build up and channels",
    "chance_creation_pressing_transitions": "Radar: chance creation, pressing and transitions", 
    "pull": "Pull chart", "distances": "Distances",
}
kind_order = ["raw", "adj", None]                       # columns of a grouped page
kind_label = {"raw": "Raw", "adj": "Adjusted", None: ""}
scope_order = ["all", "league"]                         # rows of a grouped page
scope_label = {"all": "vs all teams", "league": "vs own league teams"}
 
 
def _split_stem(stem):
    """'build_up_adj_league' -> ('build_up', 'adj', 'league'); 'pull_own_league' -> ('pull', None, 'league')."""
    s, kind, scope = stem, None, "all"
    if s.endswith("_league"):
        s = s[:-len("_league")]
        s = s[:-len("_own")] if s.endswith("_own") else s
        scope = "league"
    for suf in ("_adj", "_raw"):
        if s.endswith(suf):
            s, kind = s[:-len(suf)], suf[1:]
    return s, kind, scope
 
 
def _base_label(base):
    if base in report_names:
        return report_names[base]
    words = [w.upper() if w.lower() in ("xi", "gk", "cb", "cf", "cm", "fwb") else w for w in base.split("_") if w]
    text = " ".join(words)
    return text[:1].upper() + text[1:]
 
 
def _figure_label(stem):
    """One-figure label: 'build_up_adj_league' -> 'Radar: build up (adjusted, own league)'."""
    base, kind, scope = _split_stem(stem)
    extra = [x for x in ({"adj": "adjusted", "raw": "raw"}.get(kind), "own league" if scope == "league" else None) if x]
    return _base_label(base) + (f" ({', '.join(extra)})" if extra else "")
 
 
def _report_pages(folder, fig_dir, position, ks, order, exclude, group_versions=True):
    """[(section, label, nrows, ncols, {(row, col): (caption, path)})] for one team: all_k first, then each k."""
    sections = [("All k", os.path.join(fig_dir, position, "all_k", folder))]
    sections += [(f"k = {k}", os.path.join(fig_dir, position, f"k{k}", folder)) for k in ks]
 
    def rank(name):
        hit = [i for i, pat in enumerate(order) if re.search(pat, name)]
        return (hit[0] if hit else len(order), name)
 
    pages = []
    for sec, d in sections:
        stems = sorted(os.path.basename(f)[:-4] for f in glob.glob(os.path.join(d, "*.png")))
        stems = [s for s in stems if not any(re.search(x, s) for x in exclude)]
        if not group_versions:
            for s in sorted(stems, key=rank):
                pages.append((sec, _figure_label(s), 1, 1, {(0, 0): ("", os.path.join(d, s + ".png"))}))
            continue
        groups = {}
        for s in stems:
            base, kind, scope = _split_stem(s)
            groups.setdefault(base, []).append((kind, scope, os.path.join(d, s + ".png")))
        for base in sorted(groups, key=rank):
            members = groups[base]
            kinds = [k for k in kind_order if any(m[0] == k for m in members)]
            scopes = [sc for sc in scope_order if any(m[1] == sc for m in members)]
            if len(members) == 1:
                kind, scope, path = members[0]
                pages.append((sec, _figure_label(os.path.basename(path)[:-4]), 1, 1, {(0, 0): ("", path)}))
                continue
            if len(kinds) > 1:                                   # raw / adjusted x all / own league: 2 x 2 grid
                nrows, ncols = len(scopes), len(kinds)
                cell = lambda kind, scope: (scopes.index(scope), kinds.index(kind))
            else:                                                # all / own league: side by side
                nrows, ncols = 1, len(scopes)
                cell = lambda kind, scope: (0, scopes.index(scope))
            panels = {}
            for kind, scope, path in members:
                cap = " · ".join(x for x in (kind_label[kind], scope_label[scope]) if x)
                panels[cell(kind, scope)] = (cap, path)
            pages.append((sec, _base_label(base), nrows, ncols, panels))
    return pages
 
 
def _load_png(path, max_px):
    """RGB array of the PNG (transparency flattened onto the page colour), shrunk so its longer side <= max_px."""
    im = Image.open(path)
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        bg = Image.new("RGBA", im.size, surface)
        im = Image.alpha_composite(bg, im)
    im = im.convert("RGB")
    if max_px and max(im.size) > max_px:
        s = max_px / max(im.size)
        im = im.resize((max(1, round(im.size[0] * s)), max(1, round(im.size[1] * s))), Image.LANCZOS)
    return np.asarray(im)
 
 
def _report_page(header, nrows, ncols, panels, max_px):
    """One page: header on top, the figures in an nrows x ncols grid, each at its own aspect ratio with its caption.
    panels: {(row, col): (caption, path)}. Cells without a figure stay empty."""
    arrs = {rc: (cap, _load_png(p, max_px)) for rc, (cap, p) in panels.items()}
    col_w = 11.0 if ncols == 1 else 8.4
    max_h = 13.5 if nrows == 1 and ncols == 1 else 11.0
    has_cap = any(cap for cap, _ in arrs.values())
    TOP, PAD, GAP, CAP = 0.6, 0.25, 0.3, (0.32 if has_cap else 0.0)
    row_h = []
    for r in range(nrows):
        hs = [col_w * a.shape[0] / a.shape[1] for (rr, _), (_, a) in arrs.items() if rr == r]
        row_h.append(min(max(hs) if hs else 1.0, max_h))
    W = 2 * PAD + ncols * col_w + (ncols - 1) * GAP
    H = TOP + sum(row_h) + nrows * CAP + (nrows - 1) * GAP + PAD
    fig = plt.figure(figsize=(W, H))
    fig.set_facecolor(surface)
    fig.text(PAD / W, 1 - 0.32 / H, header, fontsize=12, fontweight="bold", color=ink, va="center")
    y_top = H - TOP
    for r in range(nrows):
        for c in range(ncols):
            if (r, c) not in arrs:
                continue
            cap, a = arrs[(r, c)]
            x0 = PAD + c * (col_w + GAP)
            if cap:
                fig.text((x0 + 0.05) / W, (y_top - CAP / 2) / H, cap, fontsize=10, fontweight="bold", color=ink2,
                         va="center")
            w = col_w
            h = w * a.shape[0] / a.shape[1]
            if h > row_h[r]:                                      # taller than the row allows: shrink, keep aspect
                h = row_h[r]
                w = h * a.shape[1] / a.shape[0]
            ax = fig.add_axes([(x0 + (col_w - w) / 2) / W, (y_top - CAP - h) / H, w / W, h / H])
            ax.imshow(a, interpolation="none")
            ax.axis("off")
        y_top -= row_h[r] + CAP + GAP
    return fig
 
 
def _report_contents(team_name, league, items):
    """Contents page: one column per section (All k, k = 2, ...), each page a link target.
    items: [(section, label, page)]. Returns (fig, [rect in points per item, in item order])."""
    sections = list(dict.fromkeys(s for s, _, _ in items))
    by_sec = {sec: [it for it in items if it[0] == sec] for sec in sections}
    COL, ROW = 3.7, 0.28
    n_rows = max(len(v) for v in by_sec.values())
    W = max(0.6 + len(sections) * COL, 8.0)
    H = 1.75 + (n_rows + 0.5) * ROW + 0.3
    fig = plt.figure(figsize=(W, H))
    fig.set_facecolor(surface)
    fig.text(0.3 / W, 1 - 0.45 / H, team_name, fontsize=18, fontweight="bold", color=ink, va="center")
    fig.text(0.3 / W, 1 - 0.85 / H, f"{league} · every figure exported for this team. Click a page to open it; "
             "every page links back here.", fontsize=9.5, color=ink2, va="center")
    rect_of = {}
    for j, sec in enumerate(sections):
        x = 0.3 + j * COL
        y = H - 1.45
        fig.text(x / W, y / H, sec, fontsize=11, fontweight="bold", color=ink, va="center")
        for i, (_, label, page) in enumerate(by_sec[sec]):
            yy = y - (i + 1) * ROW
            fig.text(x / W, yy / H, label, fontsize=8.8, color=slots[0], va="center")
            fig.text((x + COL - 0.35) / W, yy / H, f"p. {page}", fontsize=8, color=muted, va="center", ha="right")
            rect_of[page] = (x * 72, (yy - ROW / 2) * 72, (x + COL - 0.3) * 72, (yy + ROW / 2) * 72)
    return fig, [rect_of[page] for _, _, page in items]
 
 
def _back_link_report(fig, text="← Back to contents"):
    W, H = fig.get_size_inches()
    t = fig.text(1 - 0.25 / W, 1 - 0.32 / H, text, fontsize=10, color=slots[0], ha="right", va="center")
    bb = t.get_window_extent(fig.canvas.get_renderer())          # measures the text only (no full draw of the page)
    k = 72 / fig.dpi
    return (bb.x0 * k - 4, bb.y0 * k - 4, bb.x1 * k + 4, bb.y1 * k + 4)
 
 
def team_report_pdf(team_id, team_id_to_team, team_id_to_league, fig_dir=player_fig_dir, position="teams",
                    ks=(2, 3, 4), order=None, exclude=(), max_px=1800, filename="team_report.pdf", fit_page=False,
                    group_versions=True):
    """Every PNG exported for one team behind a clickable contents page -> <...>/all_k/<Team>_<League>/team_report.pdf.
    ks: which k folders to include (e.g. ks=(2, 3) to leave out the diagnostic k = 4).
    order: list of regexes on figure names giving the page order within each section; default REPORT_ORDER.
    exclude: regexes of file names (without .png) to leave out (e.g. exclude=(r"_raw",) drops the raw radars).
    max_px: longest side of each image in the PDF (smaller = smaller file; 1800 stays sharp on screen).
    group_versions: True puts the versions of one figure on one page (side by side, or 2 x 2 for the radars).
    Returns the path, or None if the team has no exported figures."""
    order = report_order if order is None else order
    name = str(team_id_to_team.get(team_id, team_id))
    league = str(team_id_to_league.get(team_id, ""))
    folder = get_folder_name(team_id, team_id, team_id_to_team, team_id_to_league)
    pages = _report_pages(folder, fig_dir, position, ks, order, exclude, group_versions)
    if not pages:
        warnings.warn(f"no exported figures found for {name} (looked in all_k/{folder} and k*/{folder})", stacklevel=2)
        return None
    out_dir = os.path.join(fig_dir, position, "all_k", folder)
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, filename)
    items = [(sec, label, i + 2) for i, (sec, label, _, _, _) in enumerate(pages)]
    try:
        from pypdf import PdfReader, PdfWriter
        from pypdf.annotations import Link
        from pypdf.generic import ArrayObject, NumberObject, NameObject, NullObject, FloatObject, Fit
    except ImportError as e:
        raise ImportError("team_report_pdf needs pypdf (pip install pypdf)") from e
    writer = PdfWriter()
 
    def add_page(fig):
        """Save one page on its own and add it to the report, so only one page's images are ever held in memory."""
        buf = io.BytesIO()
        fig.savefig(buf, format="pdf")                            # no bbox_inches="tight": link positions must not move
        plt.close(fig)
        buf.seek(0)
        writer.add_page(PdfReader(buf).pages[0])
        gc.collect()                                              # figures hold their images until collected
 
    fig, contents_rects = _report_contents(name, league, items)
    add_page(fig)
    back_rects = []
    for sec, label, nrows, ncols, panels in pages:
        header = f"{name} ({league}) · {sec} · {label}"
        try:
            fig = _report_page(header, nrows, ncols, panels, max_px)
        except Exception as e:                                    # unreadable file: placeholder keeps page numbers
            plt.close("all")
            fig = plt.figure(figsize=(11, 3))
            fig.set_facecolor(surface)
            fig.text(0.03, 0.6, header, fontsize=12, fontweight="bold", color=ink)
            fig.text(0.03, 0.35, f"Could not draw this page: {type(e).__name__}: {e}", fontsize=9, color=muted)
        back_rects.append(_back_link_report(fig))
        add_page(fig)
 
    no_border = ArrayObject([NumberObject(0), NumberObject(0), NumberObject(0)])
    top_of = lambda target: float(writer.pages[target].mediabox.top)
 
    def goto(on_page, rect, target):                              # link to the page object itself (works in all viewers)
        a = writer.add_annotation(on_page, Link(rect=rect, target_page_index=target, border=no_border))
        ref = writer.pages[target].indirect_reference
        a[NameObject("/Dest")] = (ArrayObject([ref, NameObject("/Fit")]) if fit_page else
                                  ArrayObject([ref, NameObject("/XYZ"), NullObject(), FloatObject(top_of(target)),
                                               NullObject()]))
 
    for i, rect in enumerate(contents_rects):
        goto(0, rect, i + 1)
    for i, rect in enumerate(back_rects):
        goto(i + 1, rect, 0)
    fit_of = lambda target: Fit.fit() if fit_page else Fit.xyz(left=None, top=top_of(target), zoom=None)
    writer.add_outline_item("Contents", 0, fit=fit_of(0))
    parents = {}
    for sec, label, page in items:
        if sec not in parents:
            parents[sec] = writer.add_outline_item(sec, page - 1, is_open=True, fit=fit_of(page - 1))
        writer.add_outline_item(label, page - 1, parent=parents[sec], fit=fit_of(page - 1))
    tmp = path + ".tmp"
    with open(tmp, "wb") as fh:
        writer.write(fh)
    os.replace(tmp, path)
    return path
 
 
def export_team_reports(team_id_to_team, team_id_to_league, team_ids=None, **kwargs):
    """One report per team (ordered by league, then team id) -> <...>/all_k/<Team>_<League>/team_report.pdf.
    kwargs go to team_report_pdf (ks=..., exclude=..., max_px=..., fit_page=..., group_versions=...).
    Returns the saved paths."""
    ids = list(team_ids) if team_ids is not None else list(team_id_to_team)
    ids = sorted(ids, key=lambda t: (str(team_id_to_league.get(t, "")), t))
    paths, failed, empty = [], {}, []
    for t in ids:
        try:
            p = team_report_pdf(t, team_id_to_team, team_id_to_league, **kwargs)
        except Exception as e:
            failed[t] = f"{type(e).__name__}: {e}"
            plt.close("all")
            continue
        (paths.append(p) if p else empty.append(t))
        gc.collect()                                              # free each team's images before the next one
    print(f"saved {len(paths)} team reports")
    for t in empty:
        print(f"  no figures  {team_id_to_team.get(t, t)}")
    for t, err in failed.items():
        print(f"  failed      {team_id_to_team.get(t, t)}: {err}")
    return paths
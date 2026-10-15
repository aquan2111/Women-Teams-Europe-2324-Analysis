<p align="right"><img alt="Hudl StatsBomb logo" src="https://raw.githubusercontent.com/statsbomb/logos/main/HudlStatsbomb_Python.svg" height="28"></p>

# Women-Teams-Europe-2324-Analysis

How do women's teams in top European leagues play, which teams play alike, and do teams play a certain way pick a certain type of player?

This project groups 50 teams from four European leagues by their style of play, after allowing for their strength, and looks at the players each type relies on.

## Key Questions

1. **What styles of player are there?** Once you allow for how strong a team is, what styles do the 50 teams fall into, what sets them apart, and does every league have the same styles? -> [Style groups](findings/clustering.md)
2. **Do teams that play alike end up in the same group?** Which groups are tight-knit and which are loose, where do styles overlap, and which teams change group when styles are split more finely? -> [Style groups vs How alike teams play](findings/cluster_vs_distance.md)
3. **Do different styles pick different players?** Does each style give minutes to different types of players, and is it true in every league? -> [Style groups vs Squad](findings/cluster_vs_squad.md)
4. **Which types of player go with which habits?** For example, do teams that play line holding center backs also defend deeper and pass forward deeper, and does that fit what those players do? -> [Player types vs Style habits](findings/style_features_vs_squad.md)
5. **What does each style look like on a real team?** A closer look at clear examples of each style, and teams that sit between styles.

   - [Aston Villa Breakdown](findings/findings_AS_Roma_W.md)
   - [Chelsea Breakdown](findings/findings_Chelsea_FCW.md)
   - [AS Roma Breakdown](findings/findings_AS_Roma_W.md)
   - [Wolfsburg Breakdown](findings/findings_VfL_Wolfsburg_WFC.md)
   - [Barcelona Breakdown](findings/findings_Barcelona_WFC.md)
   - [Internazionale Breakdown](findings/findings_FC_Internazionale_Milano_W.md)
   - [Hoffenheim Breakdown](findings/findings_Hoffenheim_W.md)
   - [Tottenham Breakdown](findings/findings_Tottenham_Hotspur_Women.md)

## Data

Data: [StatsBomb Open Data](https://github.com/statsbomb/open-data).

- Season: 2023/24
- 50 teams: 12 in English FA Women's Super League, 12 in German Frauen Bundesliga, 16 in Spanish Liga F, and 10 in Italian Serie A Women.

## How it works

**Describing a style.** Each team is described by how it plays in four phases:

- **Build-up:** How often teams pass and carry the ball forward, how direct and patient teams take when taking shots.
- **Channels:** Where do teams enter and touch in the final third by different areas, left, right, or center.
- **Chance creation:** Crosses, cut-backs, through balls, and how many of teams' shots come from different situations.
- **Pressing and transitions:** How high teams defend, how much teams counterpress in the opponent's half, and how many of teams' shots come from transitions.

How much of the ball a team has (possession, field tilt) is left out because it says more about how strong a team is than how it plays.

**Allowing for team strength.** A dominant team spends more time in the opponent's half, so it naturally keeps the ball longer and defends higher. Therefore, every measure is compared with what a team of the same strength usually does, so that a style group is not just "top teams" or "bottom teams".

**Grouping teams.** Teams are split by style into 2, 3 and 4 groups. The 2-group split is the main result as it is the most stable, while the 3-group split adds the next level of detail and holds in every league and the 4-group split is a rough guide only. Each team also gets a score for how much it resembles each group, which separates clear members from teams that sit in between.

**Comparing teams.** For every pair of teams, how alike do they play? "Close" means the most alike 10% of all pairs.

**Squads.** Every player has a type, and for each team we look at how its minutes at each position are shared across those types. [Player type details](https://github.com/aquan2111/Clustering-Women-Players-Europe-2324).

**What coutns as a real difference.** A difference between styles only counts if it is at least 5 percentage points and shows up the same way in at least 3 leagues. A link between a player type and a style habit also has to beat chance, allowing for the many comparisons made.

## Conclusions

1. **The main divide is patient against front-foot, and it covers the whole team.** Patient teams move the ball up by carrying, take longer to get a shot away, defend deeper and counterpress less. The other way around can be seen in front-foot teams.
2. **It is not about quality or league.** Top and bottom sides play both ways, and every league has teams of every style.
3. **Patient teams are one family, while front-foot teams come in flavours.** 26 teraams are patient however finely styles are split. On the other hand, front-foot teams divide into central combiners, who attack through the middle with through balls, and wide crossers, who attack down the flanks and cross. With four groups, a set of high pressers appears.
4. **Styles are tendencies, not boxes.** Teams that play alike usually share a group, but some teams sit between styles however they are split.
5. **Style shows in the squad more at the back and in midfield, in every league.** While patient teams give more minutes to short passing keepers, line holding center backs and carrying midfielders, while front-foot teams give more to long passing keepers, stopper center backs and progressive passing midfielders.
6. **Which flank a team attacks, and how it creates chances, has alsmot nothing to do with player types.**

## Limitations

## Repository structure

- `code/`: functions and notebooks
- `findings/`: write-ups for questions, each with its own appendix
- `plots/teams/` `all_k/` (across all splits and per team reports), `k2/`, `k3/`, `k4/`

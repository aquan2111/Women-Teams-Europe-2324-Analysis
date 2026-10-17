# Team Clustering Results

<a id="contents"></a>

## Contents

- [Team breakdown](#team-breakdown)
- [Results](#results)
  - [Results for 2 clusters](#k2-results): [by league](#k2-league) · [by features](#k2-features)
  - [Results for 3 clusters](#k3-results): [by league](#k3-league) · [k = 2 vs k = 3](#k2-vs-k3) · [by features](#k3-features)
  - [Results for 4 clusters](#k4-results): [by league](#k4-league) · [k = 2 vs k = 4](#k2-vs-k4) · [k = 3 vs k = 4](#k3-vs-k4) · [by features](#k4-features)
- [Appendix](#appendix)
  - [A1. Group flow from k = 2 to k = 4](#app-flow)
  - [A2. Team paths across k](#app-paths)
  - **k = 2**
    - [Group profile](#app-k2-profile) (by league: [WSL · Bundesliga](#app-k2-profile-1), [Liga F · Serie A](#app-k2-profile-2))
    - [Build-up and channels radars](#app-k2-build_up_channels) ([WSL](#app-k2-build_up_channels-1) · [Bundesliga](#app-k2-build_up_channels-2) · [Liga F](#app-k2-build_up_channels-3) · [Serie A](#app-k2-build_up_channels-4))
    - [Chance creation, pressing and transitions radars](#app-k2-chance_creation_pressing_transitions) ([WSL](#app-k2-chance_creation_pressing_transitions-1) · [Bundesliga](#app-k2-chance_creation_pressing_transitions-2) · [Liga F](#app-k2-chance_creation_pressing_transitions-3) · [Serie A](#app-k2-chance_creation_pressing_transitions-4))
    - [Strength and dominance](#app-k2-strength) (by league: [WSL · Bundesliga](#app-k2-strength-1), [Liga F · Serie A](#app-k2-strength-2))
  - **k = 3**
    - [Group profile](#app-k3-profile) (by league: [WSL · Bundesliga](#app-k3-profile-1), [Liga F · Serie A](#app-k3-profile-2))
    - [Build-up and channels radars](#app-k3-build_up_channels) ([WSL](#app-k3-build_up_channels-1) · [Bundesliga](#app-k3-build_up_channels-2) · [Liga F](#app-k3-build_up_channels-3) · [Serie A](#app-k3-build_up_channels-4))
    - [Chance creation, pressing and transitions radars](#app-k3-chance_creation_pressing_transitions) ([WSL](#app-k3-chance_creation_pressing_transitions-1) · [Bundesliga](#app-k3-chance_creation_pressing_transitions-2) · [Liga F](#app-k3-chance_creation_pressing_transitions-3) · [Serie A](#app-k3-chance_creation_pressing_transitions-4))
    - [Strength and dominance](#app-k3-strength) (by league: [WSL · Bundesliga](#app-k3-strength-1), [Liga F · Serie A](#app-k3-strength-2))
  - **k = 4**
    - [Group profile](#app-k4-profile) (by league: [WSL · Bundesliga](#app-k4-profile-1), [Liga F · Serie A](#app-k4-profile-2))
    - [Build-up and channels radars](#app-k4-build_up_channels) ([WSL](#app-k4-build_up_channels-1) · [Bundesliga](#app-k4-build_up_channels-2) · [Liga F](#app-k4-build_up_channels-3) · [Serie A](#app-k4-build_up_channels-4))
    - [Chance creation, pressing and transitions radars](#app-k4-chance_creation_pressing_transitions) ([WSL](#app-k4-chance_creation_pressing_transitions-1) · [Bundesliga](#app-k4-chance_creation_pressing_transitions-2) · [Liga F](#app-k4-chance_creation_pressing_transitions-3) · [Serie A](#app-k4-chance_creation_pressing_transitions-4))
    - [Strength and dominance](#app-k4-strength) (by league: [WSL · Bundesliga](#app-k4-strength-1), [Liga F · Serie A](#app-k4-strength-2))

<div style="page-break-after: always;"></div>

<a id="team-breakdown"></a>

## Team breakdown

In this project, there are 50 teams considered, with

- 12 teams in the English FA Women's Super League
- 12 teams in the German Frauen Bundesliga
- 16 teams in the Spanish Liga F
- 10 teams in the Italian Serie A Women

<a id="results"></a>

## Results

<a id="k2-results"></a>

### Results for 2 clusters

<a id="k2-league"></a>

#### Breakdown of results by league

<div>
<table border="1">
  <thead>
    <tr style="text-align: right;">
      <th>league</th>
      <th>FA Women's Super League</th>
      <th>Frauen Bundesliga</th>
      <th>Liga F</th>
      <th>Serie A Women</th>
    </tr>
    <tr>
      <th>kmeans_2_cluster</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>7</td>
      <td>8</td>
      <td>8</td>
      <td>5</td>
    </tr>
    <tr>
      <th>1</th>
      <td>5</td>
      <td>4</td>
      <td>8</td>
      <td>5</td>
    </tr>
  </tbody>
</table>
</div>

While the split is equal for Liga F and Serie A Women, the split for FA WSL and Frauen Bundesliga is around 3:2 between cluster 0 and cluster 1.

Overall the split between cluster 0 and cluster 1 is around 2:3

<a id="k2-features"></a>

#### Breakdown of results by features

- Cluster 0 teams have higher shares of passes being progressive and higher shares of progression done via passing, long goal kicks, crosses, average defensive x location, counterpress actions in opposition half, average directness per possession, and shares of box entries by passes.
- Meanwhile, cluster 1 teams stand out for average number of seconds from start of possession to shots.

Therefore, it can be concluded that

- Cluster 0 teams take a more front footed approach
- Cluster 1 teams are more patient when building up

<a id="k3-results"></a>

### Results for 3 clusters

<a id="k3-league"></a>

#### Breakdown of results by league

<div>
<table border="1">
  <thead>
    <tr>
      <th>league</th>
      <th>FA Women's Super League</th>
      <th>Frauen Bundesliga</th>
      <th>Liga F</th>
      <th>Serie A Women</th>
    </tr>
    <tr>
      <th>kmeans_3_cluster</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>4</td>
      <td>3</td>
      <td>5</td>
      <td>3</td>
    </tr>
    <tr>
      <th>1</th>
      <td>3</td>
      <td>6</td>
      <td>6</td>
      <td>4</td>
    </tr>
    <tr>
      <th>2</th>
      <td>5</td>
      <td>3</td>
      <td>5</td>
      <td>3</td>
    </tr>
  </tbody>
</table>
</div>

The split was rather equal for all leagues, although slightly less on cluster 0 and more on cluster 1. 

<a id="k2-vs-k3"></a>

#### Comparing results for 2 clusters against 3 clusters

<div>
<table border="1">
  <thead>
    <tr>
      <th>kmeans_3_cluster</th>
      <th>0</th>
      <th>1</th>
      <th>2</th>
    </tr>
    <tr>
      <th>kmeans_2_cluster</th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>15</td>
      <td>13</td>
      <td>0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>0</td>
      <td>6</td>
      <td>16</td>
    </tr>
  </tbody>
</table>
</div>

Cluster 1 from k = 3 looks like a middle zone between the two k = 2 clusters.

<a id="k3-features"></a>

#### Breakdown of results by features

- Cluster 0 teams show positiveness towards forward passing, high directness and low patience in attacking. They cross the most, while they have fewer of their shots on open play but more on direct set piece.
- Cluster 2 teams show lower shares of passes progressive and progression via passing, lower shares of counterpress actions in opposing half and lower defensive positions, higher patience per shot ending possession, less reliance on passes to get into box, and higher share of progressive carries. They also had the fewest central final third touches entries via passes.
- Cluster 1 teams progress more by passing than carrying, as shown in their lowest share of progressive carries. They are very close to cluster 2 in directness, while staying moderately close to cluster 0 in patience. They also had a higher share of shots from open play, just like cluster 2.

Consequently,

- Similar to k = 2 cluster 0, k = 3 cluster 0 are direct and front footed teams
- Similar to k = 2 cluster 1, k = 3 cluster 2 teams take a more patient approach
- k = 3 cluster 1 are passing teams that move the ball up quickly but not directly.

<a id="k4-results"></a>

### Results for 4 clusters

<a id="k4-league"></a>

#### Breakdown of results by league

<div>
<table border="1">
  <thead>
    <tr>
      <th>league</th>
      <th>FA Women's Super League</th>
      <th>Frauen Bundesliga</th>
      <th>Liga F</th>
      <th>Serie A Women</th>
    </tr>
    <tr>
      <th>kmeans_4_cluster</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>2</td>
      <td>3</td>
      <td>2</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
      <td>4</td>
      <td>3</td>
      <td>2</td>
    </tr>
    <tr>
      <th>2</th>
      <td>5</td>
      <td>4</td>
      <td>5</td>
      <td>3</td>
    </tr>
    <tr>
      <th>3</th>
      <td>4</td>
      <td>2</td>
      <td>5</td>
      <td>3</td>
    </tr>
  </tbody>
</table>
</div>

The split was slightly more lopsided towards cluster 3, which mainly come down to Liga F teams. Other than that, the split was quite equal between all 4 clusters.

<a id="k2-vs-k4"></a>

#### Comparing results for 2 clusters against 4 clusters

<div>
<table border="1">
  <thead>
    <tr>
      <th>kmeans_4_cluster</th>
      <th>0</th>
      <th>1</th>
      <th>2</th>
      <th>3</th>
    </tr>
    <tr>
      <th>kmeans_2_cluster</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0</td>
      <td>11</td>
      <td>17</td>
      <td>0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>8</td>
      <td>0</td>
      <td>0</td>
      <td>14</td>
    </tr>
  </tbody>
</table>
</div>

While k = 2 cluster 0 is broken down into k = 4 clusters 1 and 2, k = 2 cluster 1 is broken down into k = 4 clusters 0 and 3.

<a id="k3-vs-k4"></a>

#### Comparing results for 3 clusters against 4 clusters

<div>
<table border="1">
  <thead>
    <tr>
      <th>kmeans_4_cluster</th>
      <th>0</th>
      <th>1</th>
      <th>2</th>
      <th>3</th>
    </tr>
    <tr>
      <th>kmeans_3_cluster</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0</td>
      <td>0</td>
      <td>15</td>
      <td>0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>3</td>
      <td>11</td>
      <td>2</td>
      <td>3</td>
    </tr>
    <tr>
      <th>2</th>
      <td>5</td>
      <td>0</td>
      <td>0</td>
      <td>11</td>
    </tr>
  </tbody>
</table>
</div>

While k = 3 cluster 0 converts into k = 4 cluster 2, k = 3 cluster 1 mostly converts to k = 4 cluster 1, and k = 3 cluster 2 converts into k = 3 cluster 3. Cluster 0 of k = 4 is a smaller sample drawing from both k = 3 clusters 1 and 2.

<a id="k4-features"></a>

#### Breakdown of results by features

Clusters 1 and 2 both defend high and counterpress a lot in the opponent's half and cross more.

- Cluster 2 teams have more progressive passes, build up the most directly, take more long goal kicks, have the least shots from open play but the most from direct set piece and transitions.
- Cluster 1 teams pass shorter and less forward than cluster 2. While they carry the ball forward the least, they had the highest share of shots from open play out of all four clusters and the lowest off direct set piece and transitions.
- Cluster 1 teams get forward and enter the box more by passing than carrying. They also attempt more crosses, and higher share of shots coming from open play.

Clusters 0 and 3, on the other hand, both defend lower and counterpress less in the opponent's half.

- Cluster 0 teams have most of their goal kicks short. They had the most final third entries into central positions. They attempt the least crosses out of all four clusters.
- Cluster 3 teams progress less by passing, are the most patient when building up. They attempt fewer through balls. They had the least final third entries into central positions.

Hence,

- Cluster 2 are the most direct, front footed teams.
- Cluster 1 are front footed teams that build their way more in open play rather than going long.
- Cluster 0 are deeper teams that build up short and go more through the middle
- Cluster 3 are patient teams that avoid using the middle.

<div style="page-break-after: always;"></div>

<a id="appendix"></a>

## Appendix

<a id="app-flow"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A1. Group flow from k = 2 to k = 4

<p align="center">
  <img src="../plots/teams/all_k/group_flow.png" alt="Group flow" width="85%">
</p>
<p align="center"><em>Figure A1. How teams move between clusters from k = 2 to k = 4.</em></p>

<div style="page-break-after: always;"></div>

<a id="app-paths"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A2. Team paths across k

<p align="center">
  <img src="../plots/teams/all_k/team_paths.png" alt="Team paths from k = 2 to k = 4" width="65%">
</p>
<p align="center"><em>Figure A2. Each team's cluster from k = 2 to k = 4. A team moves when it leaves the cluster that most of its previous cluster went to; 16 teams stay patient at every k.</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k2-profile"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A3. Group profile, k = 2

<p align="center">
  <img src="../plots/teams/k2/group_profile.png" alt="Group profile, k = 2" width="90%">
</p>
<p align="center"><em>Figure A3. Headline traits by cluster at k = 2: dots after allowing for team strength, raw values in the table.</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k2-profile-1"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A4. Group profile by league, k = 2: FA Women's Super League and Frauen Bundesliga

<p align="center">
  <img src="../plots/teams/k2/group_profile_FA_Womens_Super_League.png" alt="Group profile, FA Women's Super League, k = 2" width="49%">
  <img src="../plots/teams/k2/group_profile_Frauen_Bundesliga.png" alt="Group profile, Frauen Bundesliga, k = 2" width="49%">
</p>
<p align="center"><em>Figure A4. Headline traits by cluster at k = 2, within FA Women's Super League (left) and Frauen Bundesliga (right): dots after allowing for team strength, raw values in the table. Each cluster rests on only a few teams per league.</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k2-profile-2"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A5. Group profile by league, k = 2: Liga F and Serie A Women

<p align="center">
  <img src="../plots/teams/k2/group_profile_Liga_F.png" alt="Group profile, Liga F, k = 2" width="49%">
  <img src="../plots/teams/k2/group_profile_Serie_A_Women.png" alt="Group profile, Serie A Women, k = 2" width="49%">
</p>
<p align="center"><em>Figure A5. Headline traits by cluster at k = 2, within Liga F (left) and Serie A Women (right): dots after allowing for team strength, raw values in the table. Each cluster rests on only a few teams per league.</em></p>

<div style="page-break-after: always;"></div><a id="app-k2-build_up_channels"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A6. Build-up and channels radars, k = 2

<p align="center">
  <img src="../plots/teams/k2/build_up_channels_raw.png" alt="Build-up and channels radar, raw, k = 2" width="49%">
  <img src="../plots/teams/k2/build_up_channels_adj.png" alt="Build-up and channels radar, adjusted, k = 2" width="49%">
</p>
<p align="center"><em>Figure A6. Build-up and channels traits of each cluster at k = 2: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div><a id="app-k2-build_up_channels-1"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A7. Build-up and channels radars, k = 2: FA Women's Super League

<p align="center">
  <img src="../plots/teams/k2/build_up_channels_raw_FA_Womens_Super_League.png" alt="Build-up and channels radar, raw, FA Women's Super League, k = 2" width="49%">
  <img src="../plots/teams/k2/build_up_channels_adj_FA_Womens_Super_League.png" alt="Build-up and channels radar, adjusted, FA Women's Super League, k = 2" width="49%">
</p>
<p align="center"><em>Figure A7. Build-up and channels traits of each cluster at k = 2, FA Women's Super League teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div><a id="app-k2-build_up_channels-2"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A8. Build-up and channels radars, k = 2: Frauen Bundesliga

<p align="center">
  <img src="../plots/teams/k2/build_up_channels_raw_Frauen_Bundesliga.png" alt="Build-up and channels radar, raw, Frauen Bundesliga, k = 2" width="49%">
  <img src="../plots/teams/k2/build_up_channels_adj_Frauen_Bundesliga.png" alt="Build-up and channels radar, adjusted, Frauen Bundesliga, k = 2" width="49%">
</p>
<p align="center"><em>Figure A8. Build-up and channels traits of each cluster at k = 2, Frauen Bundesliga teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div><a id="app-k2-build_up_channels-3"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A9. Build-up and channels radars, k = 2: Liga F

<p align="center">
  <img src="../plots/teams/k2/build_up_channels_raw_Liga_F.png" alt="Build-up and channels radar, raw, Liga F, k = 2" width="49%">
  <img src="../plots/teams/k2/build_up_channels_adj_Liga_F.png" alt="Build-up and channels radar, adjusted, Liga F, k = 2" width="49%">
</p>
<p align="center"><em>Figure A9. Build-up and channels traits of each cluster at k = 2, Liga F teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div><a id="app-k2-build_up_channels-4"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A10. Build-up and channels radars, k = 2: Serie A Women

<p align="center">
  <img src="../plots/teams/k2/build_up_channels_raw_Serie_A_Women.png" alt="Build-up and channels radar, raw, Serie A Women, k = 2" width="49%">
  <img src="../plots/teams/k2/build_up_channels_adj_Serie_A_Women.png" alt="Build-up and channels radar, adjusted, Serie A Women, k = 2" width="49%">
</p>
<p align="center"><em>Figure A10. Build-up and channels traits of each cluster at k = 2, Serie A Women teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div><a id="app-k2-chance_creation_pressing_transitions"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A11. Chance creation, pressing and transitions radars, k = 2

<p align="center">
  <img src="../plots/teams/k2/chance_creation_pressing_transitions_raw.png" alt="Chance creation, pressing and transitions radar, raw, k = 2" width="49%">
  <img src="../plots/teams/k2/chance_creation_pressing_transitions_adj.png" alt="Chance creation, pressing and transitions radar, adjusted, k = 2" width="49%">
</p>
<p align="center"><em>Figure A11. Chance creation, pressing and transitions traits of each cluster at k = 2: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div><a id="app-k2-chance_creation_pressing_transitions-1"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A12. Chance creation, pressing and transitions radars, k = 2: FA Women's Super League

<p align="center">
  <img src="../plots/teams/k2/chance_creation_pressing_transitions_raw_FA_Womens_Super_League.png" alt="Chance creation, pressing and transitions radar, raw, FA Women's Super League, k = 2" width="49%">
  <img src="../plots/teams/k2/chance_creation_pressing_transitions_adj_FA_Womens_Super_League.png" alt="Chance creation, pressing and transitions radar, adjusted, FA Women's Super League, k = 2" width="49%">
</p>
<p align="center"><em>Figure A12. Chance creation, pressing and transitions traits of each cluster at k = 2, FA Women's Super League teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div><a id="app-k2-chance_creation_pressing_transitions-2"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A13. Chance creation, pressing and transitions radars, k = 2: Frauen Bundesliga

<p align="center">
  <img src="../plots/teams/k2/chance_creation_pressing_transitions_raw_Frauen_Bundesliga.png" alt="Chance creation, pressing and transitions radar, raw, Frauen Bundesliga, k = 2" width="49%">
  <img src="../plots/teams/k2/chance_creation_pressing_transitions_adj_Frauen_Bundesliga.png" alt="Chance creation, pressing and transitions radar, adjusted, Frauen Bundesliga, k = 2" width="49%">
</p>
<p align="center"><em>Figure A13. Chance creation, pressing and transitions traits of each cluster at k = 2, Frauen Bundesliga teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div><a id="app-k2-chance_creation_pressing_transitions-3"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A14. Chance creation, pressing and transitions radars, k = 2: Liga F

<p align="center">
  <img src="../plots/teams/k2/chance_creation_pressing_transitions_raw_Liga_F.png" alt="Chance creation, pressing and transitions radar, raw, Liga F, k = 2" width="49%">
  <img src="../plots/teams/k2/chance_creation_pressing_transitions_adj_Liga_F.png" alt="Chance creation, pressing and transitions radar, adjusted, Liga F, k = 2" width="49%">
</p>
<p align="center"><em>Figure A14. Chance creation, pressing and transitions traits of each cluster at k = 2, Liga F teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div><a id="app-k2-chance_creation_pressing_transitions-4"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A15. Chance creation, pressing and transitions radars, k = 2: Serie A Women

<p align="center">
  <img src="../plots/teams/k2/chance_creation_pressing_transitions_raw_Serie_A_Women.png" alt="Chance creation, pressing and transitions radar, raw, Serie A Women, k = 2" width="49%">
  <img src="../plots/teams/k2/chance_creation_pressing_transitions_adj_Serie_A_Women.png" alt="Chance creation, pressing and transitions radar, adjusted, Serie A Women, k = 2" width="49%">
</p>
<p align="center"><em>Figure A15. Chance creation, pressing and transitions traits of each cluster at k = 2, Serie A Women teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k2-strength"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A16. Strength and dominance, k = 2

<p align="center">
  <img src="../plots/teams/k2/strength_dominance_strips.png" alt="Strength and dominance strips, k = 2" width="90%">
</p>
<p align="center"><em>Figure A16. Strength and dominance measures for every team, grouped by cluster, at k = 2.</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k2-strength-1"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A17. Strength and dominance by league, k = 2: FA Women's Super League and Frauen Bundesliga

<p align="center">
  <img src="../plots/teams/k2/strength_dominance_strips_FA_Womens_Super_League.png" alt="Strength and dominance, FA Women's Super League, k = 2" width="49%">
  <img src="../plots/teams/k2/strength_dominance_strips_Frauen_Bundesliga.png" alt="Strength and dominance, Frauen Bundesliga, k = 2" width="49%">
</p>
<p align="center"><em>Figure A17. Strength and dominance measures for every team, grouped by cluster, at k = 2, within FA Women's Super League (left) and Frauen Bundesliga (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k2-strength-2"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A18. Strength and dominance by league, k = 2: Liga F and Serie A Women

<p align="center">
  <img src="../plots/teams/k2/strength_dominance_strips_Liga_F.png" alt="Strength and dominance, Liga F, k = 2" width="49%">
  <img src="../plots/teams/k2/strength_dominance_strips_Serie_A_Women.png" alt="Strength and dominance, Serie A Women, k = 2" width="49%">
</p>
<p align="center"><em>Figure A18. Strength and dominance measures for every team, grouped by cluster, at k = 2, within Liga F (left) and Serie A Women (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k3-profile"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A19. Group profile, k = 3

<p align="center">
  <img src="../plots/teams/k3/group_profile.png" alt="Group profile, k = 3" width="90%">
</p>
<p align="center"><em>Figure A19. Headline traits by cluster at k = 3: dots after allowing for team strength, raw values in the table.</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k3-profile-1"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A20. Group profile by league, k = 3: FA Women's Super League and Frauen Bundesliga

<p align="center">
  <img src="../plots/teams/k3/group_profile_FA_Womens_Super_League.png" alt="Group profile, FA Women's Super League, k = 3" width="49%">
  <img src="../plots/teams/k3/group_profile_Frauen_Bundesliga.png" alt="Group profile, Frauen Bundesliga, k = 3" width="49%">
</p>
<p align="center"><em>Figure A20. Headline traits by cluster at k = 3, within FA Women's Super League (left) and Frauen Bundesliga (right): dots after allowing for team strength, raw values in the table. Each cluster rests on only a few teams per league.</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k3-profile-2"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A21. Group profile by league, k = 3: Liga F and Serie A Women

<p align="center">
  <img src="../plots/teams/k3/group_profile_Liga_F.png" alt="Group profile, Liga F, k = 3" width="49%">
  <img src="../plots/teams/k3/group_profile_Serie_A_Women.png" alt="Group profile, Serie A Women, k = 3" width="49%">
</p>
<p align="center"><em>Figure A21. Headline traits by cluster at k = 3, within Liga F (left) and Serie A Women (right): dots after allowing for team strength, raw values in the table. Each cluster rests on only a few teams per league.</em></p>

<div style="page-break-after: always;"></div><a id="app-k3-build_up_channels"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A22. Build-up and channels radars, k = 3

<p align="center">
  <img src="../plots/teams/k3/build_up_channels_raw.png" alt="Build-up and channels radar, raw, k = 3" width="49%">
  <img src="../plots/teams/k3/build_up_channels_adj.png" alt="Build-up and channels radar, adjusted, k = 3" width="49%">
</p>
<p align="center"><em>Figure A22. Build-up and channels traits of each cluster at k = 3: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div><a id="app-k3-build_up_channels-1"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A23. Build-up and channels radars, k = 3: FA Women's Super League

<p align="center">
  <img src="../plots/teams/k3/build_up_channels_raw_FA_Womens_Super_League.png" alt="Build-up and channels radar, raw, FA Women's Super League, k = 3" width="49%">
  <img src="../plots/teams/k3/build_up_channels_adj_FA_Womens_Super_League.png" alt="Build-up and channels radar, adjusted, FA Women's Super League, k = 3" width="49%">
</p>
<p align="center"><em>Figure A23. Build-up and channels traits of each cluster at k = 3, FA Women's Super League teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div><a id="app-k3-build_up_channels-2"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A24. Build-up and channels radars, k = 3: Frauen Bundesliga

<p align="center">
  <img src="../plots/teams/k3/build_up_channels_raw_Frauen_Bundesliga.png" alt="Build-up and channels radar, raw, Frauen Bundesliga, k = 3" width="49%">
  <img src="../plots/teams/k3/build_up_channels_adj_Frauen_Bundesliga.png" alt="Build-up and channels radar, adjusted, Frauen Bundesliga, k = 3" width="49%">
</p>
<p align="center"><em>Figure A24. Build-up and channels traits of each cluster at k = 3, Frauen Bundesliga teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div><a id="app-k3-build_up_channels-3"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A25. Build-up and channels radars, k = 3: Liga F

<p align="center">
  <img src="../plots/teams/k3/build_up_channels_raw_Liga_F.png" alt="Build-up and channels radar, raw, Liga F, k = 3" width="49%">
  <img src="../plots/teams/k3/build_up_channels_adj_Liga_F.png" alt="Build-up and channels radar, adjusted, Liga F, k = 3" width="49%">
</p>
<p align="center"><em>Figure A25. Build-up and channels traits of each cluster at k = 3, Liga F teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div><a id="app-k3-build_up_channels-4"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A26. Build-up and channels radars, k = 3: Serie A Women

<p align="center">
  <img src="../plots/teams/k3/build_up_channels_raw_Serie_A_Women.png" alt="Build-up and channels radar, raw, Serie A Women, k = 3" width="49%">
  <img src="../plots/teams/k3/build_up_channels_adj_Serie_A_Women.png" alt="Build-up and channels radar, adjusted, Serie A Women, k = 3" width="49%">
</p>
<p align="center"><em>Figure A26. Build-up and channels traits of each cluster at k = 3, Serie A Women teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div><a id="app-k3-chance_creation_pressing_transitions"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A27. Chance creation, pressing and transitions radars, k = 3

<p align="center">
  <img src="../plots/teams/k3/chance_creation_pressing_transitions_raw.png" alt="Chance creation, pressing and transitions radar, raw, k = 3" width="49%">
  <img src="../plots/teams/k3/chance_creation_pressing_transitions_adj.png" alt="Chance creation, pressing and transitions radar, adjusted, k = 3" width="49%">
</p>
<p align="center"><em>Figure A27. Chance creation, pressing and transitions traits of each cluster at k = 3: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div><a id="app-k3-chance_creation_pressing_transitions-1"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A28. Chance creation, pressing and transitions radars, k = 3: FA Women's Super League

<p align="center">
  <img src="../plots/teams/k3/chance_creation_pressing_transitions_raw_FA_Womens_Super_League.png" alt="Chance creation, pressing and transitions radar, raw, FA Women's Super League, k = 3" width="49%">
  <img src="../plots/teams/k3/chance_creation_pressing_transitions_adj_FA_Womens_Super_League.png" alt="Chance creation, pressing and transitions radar, adjusted, FA Women's Super League, k = 3" width="49%">
</p>
<p align="center"><em>Figure A28. Chance creation, pressing and transitions traits of each cluster at k = 3, FA Women's Super League teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div><a id="app-k3-chance_creation_pressing_transitions-2"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A29. Chance creation, pressing and transitions radars, k = 3: Frauen Bundesliga

<p align="center">
  <img src="../plots/teams/k3/chance_creation_pressing_transitions_raw_Frauen_Bundesliga.png" alt="Chance creation, pressing and transitions radar, raw, Frauen Bundesliga, k = 3" width="49%">
  <img src="../plots/teams/k3/chance_creation_pressing_transitions_adj_Frauen_Bundesliga.png" alt="Chance creation, pressing and transitions radar, adjusted, Frauen Bundesliga, k = 3" width="49%">
</p>
<p align="center"><em>Figure A29. Chance creation, pressing and transitions traits of each cluster at k = 3, Frauen Bundesliga teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div><a id="app-k3-chance_creation_pressing_transitions-3"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A30. Chance creation, pressing and transitions radars, k = 3: Liga F

<p align="center">
  <img src="../plots/teams/k3/chance_creation_pressing_transitions_raw_Liga_F.png" alt="Chance creation, pressing and transitions radar, raw, Liga F, k = 3" width="49%">
  <img src="../plots/teams/k3/chance_creation_pressing_transitions_adj_Liga_F.png" alt="Chance creation, pressing and transitions radar, adjusted, Liga F, k = 3" width="49%">
</p>
<p align="center"><em>Figure A30. Chance creation, pressing and transitions traits of each cluster at k = 3, Liga F teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div><a id="app-k3-chance_creation_pressing_transitions-4"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A31. Chance creation, pressing and transitions radars, k = 3: Serie A Women

<p align="center">
  <img src="../plots/teams/k3/chance_creation_pressing_transitions_raw_Serie_A_Women.png" alt="Chance creation, pressing and transitions radar, raw, Serie A Women, k = 3" width="49%">
  <img src="../plots/teams/k3/chance_creation_pressing_transitions_adj_Serie_A_Women.png" alt="Chance creation, pressing and transitions radar, adjusted, Serie A Women, k = 3" width="49%">
</p>
<p align="center"><em>Figure A31. Chance creation, pressing and transitions traits of each cluster at k = 3, Serie A Women teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k3-strength"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A32. Strength and dominance, k = 3

<p align="center">
  <img src="../plots/teams/k3/strength_dominance_strips.png" alt="Strength and dominance strips, k = 3" width="90%">
</p>
<p align="center"><em>Figure A32. Strength and dominance measures for every team, grouped by cluster, at k = 3.</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k3-strength-1"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A33. Strength and dominance by league, k = 3: FA Women's Super League and Frauen Bundesliga

<p align="center">
  <img src="../plots/teams/k3/strength_dominance_strips_FA_Womens_Super_League.png" alt="Strength and dominance, FA Women's Super League, k = 3" width="49%">
  <img src="../plots/teams/k3/strength_dominance_strips_Frauen_Bundesliga.png" alt="Strength and dominance, Frauen Bundesliga, k = 3" width="49%">
</p>
<p align="center"><em>Figure A33. Strength and dominance measures for every team, grouped by cluster, at k = 3, within FA Women's Super League (left) and Frauen Bundesliga (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k3-strength-2"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A34. Strength and dominance by league, k = 3: Liga F and Serie A Women

<p align="center">
  <img src="../plots/teams/k3/strength_dominance_strips_Liga_F.png" alt="Strength and dominance, Liga F, k = 3" width="49%">
  <img src="../plots/teams/k3/strength_dominance_strips_Serie_A_Women.png" alt="Strength and dominance, Serie A Women, k = 3" width="49%">
</p>
<p align="center"><em>Figure A34. Strength and dominance measures for every team, grouped by cluster, at k = 3, within Liga F (left) and Serie A Women (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k4-profile"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A35. Group profile, k = 4

<p align="center">
  <img src="../plots/teams/k4/group_profile.png" alt="Group profile, k = 4" width="90%">
</p>
<p align="center"><em>Figure A35. Headline traits by cluster at k = 4: dots after allowing for team strength, raw values in the table.</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k4-profile-1"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A36. Group profile by league, k = 4: FA Women's Super League and Frauen Bundesliga

<p align="center">
  <img src="../plots/teams/k4/group_profile_FA_Womens_Super_League.png" alt="Group profile, FA Women's Super League, k = 4" width="49%">
  <img src="../plots/teams/k4/group_profile_Frauen_Bundesliga.png" alt="Group profile, Frauen Bundesliga, k = 4" width="49%">
</p>
<p align="center"><em>Figure A36. Headline traits by cluster at k = 4, within FA Women's Super League (left) and Frauen Bundesliga (right): dots after allowing for team strength, raw values in the table. Each cluster rests on only a few teams per league.</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k4-profile-2"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A37. Group profile by league, k = 4: Liga F and Serie A Women

<p align="center">
  <img src="../plots/teams/k4/group_profile_Liga_F.png" alt="Group profile, Liga F, k = 4" width="49%">
  <img src="../plots/teams/k4/group_profile_Serie_A_Women.png" alt="Group profile, Serie A Women, k = 4" width="49%">
</p>
<p align="center"><em>Figure A37. Headline traits by cluster at k = 4, within Liga F (left) and Serie A Women (right): dots after allowing for team strength, raw values in the table. Each cluster rests on only a few teams per league.</em></p>

<div style="page-break-after: always;"></div><a id="app-k4-build_up_channels"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A38. Build-up and channels radars, k = 4

<p align="center">
  <img src="../plots/teams/k4/build_up_channels_raw.png" alt="Build-up and channels radar, raw, k = 4" width="49%">
  <img src="../plots/teams/k4/build_up_channels_adj.png" alt="Build-up and channels radar, adjusted, k = 4" width="49%">
</p>
<p align="center"><em>Figure A38. Build-up and channels traits of each cluster at k = 4: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div><a id="app-k4-build_up_channels-1"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A39. Build-up and channels radars, k = 4: FA Women's Super League

<p align="center">
  <img src="../plots/teams/k4/build_up_channels_raw_FA_Womens_Super_League.png" alt="Build-up and channels radar, raw, FA Women's Super League, k = 4" width="49%">
  <img src="../plots/teams/k4/build_up_channels_adj_FA_Womens_Super_League.png" alt="Build-up and channels radar, adjusted, FA Women's Super League, k = 4" width="49%">
</p>
<p align="center"><em>Figure A39. Build-up and channels traits of each cluster at k = 4, FA Women's Super League teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div><a id="app-k4-build_up_channels-2"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A40. Build-up and channels radars, k = 4: Frauen Bundesliga

<p align="center">
  <img src="../plots/teams/k4/build_up_channels_raw_Frauen_Bundesliga.png" alt="Build-up and channels radar, raw, Frauen Bundesliga, k = 4" width="49%">
  <img src="../plots/teams/k4/build_up_channels_adj_Frauen_Bundesliga.png" alt="Build-up and channels radar, adjusted, Frauen Bundesliga, k = 4" width="49%">
</p>
<p align="center"><em>Figure A40. Build-up and channels traits of each cluster at k = 4, Frauen Bundesliga teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div><a id="app-k4-build_up_channels-3"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A41. Build-up and channels radars, k = 4: Liga F

<p align="center">
  <img src="../plots/teams/k4/build_up_channels_raw_Liga_F.png" alt="Build-up and channels radar, raw, Liga F, k = 4" width="49%">
  <img src="../plots/teams/k4/build_up_channels_adj_Liga_F.png" alt="Build-up and channels radar, adjusted, Liga F, k = 4" width="49%">
</p>
<p align="center"><em>Figure A41. Build-up and channels traits of each cluster at k = 4, Liga F teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div><a id="app-k4-build_up_channels-4"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A42. Build-up and channels radars, k = 4: Serie A Women

<p align="center">
  <img src="../plots/teams/k4/build_up_channels_raw_Serie_A_Women.png" alt="Build-up and channels radar, raw, Serie A Women, k = 4" width="49%">
  <img src="../plots/teams/k4/build_up_channels_adj_Serie_A_Women.png" alt="Build-up and channels radar, adjusted, Serie A Women, k = 4" width="49%">
</p>
<p align="center"><em>Figure A42. Build-up and channels traits of each cluster at k = 4, Serie A Women teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div><a id="app-k4-chance_creation_pressing_transitions"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A43. Chance creation, pressing and transitions radars, k = 4

<p align="center">
  <img src="../plots/teams/k4/chance_creation_pressing_transitions_raw.png" alt="Chance creation, pressing and transitions radar, raw, k = 4" width="49%">
  <img src="../plots/teams/k4/chance_creation_pressing_transitions_adj.png" alt="Chance creation, pressing and transitions radar, adjusted, k = 4" width="49%">
</p>
<p align="center"><em>Figure A43. Chance creation, pressing and transitions traits of each cluster at k = 4: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div><a id="app-k4-chance_creation_pressing_transitions-1"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A44. Chance creation, pressing and transitions radars, k = 4: FA Women's Super League

<p align="center">
  <img src="../plots/teams/k4/chance_creation_pressing_transitions_raw_FA_Womens_Super_League.png" alt="Chance creation, pressing and transitions radar, raw, FA Women's Super League, k = 4" width="49%">
  <img src="../plots/teams/k4/chance_creation_pressing_transitions_adj_FA_Womens_Super_League.png" alt="Chance creation, pressing and transitions radar, adjusted, FA Women's Super League, k = 4" width="49%">
</p>
<p align="center"><em>Figure A44. Chance creation, pressing and transitions traits of each cluster at k = 4, FA Women's Super League teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div><a id="app-k4-chance_creation_pressing_transitions-2"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A45. Chance creation, pressing and transitions radars, k = 4: Frauen Bundesliga

<p align="center">
  <img src="../plots/teams/k4/chance_creation_pressing_transitions_raw_Frauen_Bundesliga.png" alt="Chance creation, pressing and transitions radar, raw, Frauen Bundesliga, k = 4" width="49%">
  <img src="../plots/teams/k4/chance_creation_pressing_transitions_adj_Frauen_Bundesliga.png" alt="Chance creation, pressing and transitions radar, adjusted, Frauen Bundesliga, k = 4" width="49%">
</p>
<p align="center"><em>Figure A45. Chance creation, pressing and transitions traits of each cluster at k = 4, Frauen Bundesliga teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div><a id="app-k4-chance_creation_pressing_transitions-3"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A46. Chance creation, pressing and transitions radars, k = 4: Liga F

<p align="center">
  <img src="../plots/teams/k4/chance_creation_pressing_transitions_raw_Liga_F.png" alt="Chance creation, pressing and transitions radar, raw, Liga F, k = 4" width="49%">
  <img src="../plots/teams/k4/chance_creation_pressing_transitions_adj_Liga_F.png" alt="Chance creation, pressing and transitions radar, adjusted, Liga F, k = 4" width="49%">
</p>
<p align="center"><em>Figure A46. Chance creation, pressing and transitions traits of each cluster at k = 4, Liga F teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div><a id="app-k4-chance_creation_pressing_transitions-4"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A47. Chance creation, pressing and transitions radars, k = 4: Serie A Women

<p align="center">
  <img src="../plots/teams/k4/chance_creation_pressing_transitions_raw_Serie_A_Women.png" alt="Chance creation, pressing and transitions radar, raw, Serie A Women, k = 4" width="49%">
  <img src="../plots/teams/k4/chance_creation_pressing_transitions_adj_Serie_A_Women.png" alt="Chance creation, pressing and transitions radar, adjusted, Serie A Women, k = 4" width="49%">
</p>
<p align="center"><em>Figure A47. Chance creation, pressing and transitions traits of each cluster at k = 4, Serie A Women teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k4-strength"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A48. Strength and dominance, k = 4

<p align="center">
  <img src="../plots/teams/k4/strength_dominance_strips.png" alt="Strength and dominance strips, k = 4" width="90%">
</p>
<p align="center"><em>Figure A48. Strength and dominance measures for every team, grouped by cluster, at k = 4.</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k4-strength-1"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A49. Strength and dominance by league, k = 4: FA Women's Super League and Frauen Bundesliga

<p align="center">
  <img src="../plots/teams/k4/strength_dominance_strips_FA_Womens_Super_League.png" alt="Strength and dominance, FA Women's Super League, k = 4" width="49%">
  <img src="../plots/teams/k4/strength_dominance_strips_Frauen_Bundesliga.png" alt="Strength and dominance, Frauen Bundesliga, k = 4" width="49%">
</p>
<p align="center"><em>Figure A49. Strength and dominance measures for every team, grouped by cluster, at k = 4, within FA Women's Super League (left) and Frauen Bundesliga (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k4-strength-2"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A50. Strength and dominance by league, k = 4: Liga F and Serie A Women

<p align="center">
  <img src="../plots/teams/k4/strength_dominance_strips_Liga_F.png" alt="Strength and dominance, Liga F, k = 4" width="49%">
  <img src="../plots/teams/k4/strength_dominance_strips_Serie_A_Women.png" alt="Strength and dominance, Serie A Women, k = 4" width="49%">
</p>
<p align="center"><em>Figure A50. Strength and dominance measures for every team, grouped by cluster, at k = 4, within Liga F (left) and Serie A Women (right).</em></p>
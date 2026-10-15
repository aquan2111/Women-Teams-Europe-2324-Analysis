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
    - [Build-up radars](#app-k2-build_up) ([WSL](#app-k2-build_up-1) · [Bundesliga](#app-k2-build_up-2) · [Liga F](#app-k2-build_up-3) · [Serie A](#app-k2-build_up-4))
    - [Channels radars](#app-k2-channels) ([WSL](#app-k2-channels-1) · [Bundesliga](#app-k2-channels-2) · [Liga F](#app-k2-channels-3) · [Serie A](#app-k2-channels-4))
    - [Chance creation radars](#app-k2-chance_creation) ([WSL](#app-k2-chance_creation-1) · [Bundesliga](#app-k2-chance_creation-2) · [Liga F](#app-k2-chance_creation-3) · [Serie A](#app-k2-chance_creation-4))
    - [Pressing and transitions radars](#app-k2-pressing_transitions) ([WSL](#app-k2-pressing_transitions-1) · [Bundesliga](#app-k2-pressing_transitions-2) · [Liga F](#app-k2-pressing_transitions-3) · [Serie A](#app-k2-pressing_transitions-4))
    - [Strength and dominance](#app-k2-strength) (by league: [WSL · Bundesliga](#app-k2-strength-1), [Liga F · Serie A](#app-k2-strength-2))
  - **k = 3**
    - [Group profile](#app-k3-profile) (by league: [WSL · Bundesliga](#app-k3-profile-1), [Liga F · Serie A](#app-k3-profile-2))
    - [Build-up radars](#app-k3-build_up) ([WSL](#app-k3-build_up-1) · [Bundesliga](#app-k3-build_up-2) · [Liga F](#app-k3-build_up-3) · [Serie A](#app-k3-build_up-4))
    - [Channels radars](#app-k3-channels) ([WSL](#app-k3-channels-1) · [Bundesliga](#app-k3-channels-2) · [Liga F](#app-k3-channels-3) · [Serie A](#app-k3-channels-4))
    - [Chance creation radars](#app-k3-chance_creation) ([WSL](#app-k3-chance_creation-1) · [Bundesliga](#app-k3-chance_creation-2) · [Liga F](#app-k3-chance_creation-3) · [Serie A](#app-k3-chance_creation-4))
    - [Pressing and transitions radars](#app-k3-pressing_transitions) ([WSL](#app-k3-pressing_transitions-1) · [Bundesliga](#app-k3-pressing_transitions-2) · [Liga F](#app-k3-pressing_transitions-3) · [Serie A](#app-k3-pressing_transitions-4))
    - [Strength and dominance](#app-k3-strength) (by league: [WSL · Bundesliga](#app-k3-strength-1), [Liga F · Serie A](#app-k3-strength-2))
  - **k = 4**
    - [Group profile](#app-k4-profile) (by league: [WSL · Bundesliga](#app-k4-profile-1), [Liga F · Serie A](#app-k4-profile-2))
    - [Build-up radars](#app-k4-build_up) ([WSL](#app-k4-build_up-1) · [Bundesliga](#app-k4-build_up-2) · [Liga F](#app-k4-build_up-3) · [Serie A](#app-k4-build_up-4))
    - [Channels radars](#app-k4-channels) ([WSL](#app-k4-channels-1) · [Bundesliga](#app-k4-channels-2) · [Liga F](#app-k4-channels-3) · [Serie A](#app-k4-channels-4))
    - [Chance creation radars](#app-k4-chance_creation) ([WSL](#app-k4-chance_creation-1) · [Bundesliga](#app-k4-chance_creation-2) · [Liga F](#app-k4-chance_creation-3) · [Serie A](#app-k4-chance_creation-4))
    - [Pressing and transitions radars](#app-k4-pressing_transitions) ([WSL](#app-k4-pressing_transitions-1) · [Bundesliga](#app-k4-pressing_transitions-2) · [Liga F](#app-k4-pressing_transitions-3) · [Serie A](#app-k4-pressing_transitions-4))
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
    <tr>
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
      <td>5</td>
      <td>5</td>
      <td>7</td>
      <td>3</td>
    </tr>
    <tr>
      <th>1</th>
      <td>7</td>
      <td>7</td>
      <td>9</td>
      <td>7</td>
    </tr>
  </tbody>
</table>
</div>

Overall the split between cluster 0 and cluster 1 is around 2:3

<a id="k2-features"></a>

#### Breakdown of results by features

- Cluster 0 teams stand out for shares of passes into the final third and touches in the final third in left locations, average number of seconds from start of possession to shots, shot share from open play, and shares of progressive carries.
- Meanwhile, cluster 1 teams have higher shares of passes being progressive and higher shares of progression done via passing, average defensive x location, counterpress actions in opposition half, average directness per possession, shares of passes into the final third and and touches in the final third in central locations, shares of box entries by passes, and shots shares from transitions and counters.

Therefore, it can be concluded that

- Cluster 0 teams are more patient when building up
- Cluster 1 teams take a more front footed approach

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
      <td>4</td>
      <td>3</td>
    </tr>
    <tr>
      <th>1</th>
      <td>4</td>
      <td>5</td>
      <td>5</td>
      <td>3</td>
    </tr>
    <tr>
      <th>2</th>
      <td>4</td>
      <td>4</td>
      <td>7</td>
      <td>4</td>
    </tr>
  </tbody>
</table>
</div>

The split was rather equal for all leagues, although slightly less on cluster 0 and more on cluster 2

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
      <td>1</td>
      <td>1</td>
      <td>18</td>
    </tr>
    <tr>
      <th>1</th>
      <td>13</td>
      <td>16</td>
      <td>1</td>
    </tr>
  </tbody>
</table>
</div>

While k = 2 cluster 0 mostly converts into k = 3 cluster 2, k = 2 cluster 1 breaks down into k = 3 cluster 0 and 1.

<a id="k3-features"></a>

#### Breakdown of results by features

- Cluster 0 teams show positiveness towards final third touches and passes into final third in central areas, shares of carries into the final third into central locations, and through balls attempted.
- Cluster 1 teams counterpress more on opposition half and engage in defensive actions at higher locations, shares of carries into the final third and touches in the final third in right locations, pass into box share, crosses attempted, and completed pass into the box being crosses.
- Cluster 2 teams show lower shares of passes progressive and progression via passing, lower shares of counterpress actions in opposing half and lower defensive positions, lower directness per shot ending possession, lower shares of passes into box, while higher shares of passes into the final third and touches in the final third in left locations, average number of seconds from start of possession to shots, and progressive carries.

Consequently,

- Similar to k = 2 cluster 0, k = 3 cluster 2 teams take a more patient approach
- k = 3 cluster 0 are front footed teams that combine plays more centrally
- k = 3 cluster 1 are front footed teams that take a wider approach with crosses

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
      <td>3</td>
      <td>5</td>
      <td>2</td>
      <td>3</td>
    </tr>
    <tr>
      <th>1</th>
      <td>3</td>
      <td>2</td>
      <td>4</td>
      <td>2</td>
    </tr>
    <tr>
      <th>2</th>
      <td>3</td>
      <td>2</td>
      <td>3</td>
      <td>2</td>
    </tr>
    <tr>
      <th>3</th>
      <td>3</td>
      <td>3</td>
      <td>7</td>
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
      <td>2</td>
      <td>2</td>
      <td>0</td>
      <td>16</td>
    </tr>
    <tr>
      <th>1</th>
      <td>11</td>
      <td>9</td>
      <td>10</td>
      <td>0</td>
    </tr>
  </tbody>
</table>
</div>

While k = 2 cluster 0 mostly converts into k = 4 cluster 3, k = 2 cluster 1 breaks down into ther other 3 clusters of k = 4.

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
      <td>1</td>
      <td>9</td>
      <td>4</td>
      <td>0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>10</td>
      <td>1</td>
      <td>6</td>
      <td>0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2</td>
      <td>1</td>
      <td>0</td>
      <td>16</td>
    </tr>
  </tbody>
</table>
</div>

While k = 3 cluster 2 mostly converts into k = 4 cluster 3, k = 4 cluster 2 becomes a middle zone for k = 3 cluster 0 and 1.

<a id="k4-features"></a>

#### Breakdown of results by features

- Cluster 1 teams show positiveness towards final third touches and passes into final third in central areas, shares of carries into the final third into central locations, and through balls attempted.
- Cluster 0 teams are the most direct, average higher shares of carries into the final third and touches in the final third in right locations, crosses attempted, and completed pass into the box being crosses.
- Cluster 2 teams counterpress more on opposition half and engage in defensive actions at higher locations, most of their carries into the final third end up in left locations, their goal kicks are longer on average, their pass into box shares are higher,
- Cluster 3 teams show lower shares of passes progressive and progression via passing, lower shares of counterpress actions in opposing half and lower defensive positions, lower directness per shot ending possession, lower shares of passes into box, while higher shares of passes into the final third and touches in the final third in left locations, average number of seconds from start of possession to shots, and progressive carries.

Hence,

- Similar to k = 3 cluster 2, k = 3 cluster 3 teams take a more patient approach
- Similar to k = 3 cluster 0, k = 4 cluster 1 teams combine plays more centrally
- Similar to k = 3 cluster 1, k = 4 cluster 0 teams are front footed teams that take a wider approach with crosses
- k = 4 cluster 2 teams are front footed teams that engage defensively higher while pass longer and more forward

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

<div style="page-break-after: always;"></div>

<a id="app-k2-build_up"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A6. Build-up radars, k = 2

<p align="center">
  <img src="../plots/teams/k2/build_up_raw.png" alt="Build-up radar, raw, k = 2" width="49%">
  <img src="../plots/teams/k2/build_up_adj.png" alt="Build-up radar, adjusted, k = 2" width="49%">
</p>
<p align="center"><em>Figure A6. Build-up traits of each cluster at k = 2: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k2-build_up-1"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A7. Build-up radars, k = 2: FA Women's Super League

<p align="center">
  <img src="../plots/teams/k2/build_up_raw_FA_Womens_Super_League.png" alt="Build-up radar, raw, FA Women's Super League, k = 2" width="49%">
  <img src="../plots/teams/k2/build_up_adj_FA_Womens_Super_League.png" alt="Build-up radar, adjusted, FA Women's Super League, k = 2" width="49%">
</p>
<p align="center"><em>Figure A7. Build-up traits of each cluster at k = 2, FA Women's Super League teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k2-build_up-2"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A8. Build-up radars, k = 2: Frauen Bundesliga

<p align="center">
  <img src="../plots/teams/k2/build_up_raw_Frauen_Bundesliga.png" alt="Build-up radar, raw, Frauen Bundesliga, k = 2" width="49%">
  <img src="../plots/teams/k2/build_up_adj_Frauen_Bundesliga.png" alt="Build-up radar, adjusted, Frauen Bundesliga, k = 2" width="49%">
</p>
<p align="center"><em>Figure A8. Build-up traits of each cluster at k = 2, Frauen Bundesliga teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k2-build_up-3"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A9. Build-up radars, k = 2: Liga F

<p align="center">
  <img src="../plots/teams/k2/build_up_raw_Liga_F.png" alt="Build-up radar, raw, Liga F, k = 2" width="49%">
  <img src="../plots/teams/k2/build_up_adj_Liga_F.png" alt="Build-up radar, adjusted, Liga F, k = 2" width="49%">
</p>
<p align="center"><em>Figure A9. Build-up traits of each cluster at k = 2, Liga F teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k2-build_up-4"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A10. Build-up radars, k = 2: Serie A Women

<p align="center">
  <img src="../plots/teams/k2/build_up_raw_Serie_A_Women.png" alt="Build-up radar, raw, Serie A Women, k = 2" width="49%">
  <img src="../plots/teams/k2/build_up_adj_Serie_A_Women.png" alt="Build-up radar, adjusted, Serie A Women, k = 2" width="49%">
</p>
<p align="center"><em>Figure A10. Build-up traits of each cluster at k = 2, Serie A Women teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k2-channels"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A11. Channels radars, k = 2

<p align="center">
  <img src="../plots/teams/k2/channels_raw.png" alt="Channels radar, raw, k = 2" width="49%">
  <img src="../plots/teams/k2/channels_adj.png" alt="Channels radar, adjusted, k = 2" width="49%">
</p>
<p align="center"><em>Figure A11. Channels traits of each cluster at k = 2: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k2-channels-1"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A12. Channels radars, k = 2: FA Women's Super League

<p align="center">
  <img src="../plots/teams/k2/channels_raw_FA_Womens_Super_League.png" alt="Channels radar, raw, FA Women's Super League, k = 2" width="49%">
  <img src="../plots/teams/k2/channels_adj_FA_Womens_Super_League.png" alt="Channels radar, adjusted, FA Women's Super League, k = 2" width="49%">
</p>
<p align="center"><em>Figure A12. Channels traits of each cluster at k = 2, FA Women's Super League teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k2-channels-2"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A13. Channels radars, k = 2: Frauen Bundesliga

<p align="center">
  <img src="../plots/teams/k2/channels_raw_Frauen_Bundesliga.png" alt="Channels radar, raw, Frauen Bundesliga, k = 2" width="49%">
  <img src="../plots/teams/k2/channels_adj_Frauen_Bundesliga.png" alt="Channels radar, adjusted, Frauen Bundesliga, k = 2" width="49%">
</p>
<p align="center"><em>Figure A13. Channels traits of each cluster at k = 2, Frauen Bundesliga teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k2-channels-3"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A14. Channels radars, k = 2: Liga F

<p align="center">
  <img src="../plots/teams/k2/channels_raw_Liga_F.png" alt="Channels radar, raw, Liga F, k = 2" width="49%">
  <img src="../plots/teams/k2/channels_adj_Liga_F.png" alt="Channels radar, adjusted, Liga F, k = 2" width="49%">
</p>
<p align="center"><em>Figure A14. Channels traits of each cluster at k = 2, Liga F teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k2-channels-4"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A15. Channels radars, k = 2: Serie A Women

<p align="center">
  <img src="../plots/teams/k2/channels_raw_Serie_A_Women.png" alt="Channels radar, raw, Serie A Women, k = 2" width="49%">
  <img src="../plots/teams/k2/channels_adj_Serie_A_Women.png" alt="Channels radar, adjusted, Serie A Women, k = 2" width="49%">
</p>
<p align="center"><em>Figure A15. Channels traits of each cluster at k = 2, Serie A Women teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k2-chance_creation"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A16. Chance creation radars, k = 2

<p align="center">
  <img src="../plots/teams/k2/chance_creation_raw.png" alt="Chance creation radar, raw, k = 2" width="49%">
  <img src="../plots/teams/k2/chance_creation_adj.png" alt="Chance creation radar, adjusted, k = 2" width="49%">
</p>
<p align="center"><em>Figure A16. Chance creation traits of each cluster at k = 2: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k2-chance_creation-1"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A17. Chance creation radars, k = 2: FA Women's Super League

<p align="center">
  <img src="../plots/teams/k2/chance_creation_raw_FA_Womens_Super_League.png" alt="Chance creation radar, raw, FA Women's Super League, k = 2" width="49%">
  <img src="../plots/teams/k2/chance_creation_adj_FA_Womens_Super_League.png" alt="Chance creation radar, adjusted, FA Women's Super League, k = 2" width="49%">
</p>
<p align="center"><em>Figure A17. Chance creation traits of each cluster at k = 2, FA Women's Super League teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k2-chance_creation-2"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A18. Chance creation radars, k = 2: Frauen Bundesliga

<p align="center">
  <img src="../plots/teams/k2/chance_creation_raw_Frauen_Bundesliga.png" alt="Chance creation radar, raw, Frauen Bundesliga, k = 2" width="49%">
  <img src="../plots/teams/k2/chance_creation_adj_Frauen_Bundesliga.png" alt="Chance creation radar, adjusted, Frauen Bundesliga, k = 2" width="49%">
</p>
<p align="center"><em>Figure A18. Chance creation traits of each cluster at k = 2, Frauen Bundesliga teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k2-chance_creation-3"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A19. Chance creation radars, k = 2: Liga F

<p align="center">
  <img src="../plots/teams/k2/chance_creation_raw_Liga_F.png" alt="Chance creation radar, raw, Liga F, k = 2" width="49%">
  <img src="../plots/teams/k2/chance_creation_adj_Liga_F.png" alt="Chance creation radar, adjusted, Liga F, k = 2" width="49%">
</p>
<p align="center"><em>Figure A19. Chance creation traits of each cluster at k = 2, Liga F teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k2-chance_creation-4"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A20. Chance creation radars, k = 2: Serie A Women

<p align="center">
  <img src="../plots/teams/k2/chance_creation_raw_Serie_A_Women.png" alt="Chance creation radar, raw, Serie A Women, k = 2" width="49%">
  <img src="../plots/teams/k2/chance_creation_adj_Serie_A_Women.png" alt="Chance creation radar, adjusted, Serie A Women, k = 2" width="49%">
</p>
<p align="center"><em>Figure A20. Chance creation traits of each cluster at k = 2, Serie A Women teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k2-pressing_transitions"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A21. Pressing and transitions radars, k = 2

<p align="center">
  <img src="../plots/teams/k2/pressing_transitions_raw.png" alt="Pressing and transitions radar, raw, k = 2" width="49%">
  <img src="../plots/teams/k2/pressing_transitions_adj.png" alt="Pressing and transitions radar, adjusted, k = 2" width="49%">
</p>
<p align="center"><em>Figure A21. Pressing and transitions traits of each cluster at k = 2: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k2-pressing_transitions-1"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A22. Pressing and transitions radars, k = 2: FA Women's Super League

<p align="center">
  <img src="../plots/teams/k2/pressing_transitions_raw_FA_Womens_Super_League.png" alt="Pressing and transitions radar, raw, FA Women's Super League, k = 2" width="49%">
  <img src="../plots/teams/k2/pressing_transitions_adj_FA_Womens_Super_League.png" alt="Pressing and transitions radar, adjusted, FA Women's Super League, k = 2" width="49%">
</p>
<p align="center"><em>Figure A22. Pressing and transitions traits of each cluster at k = 2, FA Women's Super League teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k2-pressing_transitions-2"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A23. Pressing and transitions radars, k = 2: Frauen Bundesliga

<p align="center">
  <img src="../plots/teams/k2/pressing_transitions_raw_Frauen_Bundesliga.png" alt="Pressing and transitions radar, raw, Frauen Bundesliga, k = 2" width="49%">
  <img src="../plots/teams/k2/pressing_transitions_adj_Frauen_Bundesliga.png" alt="Pressing and transitions radar, adjusted, Frauen Bundesliga, k = 2" width="49%">
</p>
<p align="center"><em>Figure A23. Pressing and transitions traits of each cluster at k = 2, Frauen Bundesliga teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k2-pressing_transitions-3"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A24. Pressing and transitions radars, k = 2: Liga F

<p align="center">
  <img src="../plots/teams/k2/pressing_transitions_raw_Liga_F.png" alt="Pressing and transitions radar, raw, Liga F, k = 2" width="49%">
  <img src="../plots/teams/k2/pressing_transitions_adj_Liga_F.png" alt="Pressing and transitions radar, adjusted, Liga F, k = 2" width="49%">
</p>
<p align="center"><em>Figure A24. Pressing and transitions traits of each cluster at k = 2, Liga F teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k2-pressing_transitions-4"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A25. Pressing and transitions radars, k = 2: Serie A Women

<p align="center">
  <img src="../plots/teams/k2/pressing_transitions_raw_Serie_A_Women.png" alt="Pressing and transitions radar, raw, Serie A Women, k = 2" width="49%">
  <img src="../plots/teams/k2/pressing_transitions_adj_Serie_A_Women.png" alt="Pressing and transitions radar, adjusted, Serie A Women, k = 2" width="49%">
</p>
<p align="center"><em>Figure A25. Pressing and transitions traits of each cluster at k = 2, Serie A Women teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k2-strength"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A26. Strength and dominance, k = 2

<p align="center">
  <img src="../plots/teams/k2/strength_dominance_strips.png" alt="Strength and dominance strips, k = 2" width="90%">
</p>
<p align="center"><em>Figure A26. Strength and dominance measures for every team, grouped by cluster, at k = 2.</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k2-strength-1"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A27. Strength and dominance by league, k = 2: FA Women's Super League and Frauen Bundesliga

<p align="center">
  <img src="../plots/teams/k2/strength_dominance_strips_FA_Womens_Super_League.png" alt="Strength and dominance, FA Women's Super League, k = 2" width="49%">
  <img src="../plots/teams/k2/strength_dominance_strips_Frauen_Bundesliga.png" alt="Strength and dominance, Frauen Bundesliga, k = 2" width="49%">
</p>
<p align="center"><em>Figure A27. Strength and dominance measures for every team, grouped by cluster, at k = 2, within FA Women's Super League (left) and Frauen Bundesliga (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k2-strength-2"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A28. Strength and dominance by league, k = 2: Liga F and Serie A Women

<p align="center">
  <img src="../plots/teams/k2/strength_dominance_strips_Liga_F.png" alt="Strength and dominance, Liga F, k = 2" width="49%">
  <img src="../plots/teams/k2/strength_dominance_strips_Serie_A_Women.png" alt="Strength and dominance, Serie A Women, k = 2" width="49%">
</p>
<p align="center"><em>Figure A28. Strength and dominance measures for every team, grouped by cluster, at k = 2, within Liga F (left) and Serie A Women (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k3-profile"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A29. Group profile, k = 3

<p align="center">
  <img src="../plots/teams/k3/group_profile.png" alt="Group profile, k = 3" width="90%">
</p>
<p align="center"><em>Figure A29. Headline traits by cluster at k = 3: dots after allowing for team strength, raw values in the table.</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k3-profile-1"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A30. Group profile by league, k = 3: FA Women's Super League and Frauen Bundesliga

<p align="center">
  <img src="../plots/teams/k3/group_profile_FA_Womens_Super_League.png" alt="Group profile, FA Women's Super League, k = 3" width="49%">
  <img src="../plots/teams/k3/group_profile_Frauen_Bundesliga.png" alt="Group profile, Frauen Bundesliga, k = 3" width="49%">
</p>
<p align="center"><em>Figure A30. Headline traits by cluster at k = 3, within FA Women's Super League (left) and Frauen Bundesliga (right): dots after allowing for team strength, raw values in the table. Each cluster rests on only a few teams per league.</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k3-profile-2"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A31. Group profile by league, k = 3: Liga F and Serie A Women

<p align="center">
  <img src="../plots/teams/k3/group_profile_Liga_F.png" alt="Group profile, Liga F, k = 3" width="49%">
  <img src="../plots/teams/k3/group_profile_Serie_A_Women.png" alt="Group profile, Serie A Women, k = 3" width="49%">
</p>
<p align="center"><em>Figure A31. Headline traits by cluster at k = 3, within Liga F (left) and Serie A Women (right): dots after allowing for team strength, raw values in the table. Each cluster rests on only a few teams per league.</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k3-build_up"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A32. Build-up radars, k = 3

<p align="center">
  <img src="../plots/teams/k3/build_up_raw.png" alt="Build-up radar, raw, k = 3" width="49%">
  <img src="../plots/teams/k3/build_up_adj.png" alt="Build-up radar, adjusted, k = 3" width="49%">
</p>
<p align="center"><em>Figure A32. Build-up traits of each cluster at k = 3: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k3-build_up-1"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A33. Build-up radars, k = 3: FA Women's Super League

<p align="center">
  <img src="../plots/teams/k3/build_up_raw_FA_Womens_Super_League.png" alt="Build-up radar, raw, FA Women's Super League, k = 3" width="49%">
  <img src="../plots/teams/k3/build_up_adj_FA_Womens_Super_League.png" alt="Build-up radar, adjusted, FA Women's Super League, k = 3" width="49%">
</p>
<p align="center"><em>Figure A33. Build-up traits of each cluster at k = 3, FA Women's Super League teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k3-build_up-2"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A34. Build-up radars, k = 3: Frauen Bundesliga

<p align="center">
  <img src="../plots/teams/k3/build_up_raw_Frauen_Bundesliga.png" alt="Build-up radar, raw, Frauen Bundesliga, k = 3" width="49%">
  <img src="../plots/teams/k3/build_up_adj_Frauen_Bundesliga.png" alt="Build-up radar, adjusted, Frauen Bundesliga, k = 3" width="49%">
</p>
<p align="center"><em>Figure A34. Build-up traits of each cluster at k = 3, Frauen Bundesliga teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k3-build_up-3"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A35. Build-up radars, k = 3: Liga F

<p align="center">
  <img src="../plots/teams/k3/build_up_raw_Liga_F.png" alt="Build-up radar, raw, Liga F, k = 3" width="49%">
  <img src="../plots/teams/k3/build_up_adj_Liga_F.png" alt="Build-up radar, adjusted, Liga F, k = 3" width="49%">
</p>
<p align="center"><em>Figure A35. Build-up traits of each cluster at k = 3, Liga F teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k3-build_up-4"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A36. Build-up radars, k = 3: Serie A Women

<p align="center">
  <img src="../plots/teams/k3/build_up_raw_Serie_A_Women.png" alt="Build-up radar, raw, Serie A Women, k = 3" width="49%">
  <img src="../plots/teams/k3/build_up_adj_Serie_A_Women.png" alt="Build-up radar, adjusted, Serie A Women, k = 3" width="49%">
</p>
<p align="center"><em>Figure A36. Build-up traits of each cluster at k = 3, Serie A Women teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k3-channels"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A37. Channels radars, k = 3

<p align="center">
  <img src="../plots/teams/k3/channels_raw.png" alt="Channels radar, raw, k = 3" width="49%">
  <img src="../plots/teams/k3/channels_adj.png" alt="Channels radar, adjusted, k = 3" width="49%">
</p>
<p align="center"><em>Figure A37. Channels traits of each cluster at k = 3: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k3-channels-1"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A38. Channels radars, k = 3: FA Women's Super League

<p align="center">
  <img src="../plots/teams/k3/channels_raw_FA_Womens_Super_League.png" alt="Channels radar, raw, FA Women's Super League, k = 3" width="49%">
  <img src="../plots/teams/k3/channels_adj_FA_Womens_Super_League.png" alt="Channels radar, adjusted, FA Women's Super League, k = 3" width="49%">
</p>
<p align="center"><em>Figure A38. Channels traits of each cluster at k = 3, FA Women's Super League teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k3-channels-2"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A39. Channels radars, k = 3: Frauen Bundesliga

<p align="center">
  <img src="../plots/teams/k3/channels_raw_Frauen_Bundesliga.png" alt="Channels radar, raw, Frauen Bundesliga, k = 3" width="49%">
  <img src="../plots/teams/k3/channels_adj_Frauen_Bundesliga.png" alt="Channels radar, adjusted, Frauen Bundesliga, k = 3" width="49%">
</p>
<p align="center"><em>Figure A39. Channels traits of each cluster at k = 3, Frauen Bundesliga teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k3-channels-3"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A40. Channels radars, k = 3: Liga F

<p align="center">
  <img src="../plots/teams/k3/channels_raw_Liga_F.png" alt="Channels radar, raw, Liga F, k = 3" width="49%">
  <img src="../plots/teams/k3/channels_adj_Liga_F.png" alt="Channels radar, adjusted, Liga F, k = 3" width="49%">
</p>
<p align="center"><em>Figure A40. Channels traits of each cluster at k = 3, Liga F teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k3-channels-4"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A41. Channels radars, k = 3: Serie A Women

<p align="center">
  <img src="../plots/teams/k3/channels_raw_Serie_A_Women.png" alt="Channels radar, raw, Serie A Women, k = 3" width="49%">
  <img src="../plots/teams/k3/channels_adj_Serie_A_Women.png" alt="Channels radar, adjusted, Serie A Women, k = 3" width="49%">
</p>
<p align="center"><em>Figure A41. Channels traits of each cluster at k = 3, Serie A Women teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k3-chance_creation"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A42. Chance creation radars, k = 3

<p align="center">
  <img src="../plots/teams/k3/chance_creation_raw.png" alt="Chance creation radar, raw, k = 3" width="49%">
  <img src="../plots/teams/k3/chance_creation_adj.png" alt="Chance creation radar, adjusted, k = 3" width="49%">
</p>
<p align="center"><em>Figure A42. Chance creation traits of each cluster at k = 3: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k3-chance_creation-1"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A43. Chance creation radars, k = 3: FA Women's Super League

<p align="center">
  <img src="../plots/teams/k3/chance_creation_raw_FA_Womens_Super_League.png" alt="Chance creation radar, raw, FA Women's Super League, k = 3" width="49%">
  <img src="../plots/teams/k3/chance_creation_adj_FA_Womens_Super_League.png" alt="Chance creation radar, adjusted, FA Women's Super League, k = 3" width="49%">
</p>
<p align="center"><em>Figure A43. Chance creation traits of each cluster at k = 3, FA Women's Super League teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k3-chance_creation-2"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A44. Chance creation radars, k = 3: Frauen Bundesliga

<p align="center">
  <img src="../plots/teams/k3/chance_creation_raw_Frauen_Bundesliga.png" alt="Chance creation radar, raw, Frauen Bundesliga, k = 3" width="49%">
  <img src="../plots/teams/k3/chance_creation_adj_Frauen_Bundesliga.png" alt="Chance creation radar, adjusted, Frauen Bundesliga, k = 3" width="49%">
</p>
<p align="center"><em>Figure A44. Chance creation traits of each cluster at k = 3, Frauen Bundesliga teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k3-chance_creation-3"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A45. Chance creation radars, k = 3: Liga F

<p align="center">
  <img src="../plots/teams/k3/chance_creation_raw_Liga_F.png" alt="Chance creation radar, raw, Liga F, k = 3" width="49%">
  <img src="../plots/teams/k3/chance_creation_adj_Liga_F.png" alt="Chance creation radar, adjusted, Liga F, k = 3" width="49%">
</p>
<p align="center"><em>Figure A45. Chance creation traits of each cluster at k = 3, Liga F teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k3-chance_creation-4"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A46. Chance creation radars, k = 3: Serie A Women

<p align="center">
  <img src="../plots/teams/k3/chance_creation_raw_Serie_A_Women.png" alt="Chance creation radar, raw, Serie A Women, k = 3" width="49%">
  <img src="../plots/teams/k3/chance_creation_adj_Serie_A_Women.png" alt="Chance creation radar, adjusted, Serie A Women, k = 3" width="49%">
</p>
<p align="center"><em>Figure A46. Chance creation traits of each cluster at k = 3, Serie A Women teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k3-pressing_transitions"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A47. Pressing and transitions radars, k = 3

<p align="center">
  <img src="../plots/teams/k3/pressing_transitions_raw.png" alt="Pressing and transitions radar, raw, k = 3" width="49%">
  <img src="../plots/teams/k3/pressing_transitions_adj.png" alt="Pressing and transitions radar, adjusted, k = 3" width="49%">
</p>
<p align="center"><em>Figure A47. Pressing and transitions traits of each cluster at k = 3: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k3-pressing_transitions-1"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A48. Pressing and transitions radars, k = 3: FA Women's Super League

<p align="center">
  <img src="../plots/teams/k3/pressing_transitions_raw_FA_Womens_Super_League.png" alt="Pressing and transitions radar, raw, FA Women's Super League, k = 3" width="49%">
  <img src="../plots/teams/k3/pressing_transitions_adj_FA_Womens_Super_League.png" alt="Pressing and transitions radar, adjusted, FA Women's Super League, k = 3" width="49%">
</p>
<p align="center"><em>Figure A48. Pressing and transitions traits of each cluster at k = 3, FA Women's Super League teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k3-pressing_transitions-2"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A49. Pressing and transitions radars, k = 3: Frauen Bundesliga

<p align="center">
  <img src="../plots/teams/k3/pressing_transitions_raw_Frauen_Bundesliga.png" alt="Pressing and transitions radar, raw, Frauen Bundesliga, k = 3" width="49%">
  <img src="../plots/teams/k3/pressing_transitions_adj_Frauen_Bundesliga.png" alt="Pressing and transitions radar, adjusted, Frauen Bundesliga, k = 3" width="49%">
</p>
<p align="center"><em>Figure A49. Pressing and transitions traits of each cluster at k = 3, Frauen Bundesliga teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k3-pressing_transitions-3"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A50. Pressing and transitions radars, k = 3: Liga F

<p align="center">
  <img src="../plots/teams/k3/pressing_transitions_raw_Liga_F.png" alt="Pressing and transitions radar, raw, Liga F, k = 3" width="49%">
  <img src="../plots/teams/k3/pressing_transitions_adj_Liga_F.png" alt="Pressing and transitions radar, adjusted, Liga F, k = 3" width="49%">
</p>
<p align="center"><em>Figure A50. Pressing and transitions traits of each cluster at k = 3, Liga F teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k3-pressing_transitions-4"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A51. Pressing and transitions radars, k = 3: Serie A Women

<p align="center">
  <img src="../plots/teams/k3/pressing_transitions_raw_Serie_A_Women.png" alt="Pressing and transitions radar, raw, Serie A Women, k = 3" width="49%">
  <img src="../plots/teams/k3/pressing_transitions_adj_Serie_A_Women.png" alt="Pressing and transitions radar, adjusted, Serie A Women, k = 3" width="49%">
</p>
<p align="center"><em>Figure A51. Pressing and transitions traits of each cluster at k = 3, Serie A Women teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k3-strength"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A52. Strength and dominance, k = 3

<p align="center">
  <img src="../plots/teams/k3/strength_dominance_strips.png" alt="Strength and dominance strips, k = 3" width="90%">
</p>
<p align="center"><em>Figure A52. Strength and dominance measures for every team, grouped by cluster, at k = 3.</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k3-strength-1"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A53. Strength and dominance by league, k = 3: FA Women's Super League and Frauen Bundesliga

<p align="center">
  <img src="../plots/teams/k3/strength_dominance_strips_FA_Womens_Super_League.png" alt="Strength and dominance, FA Women's Super League, k = 3" width="49%">
  <img src="../plots/teams/k3/strength_dominance_strips_Frauen_Bundesliga.png" alt="Strength and dominance, Frauen Bundesliga, k = 3" width="49%">
</p>
<p align="center"><em>Figure A53. Strength and dominance measures for every team, grouped by cluster, at k = 3, within FA Women's Super League (left) and Frauen Bundesliga (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k3-strength-2"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A54. Strength and dominance by league, k = 3: Liga F and Serie A Women

<p align="center">
  <img src="../plots/teams/k3/strength_dominance_strips_Liga_F.png" alt="Strength and dominance, Liga F, k = 3" width="49%">
  <img src="../plots/teams/k3/strength_dominance_strips_Serie_A_Women.png" alt="Strength and dominance, Serie A Women, k = 3" width="49%">
</p>
<p align="center"><em>Figure A54. Strength and dominance measures for every team, grouped by cluster, at k = 3, within Liga F (left) and Serie A Women (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k4-profile"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A55. Group profile, k = 4

<p align="center">
  <img src="../plots/teams/k4/group_profile.png" alt="Group profile, k = 4" width="90%">
</p>
<p align="center"><em>Figure A55. Headline traits by cluster at k = 4: dots after allowing for team strength, raw values in the table.</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k4-profile-1"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A56. Group profile by league, k = 4: FA Women's Super League and Frauen Bundesliga

<p align="center">
  <img src="../plots/teams/k4/group_profile_FA_Womens_Super_League.png" alt="Group profile, FA Women's Super League, k = 4" width="49%">
  <img src="../plots/teams/k4/group_profile_Frauen_Bundesliga.png" alt="Group profile, Frauen Bundesliga, k = 4" width="49%">
</p>
<p align="center"><em>Figure A56. Headline traits by cluster at k = 4, within FA Women's Super League (left) and Frauen Bundesliga (right): dots after allowing for team strength, raw values in the table. Each cluster rests on only a few teams per league.</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k4-profile-2"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A57. Group profile by league, k = 4: Liga F and Serie A Women

<p align="center">
  <img src="../plots/teams/k4/group_profile_Liga_F.png" alt="Group profile, Liga F, k = 4" width="49%">
  <img src="../plots/teams/k4/group_profile_Serie_A_Women.png" alt="Group profile, Serie A Women, k = 4" width="49%">
</p>
<p align="center"><em>Figure A57. Headline traits by cluster at k = 4, within Liga F (left) and Serie A Women (right): dots after allowing for team strength, raw values in the table. Each cluster rests on only a few teams per league.</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k4-build_up"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A58. Build-up radars, k = 4

<p align="center">
  <img src="../plots/teams/k4/build_up_raw.png" alt="Build-up radar, raw, k = 4" width="49%">
  <img src="../plots/teams/k4/build_up_adj.png" alt="Build-up radar, adjusted, k = 4" width="49%">
</p>
<p align="center"><em>Figure A58. Build-up traits of each cluster at k = 4: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k4-build_up-1"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A59. Build-up radars, k = 4: FA Women's Super League

<p align="center">
  <img src="../plots/teams/k4/build_up_raw_FA_Womens_Super_League.png" alt="Build-up radar, raw, FA Women's Super League, k = 4" width="49%">
  <img src="../plots/teams/k4/build_up_adj_FA_Womens_Super_League.png" alt="Build-up radar, adjusted, FA Women's Super League, k = 4" width="49%">
</p>
<p align="center"><em>Figure A59. Build-up traits of each cluster at k = 4, FA Women's Super League teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k4-build_up-2"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A60. Build-up radars, k = 4: Frauen Bundesliga

<p align="center">
  <img src="../plots/teams/k4/build_up_raw_Frauen_Bundesliga.png" alt="Build-up radar, raw, Frauen Bundesliga, k = 4" width="49%">
  <img src="../plots/teams/k4/build_up_adj_Frauen_Bundesliga.png" alt="Build-up radar, adjusted, Frauen Bundesliga, k = 4" width="49%">
</p>
<p align="center"><em>Figure A60. Build-up traits of each cluster at k = 4, Frauen Bundesliga teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k4-build_up-3"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A61. Build-up radars, k = 4: Liga F

<p align="center">
  <img src="../plots/teams/k4/build_up_raw_Liga_F.png" alt="Build-up radar, raw, Liga F, k = 4" width="49%">
  <img src="../plots/teams/k4/build_up_adj_Liga_F.png" alt="Build-up radar, adjusted, Liga F, k = 4" width="49%">
</p>
<p align="center"><em>Figure A61. Build-up traits of each cluster at k = 4, Liga F teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k4-build_up-4"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A62. Build-up radars, k = 4: Serie A Women

<p align="center">
  <img src="../plots/teams/k4/build_up_raw_Serie_A_Women.png" alt="Build-up radar, raw, Serie A Women, k = 4" width="49%">
  <img src="../plots/teams/k4/build_up_adj_Serie_A_Women.png" alt="Build-up radar, adjusted, Serie A Women, k = 4" width="49%">
</p>
<p align="center"><em>Figure A62. Build-up traits of each cluster at k = 4, Serie A Women teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k4-channels"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A63. Channels radars, k = 4

<p align="center">
  <img src="../plots/teams/k4/channels_raw.png" alt="Channels radar, raw, k = 4" width="49%">
  <img src="../plots/teams/k4/channels_adj.png" alt="Channels radar, adjusted, k = 4" width="49%">
</p>
<p align="center"><em>Figure A63. Channels traits of each cluster at k = 4: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k4-channels-1"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A64. Channels radars, k = 4: FA Women's Super League

<p align="center">
  <img src="../plots/teams/k4/channels_raw_FA_Womens_Super_League.png" alt="Channels radar, raw, FA Women's Super League, k = 4" width="49%">
  <img src="../plots/teams/k4/channels_adj_FA_Womens_Super_League.png" alt="Channels radar, adjusted, FA Women's Super League, k = 4" width="49%">
</p>
<p align="center"><em>Figure A64. Channels traits of each cluster at k = 4, FA Women's Super League teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k4-channels-2"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A65. Channels radars, k = 4: Frauen Bundesliga

<p align="center">
  <img src="../plots/teams/k4/channels_raw_Frauen_Bundesliga.png" alt="Channels radar, raw, Frauen Bundesliga, k = 4" width="49%">
  <img src="../plots/teams/k4/channels_adj_Frauen_Bundesliga.png" alt="Channels radar, adjusted, Frauen Bundesliga, k = 4" width="49%">
</p>
<p align="center"><em>Figure A65. Channels traits of each cluster at k = 4, Frauen Bundesliga teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k4-channels-3"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A66. Channels radars, k = 4: Liga F

<p align="center">
  <img src="../plots/teams/k4/channels_raw_Liga_F.png" alt="Channels radar, raw, Liga F, k = 4" width="49%">
  <img src="../plots/teams/k4/channels_adj_Liga_F.png" alt="Channels radar, adjusted, Liga F, k = 4" width="49%">
</p>
<p align="center"><em>Figure A66. Channels traits of each cluster at k = 4, Liga F teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k4-channels-4"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A67. Channels radars, k = 4: Serie A Women

<p align="center">
  <img src="../plots/teams/k4/channels_raw_Serie_A_Women.png" alt="Channels radar, raw, Serie A Women, k = 4" width="49%">
  <img src="../plots/teams/k4/channels_adj_Serie_A_Women.png" alt="Channels radar, adjusted, Serie A Women, k = 4" width="49%">
</p>
<p align="center"><em>Figure A67. Channels traits of each cluster at k = 4, Serie A Women teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k4-chance_creation"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A68. Chance creation radars, k = 4

<p align="center">
  <img src="../plots/teams/k4/chance_creation_raw.png" alt="Chance creation radar, raw, k = 4" width="49%">
  <img src="../plots/teams/k4/chance_creation_adj.png" alt="Chance creation radar, adjusted, k = 4" width="49%">
</p>
<p align="center"><em>Figure A68. Chance creation traits of each cluster at k = 4: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k4-chance_creation-1"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A69. Chance creation radars, k = 4: FA Women's Super League

<p align="center">
  <img src="../plots/teams/k4/chance_creation_raw_FA_Womens_Super_League.png" alt="Chance creation radar, raw, FA Women's Super League, k = 4" width="49%">
  <img src="../plots/teams/k4/chance_creation_adj_FA_Womens_Super_League.png" alt="Chance creation radar, adjusted, FA Women's Super League, k = 4" width="49%">
</p>
<p align="center"><em>Figure A69. Chance creation traits of each cluster at k = 4, FA Women's Super League teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k4-chance_creation-2"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A70. Chance creation radars, k = 4: Frauen Bundesliga

<p align="center">
  <img src="../plots/teams/k4/chance_creation_raw_Frauen_Bundesliga.png" alt="Chance creation radar, raw, Frauen Bundesliga, k = 4" width="49%">
  <img src="../plots/teams/k4/chance_creation_adj_Frauen_Bundesliga.png" alt="Chance creation radar, adjusted, Frauen Bundesliga, k = 4" width="49%">
</p>
<p align="center"><em>Figure A70. Chance creation traits of each cluster at k = 4, Frauen Bundesliga teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k4-chance_creation-3"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A71. Chance creation radars, k = 4: Liga F

<p align="center">
  <img src="../plots/teams/k4/chance_creation_raw_Liga_F.png" alt="Chance creation radar, raw, Liga F, k = 4" width="49%">
  <img src="../plots/teams/k4/chance_creation_adj_Liga_F.png" alt="Chance creation radar, adjusted, Liga F, k = 4" width="49%">
</p>
<p align="center"><em>Figure A71. Chance creation traits of each cluster at k = 4, Liga F teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k4-chance_creation-4"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A72. Chance creation radars, k = 4: Serie A Women

<p align="center">
  <img src="../plots/teams/k4/chance_creation_raw_Serie_A_Women.png" alt="Chance creation radar, raw, Serie A Women, k = 4" width="49%">
  <img src="../plots/teams/k4/chance_creation_adj_Serie_A_Women.png" alt="Chance creation radar, adjusted, Serie A Women, k = 4" width="49%">
</p>
<p align="center"><em>Figure A72. Chance creation traits of each cluster at k = 4, Serie A Women teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k4-pressing_transitions"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A73. Pressing and transitions radars, k = 4

<p align="center">
  <img src="../plots/teams/k4/pressing_transitions_raw.png" alt="Pressing and transitions radar, raw, k = 4" width="49%">
  <img src="../plots/teams/k4/pressing_transitions_adj.png" alt="Pressing and transitions radar, adjusted, k = 4" width="49%">
</p>
<p align="center"><em>Figure A73. Pressing and transitions traits of each cluster at k = 4: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k4-pressing_transitions-1"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A74. Pressing and transitions radars, k = 4: FA Women's Super League

<p align="center">
  <img src="../plots/teams/k4/pressing_transitions_raw_FA_Womens_Super_League.png" alt="Pressing and transitions radar, raw, FA Women's Super League, k = 4" width="49%">
  <img src="../plots/teams/k4/pressing_transitions_adj_FA_Womens_Super_League.png" alt="Pressing and transitions radar, adjusted, FA Women's Super League, k = 4" width="49%">
</p>
<p align="center"><em>Figure A74. Pressing and transitions traits of each cluster at k = 4, FA Women's Super League teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k4-pressing_transitions-2"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A75. Pressing and transitions radars, k = 4: Frauen Bundesliga

<p align="center">
  <img src="../plots/teams/k4/pressing_transitions_raw_Frauen_Bundesliga.png" alt="Pressing and transitions radar, raw, Frauen Bundesliga, k = 4" width="49%">
  <img src="../plots/teams/k4/pressing_transitions_adj_Frauen_Bundesliga.png" alt="Pressing and transitions radar, adjusted, Frauen Bundesliga, k = 4" width="49%">
</p>
<p align="center"><em>Figure A75. Pressing and transitions traits of each cluster at k = 4, Frauen Bundesliga teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k4-pressing_transitions-3"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A76. Pressing and transitions radars, k = 4: Liga F

<p align="center">
  <img src="../plots/teams/k4/pressing_transitions_raw_Liga_F.png" alt="Pressing and transitions radar, raw, Liga F, k = 4" width="49%">
  <img src="../plots/teams/k4/pressing_transitions_adj_Liga_F.png" alt="Pressing and transitions radar, adjusted, Liga F, k = 4" width="49%">
</p>
<p align="center"><em>Figure A76. Pressing and transitions traits of each cluster at k = 4, Liga F teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k4-pressing_transitions-4"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A77. Pressing and transitions radars, k = 4: Serie A Women

<p align="center">
  <img src="../plots/teams/k4/pressing_transitions_raw_Serie_A_Women.png" alt="Pressing and transitions radar, raw, Serie A Women, k = 4" width="49%">
  <img src="../plots/teams/k4/pressing_transitions_adj_Serie_A_Women.png" alt="Pressing and transitions radar, adjusted, Serie A Women, k = 4" width="49%">
</p>
<p align="center"><em>Figure A77. Pressing and transitions traits of each cluster at k = 4, Serie A Women teams only: raw (left) and after allowing for team strength (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k4-strength"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A78. Strength and dominance, k = 4

<p align="center">
  <img src="../plots/teams/k4/strength_dominance_strips.png" alt="Strength and dominance strips, k = 4" width="90%">
</p>
<p align="center"><em>Figure A78. Strength and dominance measures for every team, grouped by cluster, at k = 4.</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k4-strength-1"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A79. Strength and dominance by league, k = 4: FA Women's Super League and Frauen Bundesliga

<p align="center">
  <img src="../plots/teams/k4/strength_dominance_strips_FA_Womens_Super_League.png" alt="Strength and dominance, FA Women's Super League, k = 4" width="49%">
  <img src="../plots/teams/k4/strength_dominance_strips_Frauen_Bundesliga.png" alt="Strength and dominance, Frauen Bundesliga, k = 4" width="49%">
</p>
<p align="center"><em>Figure A79. Strength and dominance measures for every team, grouped by cluster, at k = 4, within FA Women's Super League (left) and Frauen Bundesliga (right).</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k4-strength-2"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A80. Strength and dominance by league, k = 4: Liga F and Serie A Women

<p align="center">
  <img src="../plots/teams/k4/strength_dominance_strips_Liga_F.png" alt="Strength and dominance, Liga F, k = 4" width="49%">
  <img src="../plots/teams/k4/strength_dominance_strips_Serie_A_Women.png" alt="Strength and dominance, Serie A Women, k = 4" width="49%">
</p>
<p align="center"><em>Figure A80. Strength and dominance measures for every team, grouped by cluster, at k = 4, within Liga F (left) and Serie A Women (right).</em></p>

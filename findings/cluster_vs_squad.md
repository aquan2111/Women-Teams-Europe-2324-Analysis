# Team clustering results vs Team squad composition

<a id="contents"></a>

## Contents

- [Team clustering results vs Team squad composition](#team-clustering-results-vs-team-squad-composition)
  - [Contents](#contents)
  - [Main question](#main-question)
  - [Do different clusters give different minutes to different player types?](#do-different-clusters-give-different-minutes-to-different-player-types)
  - [Do the same trends remain across leagues?](#do-the-same-trends-remain-across-leagues)
  - [Caveats](#caveats)
  - [Appendix](#appendix)
    - [A1. Squad mix by cluster, k = 2](#a1-squad-mix-by-cluster-k--2)
    - [A2. Player-type split by team, k = 2: goalkeeper and centre-back](#a2-player-type-split-by-team-k--2-goalkeeper-and-centre-back)
    - [A3. Player-type split by team, k = 2: full/wing-back and midfield](#a3-player-type-split-by-team-k--2-fullwing-back-and-midfield)
    - [A4. Midfield split by team, k = 2: hard types and sub-types](#a4-midfield-split-by-team-k--2-hard-types-and-sub-types)
    - [A5. Player-type split by team, k = 2: winger and centre-forward](#a5-player-type-split-by-team-k--2-winger-and-centre-forward)
    - [A6. Squad mix by cluster, k = 3](#a6-squad-mix-by-cluster-k--3)
    - [A7. Player-type split by team, k = 3: goalkeeper and centre-back](#a7-player-type-split-by-team-k--3-goalkeeper-and-centre-back)
    - [A8. Player-type split by team, k = 3: full/wing-back and midfield](#a8-player-type-split-by-team-k--3-fullwing-back-and-midfield)
    - [A9. Midfield split by team, k = 3: hard types and sub-types](#a9-midfield-split-by-team-k--3-hard-types-and-sub-types)
    - [A10. Player-type split by team, k = 3: winger and centre-forward](#a10-player-type-split-by-team-k--3-winger-and-centre-forward)
    - [A11. Squad mix by cluster, k = 4](#a11-squad-mix-by-cluster-k--4)
    - [A12. Player-type split by team, k = 4: goalkeeper and centre-back](#a12-player-type-split-by-team-k--4-goalkeeper-and-centre-back)
    - [A13. Player-type split by team, k = 4: full/wing-back and midfield](#a13-player-type-split-by-team-k--4-fullwing-back-and-midfield)
    - [A14. Midfield split by team, k = 4: hard types and sub-types](#a14-midfield-split-by-team-k--4-hard-types-and-sub-types)
    - [A15. Player-type split by team, k = 4: winger and centre-forward](#a15-player-type-split-by-team-k--4-winger-and-centre-forward)

<div style="page-break-after: always;"></div>

## Main question

Are team clusters and team squad composition related?

<a id="minutes-by-type"></a>

## Do different clusters give different minutes to different player types?

At k = 2,

- Patient teams give more minutes for short passing keepers and line holding center backs.
- Front-footed teams give more minutes for passing wingbacks, while patient teams give more minutes for deep full backs.
- While soft shares were quite even, in terms of hard shares, front-footed teams give more minutes to progressive passing central midfielders, while patient teams give more minutes to advanced carrying central midfielders.
- Patient teams give slightly more minutes for wide conservative carrying midfielders, while front-footed teams give slightly more minutes for advanced wingers.
- Patient teams give slightly more minutes for poachers, while front-footed teams give slightly more minutes to advanced forwards.

At k = 3,

- Direct teams show their front-footedness at the back, with more minutes for long passing keepers, stopper centerbacks, passing wingbacks, progressive passing central midfielders, and advanced forwards.
- Patient teams use short passing keepers, line holding center backs, deep full backs, deep pivot midfielders, advanced carrying central midfielders, wide conservative carrying midfielders.
- Passing teams do not show much squad signature, with only more minutes for short passing keepers.

At k = 4,

- Similar trends are observed in direct and patient teams
- Central teams have a similar squad to patient teams when it comes to the defence and central midfielders. They give fewer minutes to advanced wingers.
- Passing teams give more minutes to deep pivot center midfielders and less to advanced carrying center midfielders.

<a id="league-check"></a>

## Do the same trends remain across leagues?

A gap holds in a league when it points the same way there.

- At k = 2, every difference above 5 percent holds across all 4 leagues, except for deep pivot midfielders only in 2. Weaker but consistent signatures can be observed in wide conservative carrying midfielders, advanced forwards, and soft shares for progressive passing and advanced carrying central midfielders.
- For the patient group, the signature stays the same as k go up.
- At k = 3, the direct cluster's progressive passers, stopper center backs, and advanced forwards types hold in all 4 leagues, while its long passing keepers and fewer advanced carriers hold in 3 leagues. The passing cluster's short passing keepers hold in all 4.
- At k = 4, similar trends can be observed for the direct cluster, with an additon of more passing wing backs consistent across 3 leagues. The central cluster's keepers and center backs hold in all 4 leagues, while its central midfield and winger differences in 3. The passing cluster's two differences hold in 3 leagues.

<a id="caveats"></a>

## Caveats

- Team style is made up of players' own actions, so the link between squad and style is partly automatic.
- The results do not show whether clubs pick players to suit a style or coaches fit the style to the players they have.
- 10 clubs have no clustered wingers, and 2 clubs have no clustered center forwards, so they sit out.
- Midfield difference is only seen in hard shares rather than soft, as midfielders' similarity scores are spread evenly across three types.
- At k = 3 and k = 4 the clusters are small, especially with the central cluster only having 1 to 3 teams per league at k = 4.

<div style="page-break-after: always;"></div>

<a id="appendix"></a>

## Appendix

<a id="app-k2-mix"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A1. Squad mix by cluster, k = 2

<p align="center">
  <img src="../plots/teams/k2/type_shares_by_group.png" alt="Squad mix by cluster, k = 2" width="85%">
</p>
<p align="center"><em>Figure A1. Each cluster's share of minutes by player type at k = 2, against the 50-team average.</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k2-goalkeeper"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A2. Player-type split by team, k = 2: goalkeeper and centre-back

<p align="center">
  <img src="../plots/teams/k2/type_shares_teams_Goalkeeper.png" alt="Player-type split by team, goalkeeper, k = 2" width="49%">
  <img src="../plots/teams/k2/type_shares_teams_Center_Back.png" alt="Player-type split by team, centre-back, k = 2" width="49%">
</p>
<p align="center"><em>Figure A2. Every team's split of goalkeeper (left) and centre-back (right) minutes across player types at k = 2, teams grouped by cluster.</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k2-fullwing_back"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A3. Player-type split by team, k = 2: full/wing-back and midfield

<p align="center">
  <img src="../plots/teams/k2/type_shares_teams_FullWing_Back.png" alt="Player-type split by team, full/wing-back, k = 2" width="49%">
  <img src="../plots/teams/k2/type_shares_teams_Center_Midfield.png" alt="Player-type split by team, midfield, k = 2" width="49%">
</p>
<p align="center"><em>Figure A3. Every team's split of full/wing-back (left) and midfield (right) minutes across player types at k = 2, teams grouped by cluster. Shares are soft shares, so the midfield difference seen in hard shares shows less here.</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k2-midfield"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A4. Midfield split by team, k = 2: hard types and sub-types

<p align="center">
  <img src="../plots/teams/k2/type_shares_teams_Center_Midfield_hard.png" alt="Midfield split by team, hard types, k = 2" width="49%">
  <img src="../plots/teams/k2/type_shares_teams_Center_Midfield_sub.png" alt="Midfield split by team, sub-types, k = 2" width="49%">
</p>
<p align="center"><em>Figure A4. Every team's split of midfield minutes at k = 2, teams grouped by cluster: hard types, with each midfielder counted as a single type (left), and midfield sub-types (right). This is where the midfield difference between styles shows.</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k2-winger"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A5. Player-type split by team, k = 2: winger and centre-forward

<p align="center">
  <img src="../plots/teams/k2/type_shares_teams_Winger.png" alt="Player-type split by team, winger, k = 2" width="49%">
  <img src="../plots/teams/k2/type_shares_teams_Center_Forward.png" alt="Player-type split by team, centre-forward, k = 2" width="49%">
</p>
<p align="center"><em>Figure A5. Every team's split of winger (left) and centre-forward (right) minutes across player types at k = 2, teams grouped by cluster.</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k3-mix"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A6. Squad mix by cluster, k = 3

<p align="center">
  <img src="../plots/teams/k3/type_shares_by_group.png" alt="Squad mix by cluster, k = 3" width="70%">
</p>
<p align="center"><em>Figure A6. Each cluster's share of minutes by player type at k = 3, against the 50-team average.</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k3-goalkeeper"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A7. Player-type split by team, k = 3: goalkeeper and centre-back

<p align="center">
  <img src="../plots/teams/k3/type_shares_teams_Goalkeeper.png" alt="Player-type split by team, goalkeeper, k = 3" width="49%">
  <img src="../plots/teams/k3/type_shares_teams_Center_Back.png" alt="Player-type split by team, centre-back, k = 3" width="49%">
</p>
<p align="center"><em>Figure A7. Every team's split of goalkeeper (left) and centre-back (right) minutes across player types at k = 3, teams grouped by cluster.</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k3-fullwing_back"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A8. Player-type split by team, k = 3: full/wing-back and midfield

<p align="center">
  <img src="../plots/teams/k3/type_shares_teams_FullWing_Back.png" alt="Player-type split by team, full/wing-back, k = 3" width="49%">
  <img src="../plots/teams/k3/type_shares_teams_Center_Midfield.png" alt="Player-type split by team, midfield, k = 3" width="49%">
</p>
<p align="center"><em>Figure A8. Every team's split of full/wing-back (left) and midfield (right) minutes across player types at k = 3, teams grouped by cluster. Shares are soft shares, so the midfield difference seen in hard shares shows less here.</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k3-midfield"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A9. Midfield split by team, k = 3: hard types and sub-types

<p align="center">
  <img src="../plots/teams/k3/type_shares_teams_Center_Midfield_hard.png" alt="Midfield split by team, hard types, k = 3" width="49%">
  <img src="../plots/teams/k3/type_shares_teams_Center_Midfield_sub.png" alt="Midfield split by team, sub-types, k = 3" width="49%">
</p>
<p align="center"><em>Figure A9. Every team's split of midfield minutes at k = 3, teams grouped by cluster: hard types, with each midfielder counted as a single type (left), and midfield sub-types (right). This is where the midfield difference between styles shows.</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k3-winger"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A10. Player-type split by team, k = 3: winger and centre-forward

<p align="center">
  <img src="../plots/teams/k3/type_shares_teams_Winger.png" alt="Player-type split by team, winger, k = 3" width="49%">
  <img src="../plots/teams/k3/type_shares_teams_Center_Forward.png" alt="Player-type split by team, centre-forward, k = 3" width="49%">
</p>
<p align="center"><em>Figure A10. Every team's split of winger (left) and centre-forward (right) minutes across player types at k = 3, teams grouped by cluster.</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k4-mix"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A11. Squad mix by cluster, k = 4

<p align="center">
  <img src="../plots/teams/k4/type_shares_by_group.png" alt="Squad mix by cluster, k = 4" width="55%">
</p>
<p align="center"><em>Figure A11. Each cluster's share of minutes by player type at k = 4, against the 50-team average.</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k4-goalkeeper"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A12. Player-type split by team, k = 4: goalkeeper and centre-back

<p align="center">
  <img src="../plots/teams/k4/type_shares_teams_Goalkeeper.png" alt="Player-type split by team, goalkeeper, k = 4" width="49%">
  <img src="../plots/teams/k4/type_shares_teams_Center_Back.png" alt="Player-type split by team, centre-back, k = 4" width="49%">
</p>
<p align="center"><em>Figure A12. Every team's split of goalkeeper (left) and centre-back (right) minutes across player types at k = 4, teams grouped by cluster.</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k4-fullwing_back"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A13. Player-type split by team, k = 4: full/wing-back and midfield

<p align="center">
  <img src="../plots/teams/k4/type_shares_teams_FullWing_Back.png" alt="Player-type split by team, full/wing-back, k = 4" width="49%">
  <img src="../plots/teams/k4/type_shares_teams_Center_Midfield.png" alt="Player-type split by team, midfield, k = 4" width="49%">
</p>
<p align="center"><em>Figure A13. Every team's split of full/wing-back (left) and midfield (right) minutes across player types at k = 4, teams grouped by cluster. Shares are soft shares, so the midfield difference seen in hard shares shows less here.</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k4-midfield"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A14. Midfield split by team, k = 4: hard types and sub-types

<p align="center">
  <img src="../plots/teams/k4/type_shares_teams_Center_Midfield_hard.png" alt="Midfield split by team, hard types, k = 4" width="49%">
  <img src="../plots/teams/k4/type_shares_teams_Center_Midfield_sub.png" alt="Midfield split by team, sub-types, k = 4" width="49%">
</p>
<p align="center"><em>Figure A14. Every team's split of midfield minutes at k = 4, teams grouped by cluster: hard types, with each midfielder counted as a single type (left), and midfield sub-types (right). This is where the midfield difference between styles shows.</em></p>

<div style="page-break-after: always;"></div>

<a id="app-k4-winger"></a>
<p align="right"><a href="#contents">&#8593; Back to contents</a></p>

### A15. Player-type split by team, k = 4: winger and centre-forward

<p align="center">
  <img src="../plots/teams/k4/type_shares_teams_Winger.png" alt="Player-type split by team, winger, k = 4" width="49%">
  <img src="../plots/teams/k4/type_shares_teams_Center_Forward.png" alt="Player-type split by team, centre-forward, k = 4" width="49%">
</p>
<p align="center"><em>Figure A15. Every team's split of winger (left) and centre-forward (right) minutes across player types at k = 4, teams grouped by cluster.</em></p>

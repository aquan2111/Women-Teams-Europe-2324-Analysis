# Team clustering results vs Team squad composition

<a id="contents"></a>

## Contents

- [Do different clusters give different minutes to different player types?](#minutes-by-type)
- [Do the same trends remain across leagues?](#league-check)
- [Caveats](#caveats)
- [Appendix](#appendix)
  - **k = 2:** [A1. Squad mix](#app-k2-mix) · [A2. Goalkeeper and centre-back](#app-k2-goalkeeper) · [A3. Full/wing-back and midfield](#app-k2-fullwing_back) · [A4. Midfield: hard types and sub-types](#app-k2-midfield) · [A5. Winger and centre-forward](#app-k2-winger)
  - **k = 3:** [A6. Squad mix](#app-k3-mix) · [A7. Goalkeeper and centre-back](#app-k3-goalkeeper) · [A8. Full/wing-back and midfield](#app-k3-fullwing_back) · [A9. Midfield: hard types and sub-types](#app-k3-midfield) · [A10. Winger and centre-forward](#app-k3-winger)
  - **k = 4:** [A11. Squad mix](#app-k4-mix) · [A12. Goalkeeper and centre-back](#app-k4-goalkeeper) · [A13. Full/wing-back and midfield](#app-k4-fullwing_back) · [A14. Midfield: hard types and sub-types](#app-k4-midfield) · [A15. Winger and centre-forward](#app-k4-winger)

<div style="page-break-after: always;"></div>

## Main question

Are team clusters and team squad composition related?

<a id="minutes-by-type"></a>

## Do different clusters give different minutes to different player types?

At k = 2,

- Patient teams give more minutes for short passing keepers and line holding center backs.
- Front-footed teams give more minutes for passing wingbacks, while patient teams give more minutes for deep full backs.
- While soft shares were quite even, in terms of hard shares, front-footed teams give more minutes to progressive passing midfielders, while patient teams give more minutes to deep pivot midfielders and advanced carrying midfielders.
- Patient teams give more minutes for wide conservative carrying midfielders, while front-footed teams give more minutes for wide playmakers.
- Patient teams give more minutes for poachers, while front-footed teams give more minutes to advanced forwards.

At k = 3,

- Similar trends at the back can be seen as k = 2.
- Central combiners give more minutes to progressive passers but fewer to deep pivot midfielders.
- Central combiners give more minutes to wide playmakers, while wide crossers give more minutes to advanced wingers.
- Wide crossers give fewer minutes to poachers, but more to advanced forwards and target forwards.

At k = 4,

- High pressers show their front-footedness in more minutes to long passing keepers, stopper center backs, and progressive passers.

<a id="league-check"></a>

## Do the same trends remain across leagues?

A difference counts when it is at least 5 percent and points the same way in at least 3 of the 4 leagues.

- At k = 2, the patient/front-foot squad differences hold across leagues: patient teams give more minutes to advanced carriers, line holding center backs, and short passing keepers, while fewer minutes to progressive passers and progressive passing wingbacks.
- The signature for patient group remains the same throughout different values of k.
- At k = 3, central combiners give more minutes to progressive passers rather than deep pivots and more minutes to wide playmakers, while wide crossers give fewer minutes to advanced carriers and poachers.
- At k = 4, high pressing teams have more long passing keepers and stopper center backs but fewer advanced carriers.

Therefore, the squad pattern is mostly consistent among patient and front-footed teams, while differences among front-footed styles were smaller but still consistent across different leagues.

<a id="caveats"></a>

## Caveats

- Team style is made up of players' own actions, so the link between squad and style is automatic.
- 10 clubs have no clustered wingers, and 2 clubs have no clustered center forwards, so they sit out.
- Midfield difference is only seen in hard shares rather than soft, as midfielders' similarity scores are spread evenly across three types.

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

# Team clustering results vs Team style distance

In this section, we will examine the relationship between team clusters and distance between teams in terms of playing style.

Among 50 teams, there are 1225 team pairs.

Taking the closest 10% of team pairs gives 123 pairs.

## Do teams that play alike get clustered in the same cluster?

If teams were put in clusters at random while cluster sizes are preserved,

- 51% of pairs would land in the same cluster for k = 2
- 32% of pairs would land in the same cluster for k = 3
- 24% of pairs would land in the same cluster for k = 4

Among the 123 close pairs,

- 95 pairs (77%) landed in the same cluster for k = 2
- 90 pairs (73%) landed in the same cluster for k = 3
- 69 pairs (56%) landed in the same cluster for k = 4

The margins of difference in terms of similarity for close teams are also quite close, in particular,

- For k = 2, a typical gap between two close teams is 0.08, while between any two teams is 0.21
- For k = 3, a typical gap between two close teams is 0.10, while between any two teams is 0.26
- For k = 4, a typical gap between two close teams is 0.12, while between any two teams is 0.27

Therefore, teams play alike mostly land in the same cluster, well above chance. The agreement is stronger at k = 2 and k = 3.

## How tight are clusters

- For patient teams (k = 2 cluster 0, k = 3 cluster 2, k = 4 cluster 3), most teams have many neighbours, which can be even 6 or 7, or even up to 14. Most neighbours end up landing in the same cluster. On the other hand, most front foot teams (k = 2 cluster 1, k = 3 clusters 0 and 1, k = 4 cluster 0, 1, and 2) have fewer neighbours (4 or less). However there are a few teams with more neighbours than patient teams, which include Barcelona WFC (19) and SC Freiburg (15). Eventually these teams sit near the center of the style map.
- There are 6 teams without neighbours, 5 of them were front footed (SD Eibar, AS Roma W, RB Leipzig W, Nurnberg W, and SGS Essen 19/68). The other team that landed in patient cluster was Madrid CFF. Also, some of these teams were firm members within their clusters (SD Eibar at k = 2, Nurnberg W at k = 3 and k = 4, AS Roma for all k).
- Therefore, while patient teams can be quite similar, which can be seen in how they remained consistent throughout all values of k, front footed teams are more varied in how they play.

## Where do clusters meet?

Among 123 pairs of close distance,

- At k = 2, 28 pairs cross the patient/front-foot border (5% of the pairs across it). Close pairs are more common among patient cluster (54 out of 190 - 28%), while rarer among front-foot cluster (41 out of 435 - 9%).
- At k = 3, most cross cluster closeness happens between patient and wide crosser teams (23 pairs - 7% of the pairs between them). Central combiners rarely touch patient cluster (3 pairs - 1%) and only sometimes wide crossers (7 pairs - 3%).
- At k = 4, the high pressers are furthest from the patient cluster (4 close pairs - 3%), while central combiners touch patient teams most (17 close pairs - 10%), which mostly come from Barcelona and Hoffenheim joining while being close to patient teams.
- Teams that sit at the border at every k include Barcelona, Bayern, Hoffenheim, Freiburg, and Inter, while Duisburg sits at the border at k = 2.
- Consequently, at k = 3 the style runs from patient to wide crossers to central combiners, while at k = 4 the high pressers sit furthest from patient play, and a small set of teams sit where clusters meet.

## Similarity gap vs Distance

The similarity gap is the share of similarity that would have to move to turn one team's scores into the other's, with 0 being same leaning and 1 being opposite.

- At all k, the further apart two teams play, the further apart are their similarity scores. The typical gap for the closest tenth of pairs is 0.04 at k = 2, 0.08 at k = 3, and 0.10 at k = 4, against 0.20, 0.26, and 0.31 for the furthest tenth.
- At k = 2, the gap was flat across the closest third of pairs, before rising more steadily after.
- On the other hand, at k = 3 and k = 4, the rise is more steady as more clusters tell what kind of front foot a team resembles.
- The link runs one way, as teams that play alike tend to have similar scores, but similar scores do not mean similar playstyle, as shown in k = 2 how many front-foot pairs played differently but ended up with near identical scores.
- Hence, a large gap in similarity scores mean two teams play differently, while a small gap only indicates that the two teams lean the same way. At higher k, gaps are large because there are more clusters to differ accross, so comparisons are only valid within each k rather than across different values of k.

## Do teams stay in their cluster as k goes up?

A team "moves" when it leaves the cluster that most of its previous cluster went to.

- The patient cluster was stable throughout, with 16 teams staying at every k.
- At k = 3, Tottenham went from patient to central combiners, Duisburg went from patient to wide crossers, Inter went from front-foot to patient.
- 5 teams move at k = 4. Barcelona went from wide crossers to central combiners, while the other way was seen in Wolfsburg. From the patient cluster, Manchester City and Inter went to crossers, while Hoffenheim to central combiners. The high-pressing cluster was drawn from both front-foot clusters.
- Barcelona, Inter, and Hoffenheim sit between clusters at every k. Inter was only side that switched sides twice (front foot to patient then back to front foot).
- Subsequently, while the patient cluster holds across every k, front foot teams shuffle as k grows.

## Appendix

<p align="right"><a href="#team-clustering-results-vs-team-style-distance">&#8593; Back to main text</a></p>

### A1. Team paths across k

<p align="center">
  <img src="../plots/teams/all_k/team_paths.png" alt="Team paths from k = 2 to k = 4" width="65%">
</p>
<p align="center"><em>Figure A1. Each team's cluster from k = 2 to k = 4. A team moves when it leaves the cluster that most of its previous cluster went to; 16 teams stay patient at every k.</em></p>

<div style="page-break-after: always;"></div>

<p align="right"><a href="#team-clustering-results-vs-team-style-distance">&#8593; Back to main text</a></p>

### A2. k = 2

<p align="center">
  <img src="../plots/teams/k2/close_teams.png" alt="Close teams strip, k = 2" width="49%">
  <img src="../plots/teams/k2/similarity_gap_vs_distance.png" alt="Similarity gap vs style distance, k = 2" width="49%">
</p>
<p align="center"><em>Figure A2. Left: each team's lead for its own cluster, with the teams close to it in style (open markers) scored on the same cluster. Right: similarity gap against style distance for all 1,225 pairs. At k = 2, 95 of the 123 close pairs share a cluster (77%, against 51% by chance), and the typical similarity gap is 0.04 for the closest tenth of pairs against 0.20 for the furthest.</em></p>

<div style="page-break-after: always;"></div>

<p align="right"><a href="#team-clustering-results-vs-team-style-distance">&#8593; Back to main text</a></p>

### A3. k = 3

<p align="center">
  <img src="../plots/teams/k3/close_teams.png" alt="Close teams strip, k = 3" width="49%">
  <img src="../plots/teams/k3/similarity_gap_vs_distance.png" alt="Similarity gap vs style distance, k = 3" width="49%">
</p>
<p align="center"><em>Figure A3. Left: each team's lead for its own cluster at k = 3, with the teams close to it in style (open markers) scored on the same cluster. Right: similarity gap against style distance for all 1,225 pairs. 90 of the 123 close pairs share a cluster (73%, against 32% by chance), and the typical similarity gap is 0.08 for the closest tenth of pairs against 0.26 for the furthest.</em></p>

<div style="page-break-after: always;"></div>

<p align="right"><a href="#team-clustering-results-vs-team-style-distance">&#8593; Back to main text</a></p>

### A4. k = 4

<p align="center">
  <img src="../plots/teams/k4/close_teams.png" alt="Close teams strip, k = 4" width="49%">
  <img src="../plots/teams/k4/similarity_gap_vs_distance.png" alt="Similarity gap vs style distance, k = 4" width="49%">
</p>
<p align="center"><em>Figure A4. Left: each team's lead for its own cluster at k = 4, with the teams close to it in style (open markers) scored on the same cluster. Right: similarity gap against style distance for all 1,225 pairs. 69 of the 123 close pairs share a cluster (56%, against 24% by chance), and the typical similarity gap is 0.10 for the closest tenth of pairs against 0.31 for the furthest.</em></p>

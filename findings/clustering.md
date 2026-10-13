# Team Clustering Results

## Team breakdown

In this project, there are 50 teams considered, with

- 12 teams in the English FA Women's Super League
- 12 teams in the German Frauen Bundesliga
- 16 teams in the Spanish Liga F
- 10 teams in the Italian Serie A Women

## Results

### Results for 2 clusters

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

#### Breakdown of results by features

- Cluster 0 teams stand out for shares of passes into the final third and touches in the final third in left locations, average number of seconds from start of possession to shots, shot share from open play, and shares of progressive carries.
- Meanwhile, cluster 1 teams have higher shares of passes being progressive and higher shares of progression done via passing, average defensive x location, counterpress actions in opposition half, average directness per possession, shares of passes into the final third and and touches in the final third in central locations, shares of box entries by passes, and shots shares from transitions and counters.

Therefore, it can be concluded that

- Cluster 0 teams are more patient when building up
- Cluster 1 teams take a more front footed approach

### Results for 3 clusters

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

#### Breakdown of results by features

- Cluster 0 teams show positiveness towards final third touches and passes into final third in central areas, shares of carries into the final third into central locations, and through balls attempted.
- Cluster 1 teams counterpress more on opposition half and engage in defensive actions at higher locations, shares of carries into the final third and touches in the final third in right locations, pass into box share, crosses attempted, and completed pass into the box being crosses.
- Cluster 2 teams show lower shares of passes progressive and progression via passing, lower shares of counterpress actions in opposing half and lower defensive positions, lower directness per shot ending possession, lower shares of passes into box, while higher shares of passes into the final third and touches in the final third in left locations, average number of seconds from start of possession to shots, and progressive carries.

Consequently,

- Similar to k = 2 cluster 0, k = 3 cluster 2 teams take a more patient approach
- k = 3 cluster 0 are front footed teams that combine plays more centrally
- k = 3 cluster 1 are front footed teams that take a wider approach with crosses

### Results for 4 clusters

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

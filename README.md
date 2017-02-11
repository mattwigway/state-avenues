# State Avenues

One of my bucket-list items before I leave the District of Columbia to go to grad school is to visit
each of the [state-named avenues in DC](https://en.wikipedia.org/wiki/List_of_state-named_roadways_in_Washington,_D.C.).
The District has one Avenue for every state (except Ohio and California; Ohio is a Drive and California
is a Street). There is also a Columbia Road, which [is not named for the District](https://en.wikipedia.org/wiki/Columbia_Road)
but we'll go ahead and count it anyhow since DC should be a state (taxation without representation is
tyranny).

Now I want to visit all these roads in the optimal manner (if it wasn't obvious, I'm going to grad school for
a PhD in computational geography). This is a [Traveling Salesman Problem](https://en.wikipedia.org/wiki/Travelling_salesman_problem),
a well-studied but NP-hard optimization problem. However, fast near-optimal heuristic solvers exist.

One more wrinkle is that the locations I wish to visit are not points; I am happy to visit any part
of a particular road. We can reduce this a set traveling salesman problem by observing that to visit
any part of a state-named avenue I must access it via an intersection. Therefore, I can find all the
intersections along each avenue and treat them as a set of locations, one of each of which I must
visit. This is what is known as the [Set Traveling Salesman Problem](https://en.wikipedia.org/wiki/Set_TSP_problem),
a generalization of the traveling salesman problem and a special case of the [Traveling Purchaser Problem](https://en.wikipedia.org/wiki/Traveling_purchaser_problem).

The set traveling salesman problem can be transformed into a standard traveling salesman problem using
the algorithm described in [Noon and Bean 1993](https://www.researchgate.net/publication/265366022_An_Efficient_Transformation_Of_The_Generalized_Traveling_Salesman_Problem).
TODO description of transformation

We can then solve the optimization problem using the efficient solvers in Google's [or-tools](https://developers.google.com/optimization/).

To construct the network over which the problem will operate, we first download [OpenStreetMap](https://osm.org)
data for the District of Columbia from [Geofabrik](http://download.geofabrik.de/north-america.html).

# Usage

## Extract intersections

First, we need to extract intersections. To do that, run

    extract_intersections.py dc.osm.pbf states.csv intersections.json

Voila! Intersections are in the GeoJSON. That was easy.

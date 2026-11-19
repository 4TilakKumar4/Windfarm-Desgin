# Undirected, selected-vertex flow formulation from the project handout.
set V ordered;
set E within V cross V;
set F within V;
set P within V;
param r in F;
param c {E} >= 0;
param w {V} >= 0 default 0;
param q {P} >= 0;
param Q >= 0;
param M := card(V)-1;

var x {E} binary;
var z {V} binary;
# For stored edge (u,v), forward is u->v and reverse is v->u.
var forward {E} >= 0;
var reverse {E} >= 0;

minimize Investment:
    sum {(u,v) in E} c[u,v]*x[u,v] + sum {v in V} w[v]*z[v];
subject to Fixed {v in F}: z[v] = 1;
subject to EndpointU {(u,v) in E}: x[u,v] <= z[u];
subject to EndpointV {(u,v) in E}: x[u,v] <= z[v];
subject to Capacity {(u,v) in E}:
    forward[u,v] + reverse[u,v] <= M*x[u,v];
subject to Balance {v in V diff {r}}:
    sum {(u,v) in E} (forward[u,v]-reverse[u,v])
  + sum {(v,u) in E} (reverse[v,u]-forward[v,u]) = z[v];
subject to RootBalance:
    sum {(r,u) in E} (forward[r,u]-reverse[r,u])
  + sum {(u,r) in E} (reverse[u,r]-forward[u,r])
    = sum {v in V diff {r}} z[v];
subject to TreeSize: sum {(u,v) in E} x[u,v] = sum {v in V} z[v]-1;
subject to EnergyQuota: sum {v in P} q[v]*z[v] >= Q;

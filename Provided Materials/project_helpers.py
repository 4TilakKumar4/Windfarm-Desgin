"""Data preparation and independent solution checks"""
from pathlib import Path
import json
import math


def export_and_validate(ampl, output_dir, tag):
    """Check selected subgraph independently; export only selected edges/nodes."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    # Filter inside AMPL: do not transfer millions of unselected edges to Python.
    import pandas as pd
    if ampl.get_value('solve_result') in {'infeasible', 'unbounded', 'failure'}:
        raise ValueError('Solver did not return a usable solution; inspect solve_message.')
    if ampl.get_value('sum {(u,v) in E} (if x[u,v] > 0.5 then 1 else 0)'):
        edges = ampl.get_data('{(u,v) in E: x[u,v] > 0.5} c[u,v]').to_pandas()
    else:
        edges = pd.DataFrame({'cost': []}, index=pd.MultiIndex.from_tuples([], names=['u','v']))
    if not ampl.get_value('sum {v in V} (if z[v] > 0.5 then 1 else 0)'):
        raise ValueError('No selected vertices; inspect the solver message for a feasible solution.')
    nodes = ampl.get_data('{v in V: z[v] > 0.5} w[v]').to_pandas()
    selected = set(int(v) for v in nodes.index)
    fixed = {int(v) for v in ampl.get_set('F').get_values().to_list()}
    profits = ({int(v): float(q) for v, q in ampl.get_parameter('q').get_values().to_list()}
               if ampl.get_value('card(P)') else {})
    parent = {v: v for v in selected}
    def find(v):
        while parent[v] != v:
            parent[v] = parent[parent[v]]
            v = parent[v]
        return v
    acyclic = True
    for u, v in edges.index:
        u, v = int(u), int(v)
        if u not in selected or v not in selected: raise ValueError('Unselected endpoint')
        a, b = find(u), find(v)
        if a == b: acyclic = False
        parent[a] = b
    connected = bool(selected) and len({find(v) for v in selected}) == 1
    tree = connected and acyclic and len(edges) == len(selected)-1
    energy = sum(profits.get(v, 0) for v in selected)
    quota = ampl.get_value('Q')
    cost = float(edges.iloc[:, 0].sum() + nodes.iloc[:, 0].sum())
    objective = float(ampl.get_objective('Investment').value())
    integrality = max(float(ampl.get_value('max {(u,v) in E} abs(x[u,v]-round(x[u,v]))')),
                      float(ampl.get_value('max {v in V} abs(z[v]-round(z[v]))')))
    valid = (tree and fixed <= selected and energy + 1e-6 >= quota and
             abs(cost-objective) <= 1e-5*max(1, abs(objective)) and integrality <= 1e-5)
    bound = float(ampl.get_value('Investment.bestbound'))
    bound = bound if math.isfinite(bound) else None
    gap = None if bound is None else (abs(objective-bound)/abs(objective)
           if objective else (0.0 if abs(bound) < 1e-8 else None))
    report = {'status': ampl.get_value('solve_result'), 'objective_million_EUR': objective,
              'best_bound': bound,
              'relative_gap': gap,
              'energy_GWh': energy, 'quota_GWh': quota, 'selected_vertices': len(selected),
              'selected_edges': len(edges), 'selected_turbines': len(selected & profits.keys()),
              'is_tree': tree, 'all_fixed_selected': fixed <= selected,
              'independently_validated': bool(valid)}
    if not valid: raise ValueError(f'No valid integer solution to export: {report}')
    edges.index.names = ['u', 'v']
    edges.columns = ['cost_million_EUR']
    nodes.index.name = 'node_id'
    nodes.columns = ['cost_million_EUR']
    edges.to_csv(output_dir / f'{tag}_edges.csv')
    nodes.to_csv(output_dir / f'{tag}_nodes.csv')
    (output_dir / f'{tag}_summary.json').write_text(json.dumps(report, indent=2))
    return report

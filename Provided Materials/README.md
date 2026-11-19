# OR7310 — Provided materials

Read this README first, then open `start_here.ipynb`. This package supplies the cost-only baseline model from the project handout, implemented in AMPL. Your project work is to improve the baseline and study landscape impact as described in the handout.

## What is included

- `quota_steiner.mod`: the handout's integer programming model.
- `start_here.ipynb`: setup, model loading, solving, solution validation, result export, and instructions for loading the supplied Part B data.
- `requirements.txt`: Python dependencies, also installed by the notebook setup cell.
- `project_helpers.py`: solution validation and result export for the cost-only baseline.
- `tiny.dat`, `tiny.run`: a four-node example, runnable from Python or the AMPL console.
- `datasets/regionA/` and `datasets/regionB/`: two AMPL data files per region: `<region>.dat` for baseline inputs and `<region>_landscape.dat` for Part B.

All inputs are ready to load into AMPL. The notebook creates only `results/` for saved solutions; no data preprocessing is needed.

## First-time setup

1. Install Python and the Python and Jupyter extensions in VS Code. Open this folder, then the notebook.
2. Select a Python kernel using **Select Kernel**. A virtual environment is optional but recommended; create/select it through VS Code before installing packages. Jupyter does not automatically give everyone the same Python environment.
3. Run `%pip install amplpy pandas` in the notebook. This installs into the selected kernel. Restart the kernel if an import still fails.
4. Use your licensed course installation of AMPL and its Gurobi solver. Change `AMPL_FOLDER` in the notebook to its installation folder; set it to `None` if AMPL is already on PATH. `/Applications/AMPL` is a Mac example, not a universal path.
5. Run all cells with `CASE = "tiny"`. Expected objective: 8. Then select `regionA`, rerun the configuration and following cells, and finally attempt `regionB`.

Python calls AMPL through `amplpy`, and AMPL calls the Gurobi solver. Do not share license files in your submission. If the academic license lease needs renewal, connect to the internet and open AMPL; contact the instructor if it remains unavailable.

To use AMPL without Python, start AMPL in this folder and enter `include tiny.run;`.

## Instances and units

| Instance | Vertices | Undirected edges | Candidate turbines | Fixed substations | Annual quota |
|---|---:|---:|---:|---:|---:|
| Region A | 147 | 10,731 | 22 | 3 | 70 GWh |
| Region B | 1,639 | 1,342,341 | 65 | 8 | 300 GWh |

Load `datasets/regionA/regionA.dat` or `datasets/regionB/regionB.dat` for Part A. These files contain:

| AMPL input | Meaning |
|---|---|
| `V`, `E` | Vertices and available undirected edges |
| `F`, `P` | Fixed substations and candidate turbines |
| `r` | Root substation for artificial flow |
| `c[u,v]` | Cable cost in million EUR |
| `w[v]` | Vertex installation cost in million EUR; zero for junctions/substations |
| `q[v]` | Candidate turbine annual generation in GWh |
| `Q` | Required annual generation in GWh |

Costs, energy values, edges, and fixed terminals are preserved from the source instances. No calculations from turbine capacity or full-load hours are needed.

The fixed substations have artificial zero-cost connections representing the existing grid. They are included in the network selected by the optimization model. 

## Part B: Supplied landscape data

Use `datasets/regionA/regionA_landscape.dat` or `datasets/regionB/regionB_landscape.dat`. These AMPL data files already contain:

- `h[u,v]`: cable landscape impact (length in km multiplied by route scenicness), with zero for artificial existing-grid links.
- `s_turbine[v]`: turbine scenicness, corresponding to s_v in the handout.

In your Part B model, declare `param h {E} >= 0;` and `param s_turbine {P} >= 0;`, then load the supplied landscape file after the original instance data. The notebook shows the file path and loading instructions.

Your task is to implement the weighted objective and compare the requested alpha values. The supplied `.mod` is still the cost-only baseline.

The solution checker is for the cost-only model. Adapt its objective-consistency check and bound/gap reporting for your Part B objective while retaining the feasibility checks if you wish to use it for PART B.

## Model and results

There is one binary `x` per undirected edge and one binary `z` per vertex. Every selected nonroot vertex, including a junction, consumes one unit. Connectivity plus `sum(x) = sum(z)-1` forces a tree. Both flow directions share the bound `(card(V)-1)*x`.

The notebook reports the incumbent objective, lower bound, relative gap, energy, and selected nodes/edges. The gap is `abs(incumbent-bound)/abs(incumbent)` for nonzero objectives. The solution checker verifies integrality, fixed terminals, quota, tree structure, and objective consistency before saving a solution. It checks feasibility and cost consistency, not optimality. The gap is a fraction (for example, 0.10 means 10%); a missing finite lower bound is reported as `null` in the JSON output.

Default time and thread settings are `None`, and there is no memory cap. Set `TIME_LIMIT` to a number of seconds for a bounded experiment; use consistent limits when comparing methods. Region B can exhaust laptop memory. Start with Region A, close previous AMPL objects, and avoid loading all edge variables into pandas. The notebook exports only selected edges.

The notebook records model/data-loading time and solve-call time separately. The solve call also includes AMPL model generation; use the solver log for optimization time when comparing methods.

Call `ampl.close()` when finished to release its process and memory. After closing it, rerun the model-loading cell before further queries or solves.

## Sources

These source data accompany the wind-farm quota-Steiner-tree study by Pedersen, Rehfeldt, Weinand, and Syranidou:

- Paper: https://arxiv.org/abs/2304.09658
- Dataset and original metadata/license: https://doi.org/10.5281/zenodo.10600575

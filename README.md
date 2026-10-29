# Coupled Lithium-Ion Battery Degradation in PyBaMM

Simulates how several degradation mechanisms interact in a lithium-ion cell during cycling, using the Doyle-Fuller-Newman (DFN) model in [PyBaMM](https://pybamm.org) with the OKane2022 parameter set.

## Mechanisms included

| Mechanism | PyBaMM option |
| --- | --- |
| SEI growth (solvent-diffusion limited), with porosity change | `SEI`, `SEI porosity change` |
| Partially reversible lithium plating, with porosity change | `lithium plating`, `lithium plating porosity change` |
| Particle swelling and cracking (negative), swelling (positive) | `particle mechanics` |
| SEI growth on new crack surfaces | `SEI on cracks` |
| Stress-driven loss of active material | `loss of active material` |

## Experiment

1. Initial capacity check (C/10 discharge, C/3 charge, CV hold)
2. 20 aging cycles: 1C discharge to 2.5 V, C/3 charge to 4.2 V, CV hold to C/100
3. Final C/10 capacity check

## Outputs

- Capacity lost to SEI, SEI on cracks, and lithium plating vs. throughput capacity
- Degradation modes: loss of lithium inventory (LLI) and loss of active material (LAM) in each electrode
- Electrode porosity, particle crack length, and particle surface stress over time

## Run it

```bash
pip install pybamm matplotlib numpy
python Coupled_degradation.py
```

Change `NUMBER_OF_AGING_CYCLES` at the top of the script to simulate longer aging.

## Author

Farzaneh Barat, Ph.D. student, University of Kansas · [Website](https://farzanehbarat.github.io) · [Google Scholar](https://scholar.google.com/citations?user=KrAn6_gAAAAJ)

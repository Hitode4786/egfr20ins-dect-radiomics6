# Figure 7 Simulation Replay Receipt

## Scope

This receipt covers only the controlled synthetic simulation reported as
Figure 7. It contains no patient-level data, clinical labels, images, or
patient-derived predictions. It is separate from the restricted-data clinical
analysis workflow.

## Frozen execution

- Entrypoint: `simulation/run_ltop_simulation.py`
- Command: `python simulation/run_ltop_simulation.py --repetitions 1000 --seed 20261019`
- Random-number generator: NumPy `default_rng`, master seed `20261019`
- Repetitions: 1,000 per scenario, learner, and development-positive-count cell
- Development dataset: 187 cases with 4, 8, or 16 positives
- Test dataset: 61 cases with 4 positives and 57 negatives
- Threshold workflow: fit once on a 60% development fitting subset; select the
  largest recall-constrained threshold on the independent 40% development
  threshold-selection subset; apply the same fitted probability function and
  frozen threshold to the independent test set without refitting.
- Environment: Python 3.14.5 with versions pinned in
  `simulation/requirements-lock.txt` and recorded in
  `simulation/outputs/ltop_simulation_config.json`.

## Expected outputs

- `outputs/ltop_simulation_runs.csv`: one row per simulated development-test pair
- `outputs/ltop_simulation_summary.csv`: grouped summaries used for the figure
- `outputs/ltop_simulation_config.json`: run configuration and runtime versions
- `outputs/ltop_simulation.pdf`, `.svg`, and `.tiff`: Figure 7 exports
- `SIMULATION_MANIFEST_SHA256.csv`: file identity hashes for this simulation module

The receipt establishes a rerunnable synthetic simulation artifact. It does not
constitute external validation, clinical utility evidence, or a replay of the
restricted patient-data analysis.

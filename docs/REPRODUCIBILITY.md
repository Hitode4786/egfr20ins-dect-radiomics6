# Reproducibility passport

## Computational targets

| Target | Code/configuration | Inputs | Environment | Evidence state |
| --- | --- | --- | --- | --- |
| Figure 7 synthetic stress test | Present and SHA-256 listed | Public synthetic generation | `simulation/requirements-lock.txt` | REPLAYED |
| Clinical figures, tables, and metrics | Present; restricted replay route documented | Restricted authorised bundle | `environment.yml` and `requirements-clinical.lock.txt` | RERUNNABLE |

`REPLAYED` applies only to the synthetic Figure 7 target. It does not establish external validation or clinical validity. The clinical workflow is `RERUNNABLE` because its required input data are lawfully restricted and no public clinical replay receipt is included.

## Figure 7 identity contract

- Command: `python simulation/run_ltop_simulation.py --repetitions 1000 --seed 20261019`
- Seed: `20261019`
- Reference outputs: `simulation/outputs/`
- Hash manifest: `simulation/SIMULATION_MANIFEST_SHA256.csv`
- Protocol and boundaries: `simulation/REPLAY_RECEIPT.md`

## Release integrity

`REPOSITORY_MANIFEST_SHA256.csv` lists every release file except the manifest itself and untracked local preview artifacts. Verify it before creating a tag. After a future modification, regenerate the manifest and assign a new software release version. Do not overwrite or relabel an archived release.

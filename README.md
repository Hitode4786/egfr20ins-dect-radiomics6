# Locked-threshold evaluation for EGFR exon 20 insertion DECT radiomics

This repository accompanies the manuscript *Locked-threshold evaluation exposes operability failure in EGFR exon 20 insertion DECT radiomics*. It contains analysis source code and a fully synthetic, independently runnable Figure 7 simulation. It does not contain clinical images, labels, feature matrices, patient-level predictions, fitted clinical models, or model checkpoints.

## What is publicly reproducible

| Component | Data status | Evidence level | Entry point |
| --- | --- | --- | --- |
| Figure 7 synthetic stress test | Public, fully synthetic | REPLAYED | `simulation/run_ltop_simulation.py` |
| Clinical radiomics analysis | Restricted, authorised access only | RERUNNABLE | `scripts/run_egfr20ins_*.py` |

The synthetic simulation demonstrates a controlled failure boundary. It is not external validation, evidence of clinical utility, or a replay of the restricted clinical analysis. See `simulation/REPLAY_RECEIPT.md` for its frozen protocol, environment, expected outputs, hashes, and interpretation boundary.

## Quick start: synthetic Figure 7

Use the separately pinned Figure 7 environment. From the repository root:

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r simulation/requirements-lock.txt
.venv/Scripts/python simulation/run_ltop_simulation.py --repetitions 1000 --seed 20261019
```

On macOS/Linux, replace `.venv/Scripts/python` with `.venv/bin/python`. The committed outputs, including the per-repetition CSV and summary CSV, are in `simulation/outputs/`. Re-running the command writes to that directory by default; use `--output-dir` to preserve the committed reference artifacts.

## Clinical-analysis source code

The clinical workflow requires an authorised, de-identified input bundle and must not be run on publicly available files because none are included. Create the recorded environment:

```bash
conda env create -f environment.yml
conda activate egfr20ins-paper
```

The core modules are `run_egfr20ins_repeated_cv.py` (repeated development cross-validation), `run_egfr20ins_fixed_test_bootstrap.py` (frozen temporal holdout evaluation), `run_egfr20ins_calibration_dca.py` (exploratory calibration/DCA), `run_egfr20ins_bootstrap_stability.py`, `run_egfr20ins_subgroup_analysis.py`, and the table, figure, and explainability scripts. The expected input contract is in [`docs/RESTRICTED_DATA_ACCESS.md`](docs/RESTRICTED_DATA_ACCESS.md); technical provenance is in [`docs/CONFIGURATION_AND_PROVENANCE.md`](docs/CONFIGURATION_AND_PROVENANCE.md).

## Layout

- `scripts/`: restricted-data clinical analysis and figure-generation source code.
- `simulation/`: fully synthetic Figure 7 code, outputs, and replay receipt.
- `docs/`: data-access and reproducibility documentation.
- `data/`: empty, git-protected location for authorised local inputs.

## Release and citation

The code is MIT licensed. Cite the associated article and the versioned software release described in `CITATION.cff`. Before formal public archiving, create a GitHub release and archive it with Zenodo (or an equivalent repository) to obtain a version-specific DOI; replace the URL placeholder in `CITATION.cff` and cite the immutable release, not a mutable branch.

## Security and privacy

Do not commit patient data, DICOM/NIfTI files, patient-level predictions, credentials, model weights, or unreviewed outputs. `.gitignore` blocks common sensitive artifacts but does not replace a manual release review.

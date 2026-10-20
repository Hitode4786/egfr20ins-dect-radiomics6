# LT-OP Simulation Experiment

This package implements a simulation experiment for the locked-threshold
operability assessment (LT-OP) workflow. It is an analytic extension of the
single-centre DECT case study, not patient data and not external validation.

## Question

Across controlled feature distributions and development event counts, how often
can a development-selected, recall-constrained threshold yield poor specificity
in an independent test set, even when threshold-independent discrimination is
reported?

The experiment does **not** assume that every standard classifier fails. Its
purpose is to estimate the conditions under which low event counts and score
overlap make frozen-threshold specificity unstable.

## Fixed protocol

- Development set: 187 cases, with 4, 8, or 16 positive cases.
- Test set: 61 cases, with 4 positive and 57 negative cases.
- Data-generating mechanisms: moderately separated Gaussian features,
  strongly overlapping Gaussian features, and weakly informative Bernoulli
  features.
- Learners: L2-regularized logistic regression and a depth-2 decision tree.
- Development split: each 187-case development dataset is stratified into a
  60% model-fitting subset and a 40% independent threshold-selection subset.
- Threshold: the model is fitted once on the fitting subset. The largest score
  cutoff satisfying recall >= 0.75 is selected on the independent
  threshold-selection subset, then frozen and evaluated using the same fitted
  probability function on the independent test set. The model is not refitted
  after threshold selection.
- Repetitions: 1,000 per scenario, learner, and development event-count
  condition by default.

## Interpretation boundary

The script uses native model probability outputs and deliberately does not add
a calibration layer. It therefore isolates development-sample, score-overlap,
and threshold-selection behavior. It does not assess calibration uncertainty,
clinical utility, or DECT transportability. Results must be reported as a
controlled simulation rather than as evidence of external validation.

## Run

```powershell
python run_ltop_simulation.py --repetitions 1000 --seed 20261019
```

The command writes per-repetition data, a grouped summary, the exact run
configuration, package versions, and a three-panel publication figure under
`outputs/`.

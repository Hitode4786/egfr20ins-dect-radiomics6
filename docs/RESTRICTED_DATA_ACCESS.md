# Restricted clinical-data access

## Availability

The human-participant DECT images, masks, molecular labels, clinical variables, radiomic feature matrices, trained clinical models, and patient-level predictions are not publicly distributed. Their release is restricted by institutional governance and participant-data protections.

An authorised request must be reviewed through the responsible institution's data-use-agreement process. This repository does not provide an access contact, approval guarantee, or a substitute dataset. The corresponding author and data steward must supply those details in the published Data Availability statement.

## Input contract for an authorised replay

The clinical scripts expect, at minimum:

1. A de-identified label table with a non-identifying study key, outcome label, and fixed temporal split membership.
2. A radiomics matrix aligned to that study key, with documented feature ordering and DECT-series definitions.
3. Optional clinical covariates (age, sex, smoking history, and tumour location) when using the combined candidate pool.
4. For image-to-feature replay only, de-identified input images, consensus masks, and the preprocessing/radiomics configuration in `CONFIGURATION_AND_PROVENANCE.md`.

The public source uses local paths under `data/` by default or `LUAD_EGFR20INS_*` environment variables documented in `scripts/run_egfr20ins_binary_strategies.py`. Do not publish study keys, dates, accession identifiers, small-cell counts, signed URLs, or unauthorised checksums.

## Boundary

A synthetic fixture can test installation and mechanics only. It cannot reproduce the clinical model results, validate the cohort, or establish external transportability.

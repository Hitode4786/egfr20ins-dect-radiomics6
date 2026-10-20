# Configuration and provenance

## Clinical case study

The restricted clinical study used venous-phase dual-energy CT series denoted `V80KV`, `V140KV`, and `VIC`; `V` denotes venous phase. All scans used 1.25-mm slice thickness. The cohort contained 248 patients, with 77 cases acquired in 2021 and 171 in 2023-2026. This repository distributes no imaging, labels, features, identifiers, or clinical output artifacts.

## Image and radiomics configuration

- PyRadiomics: 3.0.1
- Bin width: 25
- Resampled pixel spacing: none
- Interpolator when resampling is requested: `sitkBSpline`
- Intensity normalization: disabled
- Label: 1
- Radiomics candidates: 107 per DECT series across seven series (749 total)

Manual tumour segmentation was prepared under the local study workflow, with consensus review where readers differed. The image-processing portal used for the original study is proprietary; this code release therefore documents, but does not reproduce, all upstream image-processing steps.

## Primary model and evaluation

The primary XGBoost branch used `binary:logistic`, `logloss`, 300 estimators, maximum depth 3, learning rate 0.03, subsample 1.0, column subsampling 0.8, minimum child weight 1.0, `reg_alpha=0`, `reg_lambda=1`, `gamma=0`, and eight jobs. The repeated five-fold development analysis used seeds 42, 52, 62, 72, and 82.

The combined-candidate recursive-feature-elimination branch considered 749 radiomic features plus age, sex, smoking history, and tumour location. It retained 48 radiomic features and no clinical variable. Feature selection, calibration, and threshold locking were confined to development data; the temporal holdout was evaluated after these operations were frozen.

## Portability boundary

The clinical workflow was frozen with Python 3.10.14, PyRadiomics 3.0.1, scikit-learn 1.7.2, and XGBoost 3.2.0. The feature-selection path is sensitive to the Python/scikit-learn version combination. The documented environment should therefore be used for authorised replay. This provenance record does not imply external validation or clinical deployment readiness.

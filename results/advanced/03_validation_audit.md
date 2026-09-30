# Priority 3: calibration, holdout and independent-benchmark audit

The original radiation closure remains physically unresolved. This audit asks whether a single empirical area multiplier transfers to held-out temperatures within Qi’s experiment. The split is fixed in the script before fitting; no held-out values enter the objective.

Training: [100, 120, 140] K. Held out: [90, 95, 110, 130, 153] K. Fitted multiplier: 0.4822, bounded to 0.2–1.2. Both reference radiation areas are multiplied together. All other parameters are frozen; measured flow remains prescribed.

| Chip K | Split | Measurement mW | Baseline mW | Corrected mW | Corrected error mW |
|---:|---|---:|---:|---:|---:|
| 90 | holdout | 18.2 | 14.0 | 20.0 | +1.8 |
| 95 | holdout | 48.6 | 40.1 | 64.8 | +16.2 |
| 100 | train | 63.0 | 41.8 | 66.3 | +3.3 |
| 110 | holdout | 69.8 | 48.4 | 72.6 | +2.8 |
| 120 | train | 97.0 | 72.6 | 96.4 | -0.6 |
| 130 | holdout | 121.9 | 96.8 | 120.2 | -1.7 |
| 140 | train | 142.7 | 116.9 | 139.8 | -2.9 |
| 153 | holdout | 146.9 | 121.1 | 143.2 | -3.7 |

Training RMSE: 2.60 mW. Holdout RMSE: 7.62 mW.

The fitted area multiplier absorbs multiple possible errors: wall temperature distribution, insulation exposure, emissivity and other omitted losses. Its value is not evidence that a physical surface has this fraction of the original area. No confidence interval or parameter identifiability is claimed. The low-temperature wet-return region is especially demanding; a fit at higher temperatures does not establish applicability there.

## Full-text evidence update, 2026-09-30

Both Pei main PDFs have now been read. See [the full-text external evidence report](06_external_evidence.md)
and [source ledger](../../docs/benchmark_candidates.md). Pei 2024 uses PID control,
so its laser test cannot validate the passive step model. Pei 2026 supports an
unfitted gas-runtime comparison, but its gas and detector experiments use separate
chips. Supplement S3 has now been reproduced in [the supplement audit](07_supplement_audit.md).
Independent exhaust and compatible package data remain necessary for thermal validation. The unchanged calibration results above are same-experiment
holdouts, not independent thermal validation.

# Repository Cleanup Report — Antibiotic Resistance Predictor

This cleanup report details the audit of the Antibiotic Resistance Predictor workspace. It classifies active, obsolete, duplicate, and runtime files, and proposes a clean repository structure to ensure maintainability as a professional clinical decision support software product.

---

## 1. Directory Audit & Classifications

### Root Directory Analysis
| Folder | Status | Action / Recommendation |
|---|---|---|
| `Backend/` | **Active** | Production FastAPI backend. Keep intact. |
| `Frontend/` | **Active** | Production React user interface. Keep intact. |
| `data/` | **Active** | Holds datasets. Keep clean dataset structure. |
| `logs/` | **Runtime** | Obsolete to track in git. Add to `.gitignore` and delete from git tracking. |
| `Model/` | **Obsolete** | *Already deleted* in the previous structural cleanup. |
| `models/` | **Active** | Production and experimental serialized model files. Keep intact. |
| `notebooks/` | **Active** | Reorganized notebooks and archives. Keep intact. |
| `results/` | **Active** | Consolidated metric CSV reports. Keep intact. |
| `screenshots/` | **Active** | Documentation assets for the user interface. Keep intact. |

---

## 2. Notebook Consolidation

All notebooks have been audited and organized under `notebooks/` and `notebooks/archive/`:

### Keep (Production Notebooks)
* **`notebooks/01_Data_Preparation.ipynb`**: Essential clinical data preparation and feature generation documentation.
* **`notebooks/04_Train_All_Antibiotics.ipynb`**: Active 15-target training pipeline, utilizing recall-constrained threshold optimization.
* **`notebooks/05_SHAP_Analysis.ipynb`**: Active Explainable AI (XAI) notebook featuring global summary plots and local patient waterfall explanations.

### Archive (Obsolete / Experimental)
These notebooks have been consolidated under [notebooks/archive/](file:///c:/Users/yashc/Desktop/Github/Antibiotic-Resistance-Predictor/notebooks/archive/) to prevent workspace clutter:
* `notebooks/archive/old_antibiotic_resistance_ml.ipynb` (Superseded old training)
* `notebooks/archive/Model_training.ipynb` (Draft GEN single-target experiment)
* `notebooks/archive/03_Model_Training_GEN.ipynb` (GEN pipeline verification)
* `notebooks/archive/Backend_antibiotic_resistance_ml.py` (Draft training script, kept for historical baseline reference)

---

## 3. Model Directory Cleanup (`models/`)

Serlialized XGBoost classifiers are segregated to align with deployment-readiness:

### Keep
* **`models/production/`**:
  * Contains the 6 high-performing beta-lactam models: `AMC.joblib`, `AMX_AMP.joblib`, `CTX_CRO.joblib`, `CZ.joblib`, `FOX.joblib`, and `IPM.joblib`.
  * Contains the production decision thresholds in `thresholds.json`.
* **`models/experimental/`**:
  * Contains the 9 lower-accuracy models: `Acide_nalidixique.joblib`, `AN.joblib`, `C.joblib`, `CIP.joblib`, `Co-trimoxazole.joblib`, `colistine.joblib`, `Furanes.joblib`, `GEN.joblib`, and `ofx.joblib`.
  * Contains experimental decision thresholds in `thresholds.json`.

---

## 4. Temporary and Runtime Files

Runtime outputs should be ignored to avoid committing personal settings and temporary cache files:

### Recommendations
1. Delete the Jupyter checkpoint: `notebooks/.ipynb_checkpoints/05_SHAP_Analysis-checkpoint.ipynb`.
2. Delete standard runtime log files: `logs/app.log`, `Backend/app.log`.
3. Add the following ignore patterns to `.gitignore`:
   ```text
   # Python Cache
   __pycache__/
   *.pyc
   
   # Jupyter Checkpoints
   .ipynb_checkpoints/
   
   # Logs and Runtimes
   *.log
   logs/
   Backend/logs/
   
   # OS Artifacts
   .DS_Store
   ```

---

## 5. Logs Directory Review

* **Actively Used**: Yes, standard logging outputs are directed to `logs/app.log`.
* **Recommendation**: **Remove from git tracking** but keep as a local folder. Add `/logs/` directly to `.gitignore` so that developer logs are never committed.

---

## 6. Data Directory Review

* **`data/cleaned_output_v2.csv`**: **Active**. Active production dataset with all baseline clinical records.
* **`data/archive/cleaned_output.csv`**: **Archived**. The historical dataset, preserved for backup.
* **Duplicates**: Audited. Redundant duplicate files in `Backend/` and `Model/` have already been completely removed.

---

## 7. Results Directory Review

* **`results/training_results.csv`**: **Active**. Canonical report outlining the training metrics, thresholds, and AUC scores of all 15 models.
* **`results/archive/`**: **Archived**. Obsolete metrics files from old pipeline runs, preserved for backup:
  * `results/archive/overall_metrics.csv`
  * `results/archive/per_label_metrics.csv`
  * `results/archive/tuned_thresholds.csv`

---

## 8. README Alignment Analysis

The current `README.md` is outdated and reflects the experimental baseline architecture. It needs to be updated with the following:

### Necessary Updates
1. **System Architecture**: Update text to describe the **15 independent per-antibiotic XGBoost pipelines** and their tier splits (Production vs Experimental) rather than referring to a single multi-output model (`model_small.joblib`).
2. **Clinical Feature Engineering**: Update feature description to list all 14 features (including the 7 engineered clinical risk factors).
3. **Notebook Reference**: Realign references to active notebooks (`notebooks/01_Data_Preparation.ipynb`, `notebooks/04_Train_All_Antibiotics.ipynb`, `notebooks/05_SHAP_Analysis.ipynb`).
4. **API Integration & Explainability**: Document the new FastAPI JSON response payload which features `confidence_tier`, `model_tier`, `probability`, and `explanation` (SHAP-computed clinical impact factors).

---

## 9. Final Recommended Repository Structure

This represents the canonical structure of the repository post-cleanup:

```text
ANTIBIOTIC-RESISTANCE-PREDICTOR/
│
├── Backend/                            ← FastAPI prediction service
│   ├── config.py
│   ├── main.py
│   ├── model_loader.py
│   ├── schemas.py
│   ├── utils.py
│   ├── test.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── Frontend/                           ← React patient portal & UI
│   ├── src/
│   ├── package.json
│   └── index.html
│
├── data/
│   ├── cleaned_output_v2.csv          ← Canonical production dataset
│   └── archive/
│       └── cleaned_output.csv         ← Historical backup dataset
│
├── models/
│   ├── production/                    ← Confirmed clinical-grade models
│   │   ├── AMC.joblib
│   │   ├── AMX_AMP.joblib
│   │   ├── CTX_CRO.joblib
│   │   ├── CZ.joblib
│   │   ├── FOX.joblib
│   │   ├── IPM.joblib
│   │   └── thresholds.json
│   │
│   └── experimental/                  ← Models needing further features/data
│       ├── Acide_nalidixique.joblib
│       ├── AN.joblib
│       ├── C.joblib
│       ├── CIP.joblib
│       ├── Co-trimoxazole.joblib
│       ├── colistine.joblib
│       ├── Furanes.joblib
│       ├── GEN.joblib
│       ├── ofx.joblib
│       └── thresholds.json
│
├── notebooks/
│   ├── 01_Data_Preparation.ipynb                     ← Features engineering doc
│   ├── 04_Train_All_Antibiotics.ipynb                ← Training loop pipeline
│   ├── 05_SHAP_Analysis.ipynb                        ← Interpretability notebook
│   └── archive/                                      ← Obsolete experimental baselines
│       ├── 03_Model_Training_GEN.ipynb
│       ├── Model_training.ipynb
│       ├── old_antibiotic_resistance_ml.ipynb
│       └── Backend_antibiotic_resistance_ml.py
│
├── results/
│   ├── training_results.csv           ← Full 15-target training metrics
│   └── archive/                       ← Old baselines metrics
│       ├── overall_metrics.csv
│       ├── per_label_metrics.csv
│       └── tuned_thresholds.csv
│
├── screenshots/
│   ├── ui-form.png
│   └── ui-result.png
│
├── README.md                           ← Main documentation (to be aligned)
├── PROJECT_CONTEXT.md                  ← System Context documentation
├── .gitignore                          ← Updated git ignores
└── docker-compose.yml                  ← Deployment file
```

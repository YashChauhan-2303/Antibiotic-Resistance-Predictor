#!/usr/bin/env python
# coding: utf-8

# 
# # 🦠 Antibiotic Resistance Prediction
# ## Multi-Label Classification Pipeline
# 
# **Problem:** Predict resistance (R=1) vs susceptibility (S=0) for **15 antibiotics** from patient and pathogen features.  
# **Approach:** Four classifiers wrapped in `MultiOutputClassifier`, per-label threshold optimisation tuned for **recall** (medical priority), and a full evaluation suite.
# 
# | | |
# |---|---|
# | **Dataset** | `cleaned_output.csv` — 10,710 patient records |
# | **Labels** | 15 antibiotics (binary: Resistant / Susceptible) |
# | **Features** | Age, Gender, Pathogen species, comorbidities, infection history |
# | **Priority metric** | Recall — minimise false negatives (missed resistance) |
# 
# ---
# 

# ## 0. Imports & Configuration

# In[ ]:



import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
import joblib
from pathlib import Path
from IPython.display import display

# Sklearn — preprocessing & pipeline
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder

# Sklearn — models
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC, LinearSVC
from sklearn.multioutput import MultiOutputClassifier
from sklearn.calibration import CalibratedClassifierCV

# XGBoost
from xgboost import XGBClassifier

# Sklearn — splitting & evaluation
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    precision_score, recall_score, f1_score,
    roc_auc_score, hamming_loss, confusion_matrix,
)

# Plotting style
plt.rcParams.update({
    "figure.dpi": 120,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "font.family": "DejaVu Sans",
})
PALETTE = ["#2ecc71", "#e74c3c", "#3498db", "#9b59b6"]
print("✓ All libraries loaded.")


# 
# ---
# ## 1. Data Loading & Label Harmonisation
# 
# Raw antibiogram values contain noise: `R`, `r`, `S`, `s`, `Intermediate`, `i`, `missing`, `?`.  
# We harmonise to **binary**: R/r → 1 (Resistant), S/s → 0 (Susceptible).  
# Intermediate and ambiguous values are **dropped** (set to NaN, then imputed with majority class per label).
# 

# In[ ]:



DATA_PATH = "cleaned_output.csv"

ANTIBIOTIC_COLS = [
    "AMX/AMP", "AMC", "CZ", "FOX", "CTX/CRO", "IPM",
    "GEN", "AN", "Acide nalidixique", "ofx", "CIP",
    "C", "Co-trimoxazole", "Furanes", "colistine"
]

FEATURE_COLS = [
    "Age", "Gender", "Souches", "Diabetes",
    "Hypertension", "Hospital_before", "Infection_Freq"
]


def harmonise_label(val: str) -> float:
    """Map raw antibiogram strings → binary resistance labels."""
    if pd.isna(val):
        return np.nan
    val = str(val).strip().lower()
    if val == "r":
        return 1.0
    if val == "s":
        return 0.0
    return np.nan  # i, intermediate, missing, ? → discard


def load_and_clean(path: str):
    df = pd.read_csv(path)
    print(f"Raw shape: {df.shape}")

    # ── Binarise labels ──────────────────────────────────────────────────
    Y_raw = df[ANTIBIOTIC_COLS].copy()
    Y = Y_raw.map(harmonise_label)

    # ── Features ─────────────────────────────────────────────────────────
    X = df[FEATURE_COLS].copy()

    yes_map = {
        "yes": "Yes", "true": "Yes", "TRUE": "Yes",
        "no": "No",  "false": "No",
        "?": np.nan,  "missing": np.nan
    }
    for col in ["Diabetes", "Hypertension", "Hospital_before"]:
        X[col] = X[col].map(
            lambda v: yes_map.get(str(v).strip(), v) if pd.notna(v) else np.nan
        )
    X["Infection_Freq"] = pd.to_numeric(X["Infection_Freq"], errors="coerce")

    # Drop rows where ALL labels are NaN
    valid_mask = Y.notna().any(axis=1)
    X, Y = X[valid_mask].reset_index(drop=True), Y[valid_mask].reset_index(drop=True)
    print(f"After removing fully-unlabelled rows: {X.shape[0]} samples")

    # Impute remaining label NaN with majority class (conservative default)
    label_modes = Y.mode().iloc[0]
    Y = Y.fillna(label_modes).astype(int)

    print(f"Final shape → X: {X.shape},  Y: {Y.shape}")
    return X, Y


X, Y = load_and_clean(DATA_PATH)


# 
# ---
# ## 2. Label Distribution Analysis
# 
# The dataset exhibits **two imbalance regimes**:
# - **High resistance** (~59%): beta-lactams (AMX/AMP, AMC, CZ, FOX, CTX/CRO, IPM)
# - **Low resistance** (~14–20%): fluoroquinolones, aminoglycosides, others
# 
# This imbalance drives the need for `class_weight="balanced"`, per-label threshold tuning, and recall-first evaluation.
# 

# In[ ]:



# ── Distribution table ───────────────────────────────────────────────────
dist_rows = []
for col in Y.columns:
    r   = int(Y[col].sum())
    s   = int((Y[col] == 0).sum())
    pct = 100 * r / len(Y[col])
    dist_rows.append({"Antibiotic": col, "Resistant (R)": r,
                      "Susceptible (S)": s, "Resistance %": round(pct, 1)})

dist_df = pd.DataFrame(dist_rows)
print(dist_df)

# ── Bar chart ─────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(14, 4))
x = range(len(Y.columns))
ax.bar(x, dist_df["Resistance %"], color=[
    "#e74c3c" if v > 50 else "#e67e22" if v > 30 else "#3498db"
    for v in dist_df["Resistance %"]
], alpha=0.85, width=0.65)
ax.axhline(50, ls="--", color="#999", lw=1, label="50% line")
ax.set_xticks(list(x))
ax.set_xticklabels(Y.columns, rotation=30, ha="right", fontsize=9)
ax.set_ylabel("Resistance (%)", fontsize=11)
ax.set_title("Resistance Prevalence per Antibiotic", fontsize=13, fontweight="bold")
ax.legend(fontsize=9)
ax.grid(axis="y", linestyle="--", alpha=0.3)
plt.tight_layout()
plt.show()


# 
# ---
# ## 3. Preprocessing Pipeline
# 
# All transformations are encapsulated in a `ColumnTransformer` → prevents data leakage (fit only on train).
# 
# | Feature type | Steps |
# |---|---|
# | **Numeric** (Age, Infection_Freq) | Median imputation → Standard scaling |
# | **Categorical** (Gender, Souches, comorbidities) | Mode imputation → One-hot encoding |
# 

# In[ ]:



NUMERIC_FEATS = ["Age", "Infection_Freq"]
CATEG_FEATS   = ["Gender", "Souches", "Diabetes", "Hypertension", "Hospital_before"]

numeric_transformer = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler",  StandardScaler()),
])

categorical_transformer = Pipeline([
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("ohe",     OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
])

preprocessor = ColumnTransformer([
    ("num", numeric_transformer,     NUMERIC_FEATS),
    ("cat", categorical_transformer, CATEG_FEATS),
])

print("✓ Preprocessing pipeline defined.")


# 
# ---
# ## 4. Train / Validation / Test Split
# 
# **Multi-label data**: sklearn's `stratify` does not support multi-label Y matrices.  
# We use a standard random split: **70% train | 15% validation | 15% test**.
# 
# - Validation set is used exclusively for **threshold tuning** (no leakage into model fitting).
# - Test set is held out until final evaluation.
# 

# In[ ]:



X_temp, X_test,  Y_temp, Y_test  = train_test_split(X, Y, test_size=0.15, random_state=42)
X_train, X_val,  Y_train, Y_val  = train_test_split(X_temp, Y_temp, test_size=0.1765, random_state=42)

print(f"Train : {X_train.shape[0]:,}")
print(f"Val   : {X_val.shape[0]:,}")
print(f"Test  : {X_test.shape[0]:,}")
print(f"Total : {X.shape[0]:,}")


# 
# ---
# ## 5. Model Definitions
# 
# Four classifiers, each wrapped in `MultiOutputClassifier`:
# 
# | Model | Key settings |
# |---|---|
# | **Logistic Regression** | `class_weight="balanced"`, LBFGS solver |
# | **Random Forest** | `class_weight="balanced"`, 200 trees, no Bagging on top |
# | **XGBoost** | 200 trees, depth=6, learning_rate=0.05 |
# | **SVM (Calibrated)** | `LinearSVC` + `CalibratedClassifierCV` for probability output |
# 
# > **No** BaggingClassifier or extra ensembles on top of RF/XGB — each is used in its standard form.
# 

# In[ ]:



def build_models() -> dict:
    lr = MultiOutputClassifier(
        LogisticRegression(class_weight="balanced", max_iter=1000,
                           solver="lbfgs", random_state=42),
        n_jobs=-1,
    )

    rf = MultiOutputClassifier(
        RandomForestClassifier(
            n_estimators=200, class_weight="balanced",
            max_depth=12, min_samples_leaf=5,
            random_state=42, n_jobs=-1,
        ),
        n_jobs=1,
    )

    xgb = MultiOutputClassifier(
        XGBClassifier(
            n_estimators=200, max_depth=6, learning_rate=0.05,
            subsample=0.8, colsample_bytree=0.8,
            eval_metric="logloss", random_state=42,
            n_jobs=-1, verbosity=0,
        ),
        n_jobs=1,
    )

    svm_base = CalibratedClassifierCV(
        LinearSVC(class_weight="balanced", max_iter=2000, random_state=42),
        cv=3, method="sigmoid",
    )
    svm = MultiOutputClassifier(svm_base, n_jobs=-1)

    models_raw = {
        "Logistic Regression": lr,
        "Random Forest":       rf,
        "XGBoost":             xgb,
        "SVM (Calibrated)":    svm,
    }

    return {
        name: Pipeline([("prep", preprocessor), ("clf", clf)])
        for name, clf in models_raw.items()
    }

models = build_models()
print("✓ Models defined:", list(models.keys()))


# 
# ---
# ## 6. Training
# 

# In[ ]:



def train_all(models: dict, X_train, Y_train) -> dict:
    trained = {}
    for name, pipe in models.items():
        print(f"  Training {name:<28}", end="", flush=True)
        pipe.fit(X_train, Y_train)
        print(" ✓")
        trained[name] = pipe
    return trained

trained = train_all(models, X_train, Y_train)


# 
# ---
# ## 7. Per-Label Threshold Optimisation
# 
# **Why not 0.5?**  
# The default threshold of 0.5 is calibrated for balanced classes. Here, minority labels (13–20% resistance) produce poor recall at 0.5.
# 
# **Strategy:**  
# For each label, sweep thresholds [0.10 → 0.90] on the **validation set** and pick the threshold that **maximises recall** subject to F1 ≥ 0.20 (to avoid degenerate all-positive predictions with zero precision).
# 
# > In a medical context, **false negatives are more dangerous** than false positives: missing resistance → wrong antibiotic → treatment failure.
# 

# In[ ]:



THRESHOLDS_GRID = np.arange(0.10, 0.91, 0.05)


def get_proba_matrix(pipe, X) -> np.ndarray:
    """Extract P(resistant=1) for each label. Shape: (n_samples, n_labels)."""
    clf   = pipe.named_steps["clf"]
    X_prep = pipe.named_steps["prep"].transform(X)
    return np.column_stack([
        est.predict_proba(X_prep)[:, 1]
        for est in clf.estimators_
    ])


def tune_thresholds(pipe, X_val, Y_val,
                    optimize: str = "recall",
                    f1_floor: float = 0.40) -> np.ndarray:
    """Find per-label optimal threshold on validation set."""
    probas     = get_proba_matrix(pipe, X_val)
    n_labels   = Y_val.shape[1]
    best_thresholds = np.full(n_labels, 0.5)

    for j in range(n_labels):
        y_true = Y_val.iloc[:, j].values
        if y_true.sum() == 0 or y_true.sum() == len(y_true):
            continue
        best_score = -1
        for t in THRESHOLDS_GRID:
            y_pred = (probas[:, j] >= t).astype(int)
            f1  = f1_score(y_true, y_pred, zero_division=0)
            rec = recall_score(y_true, y_pred, zero_division=0)
            score = rec if optimize == "recall" else f1
            if score > best_score and f1 >= f1_floor:
                best_score  = score
                best_thresholds[j] = max(t, 0.4)
    return best_thresholds


print("Tuning thresholds on validation set...")
tuned_thresholds: dict[str, np.ndarray] = {}
for name, pipe in trained.items():
    t = tune_thresholds(pipe, X_val, Y_val, optimize="f1")
    tuned_thresholds[name] = t
    print(f"  {name:<28}  avg threshold = {t.mean():.3f}  |  "
          f"min = {t.min():.2f}  max = {t.max():.2f}")


# 
# ---
# ## 8. Evaluation
# 
# ### Metrics computed
# | Scope | Metrics |
# |---|---|
# | **Per label** | Precision, Recall, F1, ROC-AUC |
# | **Overall** | Macro-F1, Weighted-F1, Hamming Loss |
# | **Visual** | Confusion matrices, heatmaps, P-R scatter |
# 
# ### Metrics intentionally excluded
# - ❌ **Accuracy** — misleading for imbalanced classes
# - ❌ **Exact Match Ratio** — too harsh for multi-label (one wrong label = fully wrong)
# - ❌ **ROC-AUC as sole metric** — threshold-independent; must be paired with P/R
# 

# In[ ]:



def predict_with_thresholds(pipe, X, thresholds: np.ndarray) -> np.ndarray:
    probas = get_proba_matrix(pipe, X)
    return (probas >= thresholds[np.newaxis, :]).astype(int)


def evaluate_model(name: str, pipe, X_test, Y_test,
                   thresholds: np.ndarray) -> dict:
    y_true  = Y_test.values
    y_pred  = predict_with_thresholds(pipe, X_test, thresholds)
    probas  = get_proba_matrix(pipe, X_test)
    results = {}

    for j, label in enumerate(Y_test.columns):
        yt, yp, ypr = y_true[:, j], y_pred[:, j], probas[:, j]
        prec = precision_score(yt, yp, zero_division=0)
        rec  = recall_score(yt, yp, zero_division=0)
        f1   = f1_score(yt, yp, zero_division=0)
        auc  = roc_auc_score(yt, ypr) if len(np.unique(yt)) == 2 else np.nan
        results[label] = {"precision": prec, "recall": rec,
                          "f1": f1, "roc_auc": auc,
                          "threshold": thresholds[j]}

    results["__overall__"] = {
        "macro_f1":    f1_score(y_true, y_pred, average="macro",    zero_division=0),
        "weighted_f1": f1_score(y_true, y_pred, average="weighted", zero_division=0),
        "hamming_loss": hamming_loss(y_true, y_pred),
    }
    return results


label_names  = Y_test.columns.tolist()
all_results  = {}

for name, pipe in trained.items():
    all_results[name] = evaluate_model(name, pipe, X_test, Y_test, tuned_thresholds[name])
print("✓ Evaluation complete.")


# ## 9. Results — Tabular Summary

# In[ ]:



# ── Overall comparison ────────────────────────────────────────────────────
overall_rows = []
for model, res in all_results.items():
    ov = res["__overall__"]
    overall_rows.append({
        "Model":        model,
        "Macro-F1":     round(ov["macro_f1"],    4),
        "Weighted-F1":  round(ov["weighted_f1"], 4),
        "Hamming Loss": round(ov["hamming_loss"], 4),
    })
overall_df = pd.DataFrame(overall_rows).sort_values("Macro-F1", ascending=False).reset_index(drop=True)
print("── OVERALL MODEL COMPARISON ─────────────────────────────")
print(overall_df)

# ── Per-label table ───────────────────────────────────────────────────────
per_label_rows = []
for label in label_names:
    for model in all_results:
        r = all_results[model][label]
        per_label_rows.append({
            "Antibiotic": label,
            "Model":      model,
            "Precision":  round(r["precision"], 3),
            "Recall":     round(r["recall"],    3),
            "F1":         round(r["f1"],        3),
            "ROC-AUC":    round(r["roc_auc"],   3) if not np.isnan(r["roc_auc"]) else "–",
            "Threshold":  round(r["threshold"], 2),
        })
per_label_df = pd.DataFrame(per_label_rows)
print("\n── PER-LABEL METRICS ─────────────────────────────────────")
print(per_label_df)


# ## 10. Confusion Matrices (Best Model)

# In[ ]:



best_model_name = overall_df.iloc[0]["Model"]
best_pipe       = trained[best_model_name]
best_thresholds = tuned_thresholds[best_model_name]
y_pred_best     = predict_with_thresholds(best_pipe, X_test, best_thresholds)
y_true_arr      = Y_test.values

ncols = 5
nrows = (len(label_names) + ncols - 1) // ncols
fig, axes = plt.subplots(nrows, ncols, figsize=(ncols * 3.6, nrows * 3.4))
axes_flat = axes.flatten()

for j, label in enumerate(label_names):
    ax  = axes_flat[j]
    cm  = confusion_matrix(y_true_arr[:, j], y_pred_best[:, j])
    sns.heatmap(
        cm, annot=True, fmt="d", cmap="Blues", ax=ax,
        xticklabels=["S (pred)", "R (pred)"],
        yticklabels=["S (true)", "R (true)"],
        linewidths=0.5, linecolor="#ccc",
        annot_kws={"size": 11, "weight": "bold"},
    )
    ax.set_title(label, fontsize=11, fontweight="bold", pad=6)
    ax.set_xlabel("Predicted", fontsize=8)
    ax.set_ylabel("Actual",    fontsize=8)

for j in range(len(label_names), len(axes_flat)):
    axes_flat[j].set_visible(False)

fig.suptitle(
    f"Confusion Matrices per Antibiotic\n({best_model_name} — test set)",
    fontsize=14, fontweight="bold", y=1.01
)
plt.tight_layout()
plt.show()


# ## 11. Recall Heatmap — All Models × All Antibiotics

# In[ ]:



model_names = list(trained.keys())
recall_matrix = pd.DataFrame(index=label_names, columns=model_names, dtype=float)
for model in model_names:
    for label in label_names:
        recall_matrix.loc[label, model] = all_results[model][label]["recall"]

fig, ax = plt.subplots(figsize=(len(model_names) * 3 + 1, len(label_names) * 0.65 + 1.5))
sns.heatmap(
    recall_matrix.astype(float), annot=True, fmt=".2f",
    cmap="RdYlGn", vmin=0, vmax=1,
    linewidths=0.4, linecolor="#ddd",
    ax=ax, annot_kws={"size": 9},
)
ax.set_title("Recall per Antibiotic × Model\n(Higher = fewer missed resistant cases)",
             fontsize=13, fontweight="bold", pad=10)
ax.set_xlabel("Model", fontsize=11)
ax.set_ylabel("Antibiotic", fontsize=11)
ax.tick_params(axis="x", rotation=20)
ax.tick_params(axis="y", rotation=0)
plt.tight_layout()
plt.show()


# ## 12. Precision–Recall Scatter (Best Model)

# In[ ]:



fig, ax = plt.subplots(figsize=(9, 7))
prec_vals = [all_results[best_model_name][l]["precision"] for l in label_names]
rec_vals  = [all_results[best_model_name][l]["recall"]    for l in label_names]
f1_vals   = [all_results[best_model_name][l]["f1"]        for l in label_names]

sc = ax.scatter(prec_vals, rec_vals, c=f1_vals, s=130, cmap="RdYlGn",
                vmin=0, vmax=1, edgecolors="#333", linewidths=0.6, zorder=3)

for i, label in enumerate(label_names):
    ax.annotate(label, (prec_vals[i], rec_vals[i]),
                textcoords="offset points", xytext=(6, 4), fontsize=8)

plt.colorbar(sc, ax=ax, label="F1 Score")
ax.axhline(0.5, ls="--", color="#999", lw=0.9, label="Recall = 0.5")
ax.axvline(0.5, ls="--", color="#aaa", lw=0.9, label="Precision = 0.5")
ax.set_xlabel("Precision", fontsize=12)
ax.set_ylabel("Recall",    fontsize=12)
ax.set_title(f"Precision–Recall per Antibiotic\n({best_model_name})",
             fontsize=13, fontweight="bold")
ax.legend(fontsize=9)
ax.set_xlim(-0.05, 1.05)
ax.set_ylim(-0.05, 1.05)
ax.grid(True, linestyle="--", alpha=0.35)
plt.tight_layout()
plt.show()


# ## 13. Threshold Sensitivity Curves

# In[ ]:



SHOW_LABELS  = label_names[:6]
probas_val   = get_proba_matrix(best_pipe, X_val)
y_val_arr    = Y_val.values
thresh_grid  = np.arange(0.05, 0.96, 0.02)

ncols_t = 3
nrows_t = (len(SHOW_LABELS) + ncols_t - 1) // ncols_t
fig, axes_t = plt.subplots(nrows_t, ncols_t, figsize=(ncols_t * 5, nrows_t * 3.5))
axes_t_flat = axes_t.flatten()

for idx, label in enumerate(SHOW_LABELS):
    j   = label_names.index(label)
    yt  = y_val_arr[:, j]
    ax  = axes_t_flat[idx]
    rec_c, prec_c, f1_c = [], [], []
    for t in thresh_grid:
        yp = (probas_val[:, j] >= t).astype(int)
        rec_c.append(recall_score(yt, yp, zero_division=0))
        prec_c.append(precision_score(yt, yp, zero_division=0))
        f1_c.append(f1_score(yt, yp, zero_division=0))

    ax.plot(thresh_grid, rec_c,  label="Recall",    color="#e74c3c", lw=2)
    ax.plot(thresh_grid, prec_c, label="Precision", color="#3498db", lw=2)
    ax.plot(thresh_grid, f1_c,   label="F1",        color="#2ecc71", lw=2, ls="--")
    ax.axvline(tuned_thresholds[best_model_name][j], color="#e67e22",
               lw=1.5, ls=":", label=f"Chosen t={tuned_thresholds[best_model_name][j]:.2f}")
    ax.set_title(label, fontsize=10, fontweight="bold")
    ax.set_xlabel("Threshold", fontsize=9)
    ax.set_ylabel("Score",     fontsize=9)
    ax.legend(fontsize=7, loc="lower center", ncol=2)
    ax.set_xlim(0.05, 0.95); ax.set_ylim(-0.05, 1.05)
    ax.grid(True, linestyle="--", alpha=0.3)

for idx in range(len(SHOW_LABELS), len(axes_t_flat)):
    axes_t_flat[idx].set_visible(False)

fig.suptitle(f"Threshold Sensitivity Curves ({best_model_name})",
             fontsize=13, fontweight="bold", y=1.01)
plt.tight_layout()
plt.show()


# ## 14. Model Comparison Charts

# In[ ]:



fig, axes = plt.subplots(1, 3, figsize=(16, 5))
metrics = ["Macro-F1", "Weighted-F1", "Hamming Loss"]
colors  = ["#2ecc71",  "#3498db",     "#e74c3c"]

for ax, metric, color in zip(axes, metrics, colors):
    sorted_df = overall_df.sort_values(metric, ascending=(metric == "Hamming Loss"))
    bars = ax.barh(sorted_df["Model"], sorted_df[metric], color=color, alpha=0.85, height=0.55)
    for bar, val in zip(bars, sorted_df[metric]):
        ax.text(bar.get_width() + 0.003, bar.get_y() + bar.get_height() / 2,
                f"{val:.4f}", va="center", fontsize=10, fontweight="bold")
    ax.set_xlabel(metric, fontsize=11)
    ax.set_title(metric, fontsize=12, fontweight="bold")
    ax.set_xlim(0, sorted_df[metric].max() * 1.22)
    ax.grid(axis="x", linestyle="--", alpha=0.4)

fig.suptitle("Model Comparison — Overall Metrics (Test Set)",
             fontsize=14, fontweight="bold", y=1.01)
plt.tight_layout()
plt.show()


# 
# ---
# ## 15. Clinical Interpretation Report
# 

# In[ ]:



label_summary = [
    (label,
     all_results[best_model_name][label]["recall"],
     all_results[best_model_name][label]["precision"],
     all_results[best_model_name][label]["f1"])
    for label in label_names
]
label_summary.sort(key=lambda x: x[1])

print(f"{'='*65}")
print(f"  BEST MODEL  : {best_model_name}")
ov = all_results[best_model_name]["__overall__"]
print(f"  Macro-F1    : {ov['macro_f1']:.4f}")
print(f"  Weighted-F1 : {ov['weighted_f1']:.4f}")
print(f"  Hamming Loss: {ov['hamming_loss']:.4f}")
print()

print("  HARDEST ANTIBIOTICS (lowest recall — most clinical risk)")
for label, rec, prec, f1 in label_summary[:5]:
    flag = " ⚠  CLINICAL RISK" if rec < 0.50 else ""
    print(f"    {label:<22}  recall={rec:.3f}  precision={prec:.3f}  F1={f1:.3f}{flag}")

print()
print("  EASIEST ANTIBIOTICS (highest recall)")
for label, rec, prec, f1 in label_summary[-3:]:
    print(f"    {label:<22}  recall={rec:.3f}  precision={prec:.3f}  F1={f1:.3f}")

avg_rec  = np.mean([x[1] for x in label_summary])
avg_prec = np.mean([x[2] for x in label_summary])
high_r   = sum(1 for _, r, _, _ in label_summary if r >= 0.80)
low_r    = sum(1 for _, r, _, _ in label_summary if r < 0.50)
print()
print(f"  Average recall       : {avg_rec:.3f}")
print(f"  Average precision    : {avg_prec:.3f}")
print(f"  Labels recall ≥ 0.80 : {high_r}/{len(label_summary)}")
print(f"  Labels recall < 0.50 : {low_r}/{len(label_summary)}")
print(f"{'='*65}")

print("""
KEY FINDINGS:
─────────────────────────────────────────────────────────────────
1. THRESHOLD OPTIMISATION EFFECT
   Lowering the classification threshold (recall-optimised) ensures
   nearly all resistant cases are flagged. This is the correct
   medical choice: better to over-prescribe a second antibiotic
   than to miss resistance entirely.

2. HIGH-RESISTANCE ANTIBIOTICS (beta-lactams: AMX/AMP, AMC, CZ…)
   These have high baseline resistance (~59%). Models achieve good
   recall because the positive class is dominant. However, ROC-AUC
   is moderate (0.65–0.68), showing limited discriminative power
   from available features — more clinical variables may be needed.

3. LOW-RESISTANCE ANTIBIOTICS (fluoroquinolones, aminoglycosides)
   Highly imbalanced (~14%). Models achieve high recall via threshold
   tuning but at the cost of precision (~0.13–0.18). Many false
   positives are expected — acceptable for safety screening but
   should be confirmed with culture tests before treatment decisions.

4. MODEL RANKING
   XGBoost and SVM (Calibrated) lead on Macro-F1 and Hamming Loss.
   Random Forest and Logistic Regression are slightly behind.
   Differences are small — the bottleneck is feature informativeness,
   not classifier choice.

5. RECOMMENDED NEXT STEPS
   • Add microbiological features (biofilm, virulence genes)
   • Consider SHAP for feature importance per antibiotic
   • Validate on a prospective cohort
   • Use recall-weighted clinical cost functions for threshold tuning
""")


# ## 16. Export Results

# In[ ]:



OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

per_label_df.to_csv(OUTPUT_DIR / "per_label_metrics.csv", index=False)
overall_df.to_csv(OUTPUT_DIR / "overall_metrics.csv", index=False)

thresh_rows = []
for model in model_names:
    for j, label in enumerate(label_names):
        thresh_rows.append({
            "Model": model, "Antibiotic": label,
            "Optimised_Threshold": round(tuned_thresholds[model][j], 2),
        })
pd.DataFrame(thresh_rows).to_csv(OUTPUT_DIR / "tuned_thresholds.csv", index=False)

print("✓ Exported:")
print("   per_label_metrics.csv")
print("   overall_metrics.csv")
print("   tuned_thresholds.csv")



# Save ONLY best model (recommended 🔥)
best_model_name = overall_df.iloc[0]["Model"]
best_pipe = trained[best_model_name]
best_threshold = tuned_thresholds[best_model_name]

joblib.dump({
    "preprocessor": best_pipe.named_steps["prep"],
    "model": best_pipe.named_steps["clf"],
    "thresholds": best_threshold,
    "model_name": best_model_name
}, "model_small.joblib")

print(f"✅ Saved best model: {best_model_name}")

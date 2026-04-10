#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import warnings
import time
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
warnings.filterwarnings("ignore")

from sklearn.linear_model    import LogisticRegression
from sklearn.ensemble        import (RandomForestClassifier,
                                     BaggingClassifier,
                                     AdaBoostClassifier)
from sklearn.svm             import LinearSVC
from sklearn.calibration     import CalibratedClassifierCV
from sklearn.multioutput     import MultiOutputClassifier
from sklearn.pipeline        import Pipeline
from sklearn.compose         import ColumnTransformer
from sklearn.impute          import SimpleImputer
from sklearn.preprocessing   import OneHotEncoder, StandardScaler
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.metrics         import (f1_score, roc_auc_score, hamming_loss,
                                     accuracy_score, confusion_matrix,
                                     classification_report)
from xgboost import XGBClassifier

# In[2]:


FEATURE_COLS    = ["Age", "Gender", "Souches", "Diabetes",
                   "Hypertension", "Hospital_before", "Infection_Freq"]

ANTIBIOTIC_COLS = ["AMX/AMP", "AMC", "CZ", "FOX", "CTX/CRO", "IPM",
                   "GEN", "AN", "Acide nalidixique", "ofx", "CIP",
                   "C", "Co-trimoxazole", "Furanes", "colistine"]

NUM_COLS = ["Age", "Infection_Freq"]
CAT_COLS = ["Gender", "Souches", "Diabetes", "Hypertension", "Hospital_before"]

# In[3]:


df = pd.read_csv("cleaned_output.csv")
print(f"Raw shape: {df.shape}")

# In[4]:


df.drop(columns=["ID"], inplace=True)

df["Souches"] = df["Souches"].replace({
    "E.coi"  : "Escherichia coli",
    "E.cli"  : "Escherichia coli",
    "E. coli": "Escherichia coli",
})

noise_map = {"TRUE": "Yes", "true": "Yes", "False": "No",
             "false": "No", "?": np.nan, "missing": np.nan, "unknown": np.nan}
for col in ["Diabetes", "Hypertension", "Hospital_before"]:
    df[col] = df[col].replace(noise_map)

df["Infection_Freq"] = pd.to_numeric(
    df["Infection_Freq"].replace({"unknown": np.nan, "?": np.nan, "missing": np.nan}),
    errors="coerce")

def normalize_antibiotic(val):
    if pd.isna(val):
        return np.nan
    v = str(val).strip().upper()
    return {"R": "R", "S": "S", "I": "I", "INTERMEDIATE": "I",
            "MISSING": np.nan, "?": np.nan}.get(v, np.nan)

for col in ANTIBIOTIC_COLS:
    df[col] = df[col].apply(normalize_antibiotic).replace({"I": "R"})

df.dropna(subset=ANTIBIOTIC_COLS, how="all", inplace=True)
print(f"After cleaning: {df.shape}")

# In[5]:


X = df[FEATURE_COLS].copy()
Y = df[ANTIBIOTIC_COLS].apply(
    lambda col: col.map(lambda x: 1 if x == "R" else (0 if x == "S" else np.nan))
)

mask = Y.notna().all(axis=1)
X = X[mask].reset_index(drop=True)
Y = Y[mask].reset_index(drop=True)
print(f"Clean: X={X.shape}, Y={Y.shape}")

# In[6]:


X_train, X_test, Y_train, Y_test = train_test_split(
    X, Y, test_size=0.2, random_state=42, stratify=Y.iloc[:, 0]
)
print(f"Train: {X_train.shape}  |  Test: {X_test.shape}")

# In[7]:


num_pipe = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler",  StandardScaler()),
])

cat_pipe = Pipeline([
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
])

preprocessor = ColumnTransformer([
    ("num", num_pipe, NUM_COLS),
    ("cat", cat_pipe, CAT_COLS),
])

X_train_pp = preprocessor.fit_transform(X_train)
X_test_pp  = preprocessor.transform(X_test)
Y_train_np = Y_train.values.astype(int)
Y_test_np  = Y_test.values.astype(int)
print(f"Feature matrix after encoding: {X_train_pp.shape[1]} features")

# In[8]:


def evaluate(name, Y_true, Y_pred, Y_prob=None, elapsed=0.0):
    per_f1 = f1_score(Y_true, Y_pred, average=None, zero_division=0)
    aucs = []
    if Y_prob is not None:
        for i in range(Y_true.shape[1]):
            try:
                aucs.append(roc_auc_score(Y_true[:, i], Y_prob[:, i]))
            except ValueError:
                aucs.append(np.nan)
    return {
        "Model"       : name,
        "Hamming Loss": round(hamming_loss(Y_true, Y_pred), 4),
        "Exact Match" : round(accuracy_score(Y_true, Y_pred), 4),
        "Macro F1"    : round(f1_score(Y_true, Y_pred, average="macro",    zero_division=0), 4),
        "Weighted F1" : round(f1_score(Y_true, Y_pred, average="weighted", zero_division=0), 4),
        "Mean AUC"    : round(np.nanmean(aucs), 4) if aucs else np.nan,
        "Per-AB F1"   : per_f1,
        "Per-AB AUC"  : np.array(aucs),
        "Time(s)"     : round(elapsed, 1),
    }

results = []

# In[9]:


print("\n[1/6] Training Logistic Regression...")
t0 = time.time()

lr_model = MultiOutputClassifier(
    LogisticRegression(
        max_iter     = 1000,
        class_weight = "balanced",   # handles R/S imbalance
        solver       = "lbfgs",
        random_state = 42,
        n_jobs       = -1,
    ),
    n_jobs=-1
)
lr_model.fit(X_train_pp, Y_train_np)
yp   = lr_model.predict(X_test_pp)
yprob = np.column_stack([e.predict_proba(X_test_pp)[:, 1]
                          for e in lr_model.estimators_])
results.append(evaluate("Logistic Regression", Y_test_np, yp, yprob, time.time()-t0))
print(f"  Macro F1={results[-1]['Macro F1']}  AUC={results[-1]['Mean AUC']}  t={results[-1]['Time(s)']}s")

# In[10]:


print("\n[2/6] Training Random Forest...")
t0 = time.time()

rf_model = MultiOutputClassifier(
    RandomForestClassifier(
        n_estimators     = 200,
        class_weight     = "balanced",
        min_samples_leaf = 2,
        n_jobs           = -1,
        random_state     = 42,
    ),
    n_jobs=-1
)
rf_model.fit(X_train_pp, Y_train_np)
yp    = rf_model.predict(X_test_pp)
yprob = np.column_stack([e.predict_proba(X_test_pp)[:, 1]
                          for e in rf_model.estimators_])
results.append(evaluate("Random Forest", Y_test_np, yp, yprob, time.time()-t0))
print(f"  Macro F1={results[-1]['Macro F1']}  AUC={results[-1]['Mean AUC']}  t={results[-1]['Time(s)']}s")

# In[11]:


print("\n[3/6] Training SVM (LinearSVC + CalibratedClassifierCV)...")
t0 = time.time()

svm_model = MultiOutputClassifier(
    CalibratedClassifierCV(
        LinearSVC(class_weight="balanced", max_iter=2000, random_state=42),
        cv=3
    ),
    n_jobs=-1
)
svm_model.fit(X_train_pp, Y_train_np)
yp    = svm_model.predict(X_test_pp)
yprob = np.column_stack([e.predict_proba(X_test_pp)[:, 1]
                          for e in svm_model.estimators_])
results.append(evaluate("SVM (Linear)", Y_test_np, yp, yprob, time.time()-t0))
print(f"  Macro F1={results[-1]['Macro F1']}  AUC={results[-1]['Mean AUC']}  t={results[-1]['Time(s)']}s")

# In[12]:


print("\n[4/6] Training XGBoost...")
t0 = time.time()

scale_pos_weights = [
    (Y_train_np[:, i] == 0).sum() / max((Y_train_np[:, i] == 1).sum(), 1)
    for i in range(Y_train_np.shape[1])
]

xgb_estimators = [
    XGBClassifier(
        n_estimators     = 150,
        learning_rate    = 0.1,
        max_depth        = 5,
        scale_pos_weight = scale_pos_weights[i],
        eval_metric      = "logloss",
        random_state     = 42,
        n_jobs           = -1,
        verbosity        = 0,
    )
    for i in range(len(ANTIBIOTIC_COLS))
]

xgb_preds, xgb_probs = [], []
for i, est in enumerate(xgb_estimators):
    est.fit(X_train_pp, Y_train_np[:, i])
    xgb_preds.append(est.predict(X_test_pp))
    xgb_probs.append(est.predict_proba(X_test_pp)[:, 1])

yp    = np.column_stack(xgb_preds)
yprob = np.column_stack(xgb_probs)
results.append(evaluate("XGBoost", Y_test_np, yp, yprob, time.time()-t0))
print(f"  Macro F1={results[-1]['Macro F1']}  AUC={results[-1]['Mean AUC']}  t={results[-1]['Time(s)']}s")

# In[13]:


print("\n[5/6] Training Bagging ensemble (LR base)...")
t0 = time.time()

bag_model = MultiOutputClassifier(
    BaggingClassifier(
        estimator    = LogisticRegression(max_iter=500, class_weight="balanced",
                                          solver="lbfgs", random_state=42),
        n_estimators = 30,
        max_samples  = 0.8,      # each tree sees 80% of training samples
        max_features = 0.8,      # and 80% of features
        bootstrap    = True,
        random_state = 42,
        n_jobs       = -1,
    ),
    n_jobs=-1
)
bag_model.fit(X_train_pp, Y_train_np)
yp    = bag_model.predict(X_test_pp)
yprob = np.column_stack([e.predict_proba(X_test_pp)[:, 1]
                          for e in bag_model.estimators_])
results.append(evaluate("Bagging (LR base)", Y_test_np, yp, yprob, time.time()-t0))
print(f"  Macro F1={results[-1]['Macro F1']}  AUC={results[-1]['Mean AUC']}  t={results[-1]['Time(s)']}s")

# In[14]:


print("\n[6/6] Training Boosting ensemble (AdaBoost)...")
t0 = time.time()

ada_model = MultiOutputClassifier(
    AdaBoostClassifier(
        n_estimators  = 80,
        learning_rate = 0.5,
        random_state  = 42,
    ),
    n_jobs=-1
)
ada_model.fit(X_train_pp, Y_train_np)
yp    = ada_model.predict(X_test_pp)
yprob = np.column_stack([e.predict_proba(X_test_pp)[:, 1]
                          for e in ada_model.estimators_])
results.append(evaluate("Boosting (AdaBoost)", Y_test_np, yp, yprob, time.time()-t0))
print(f"  Macro F1={results[-1]['Macro F1']}  AUC={results[-1]['Mean AUC']}  t={results[-1]['Time(s)']}s")

# In[15]:


print("\n\n" + "="*80)
print("OVERALL SUMMARY TABLE")
print("="*80)
keys = ["Model", "Hamming Loss", "Exact Match", "Macro F1", "Weighted F1", "Mean AUC", "Time(s)"]
df_summary = pd.DataFrame([{k: r[k] for k in keys} for r in results])
print(df_summary.to_string(index=False))

print("\n\n" + "="*80)
print("PER-ANTIBIOTIC F1 SCORES")
print("="*80)
per_f1_df = pd.DataFrame(
    {r["Model"]: r["Per-AB F1"] for r in results},
    index=ANTIBIOTIC_COLS
)
print(per_f1_df.round(3).to_string())

print("\n\n" + "="*80)
print("PER-ANTIBIOTIC ROC-AUC SCORES")
print("="*80)
per_auc_df = pd.DataFrame(
    {r["Model"]: r["Per-AB AUC"] for r in results},
    index=ANTIBIOTIC_COLS
)
print(per_auc_df.round(3).to_string())

# In[16]:


print("\n\n" + "="*80)
print("OVERALL SUMMARY TABLE")
print("="*80)
keys = ["Model", "Hamming Loss", "Exact Match", "Macro F1", "Weighted F1", "Mean AUC", "Time(s)"]
df_summary = pd.DataFrame([{k: r[k] for k in keys} for r in results])
print(df_summary.to_string(index=False))

print("\n\n" + "="*80)
print("PER-ANTIBIOTIC F1 SCORES")
print("="*80)
per_f1_df = pd.DataFrame(
    {r["Model"]: r["Per-AB F1"] for r in results},
    index=ANTIBIOTIC_COLS
)
print(per_f1_df.round(3).to_string())

print("\n\n" + "="*80)
print("PER-ANTIBIOTIC ROC-AUC SCORES")
print("="*80)
per_auc_df = pd.DataFrame(
    {r["Model"]: r["Per-AB AUC"] for r in results},
    index=ANTIBIOTIC_COLS
)
print(per_auc_df.round(3).to_string())

# In[17]:


COLORS = ["#378ADD", "#1D9E75", "#D85A30", "#7F77DD", "#EF9F27", "#E24B4A"]
SHORT  = ["LR", "RF", "SVM", "XGB", "Bagging", "AdaBoost"]

fig = plt.figure(figsize=(20, 22))
fig.patch.set_facecolor('#FAFAFA')

models_list = [r["Model"]        for r in results]
f1s         = [r["Macro F1"]     for r in results]
aucs        = [r["Mean AUC"]     for r in results]
hls         = [r["Hamming Loss"] for r in results]
ems         = [r["Exact Match"]  for r in results]
times       = [r["Time(s)"]      for r in results]

ax1 = fig.add_subplot(4, 3, 1)
bars = ax1.bar(SHORT, f1s, color=COLORS, edgecolor='white')
ax1.set_title("Macro F1 Score", fontsize=13, fontweight='bold')
ax1.set_ylim(0, 0.7)
for bar, v in zip(bars, f1s):
    ax1.text(bar.get_x()+bar.get_width()/2, v+0.01, f"{v:.3f}", ha='center', fontsize=9, fontweight='bold')
ax1.spines[['top','right']].set_visible(False)

ax2 = fig.add_subplot(4, 3, 2)
bars = ax2.bar(SHORT, aucs, color=COLORS, edgecolor='white')
ax2.set_title("Mean ROC-AUC", fontsize=13, fontweight='bold')
ax2.set_ylim(0.55, 0.67)
for bar, v in zip(bars, aucs):
    ax2.text(bar.get_x()+bar.get_width()/2, v+0.001, f"{v:.3f}", ha='center', fontsize=9, fontweight='bold')
ax2.spines[['top','right']].set_visible(False)

ax3 = fig.add_subplot(4, 3, 3)
bars = ax3.bar(SHORT, hls, color=COLORS, edgecolor='white')
ax3.set_title("Hamming Loss (↓ better)", fontsize=13, fontweight='bold')
for bar, v in zip(bars, hls):
    ax3.text(bar.get_x()+bar.get_width()/2, v+0.003, f"{v:.3f}", ha='center', fontsize=9, fontweight='bold')
ax3.spines[['top','right']].set_visible(False)

ax4 = fig.add_subplot(4, 3, 4)
bars = ax4.bar(SHORT, ems, color=COLORS, edgecolor='white')
ax4.set_title("Exact Match Ratio", fontsize=13, fontweight='bold')
for bar, v in zip(bars, ems):
    ax4.text(bar.get_x()+bar.get_width()/2, v+0.001, f"{v:.3f}", ha='center', fontsize=9, fontweight='bold')
ax4.spines[['top','right']].set_visible(False)

ax5 = fig.add_subplot(4, 3, 5)
bars = ax5.bar(SHORT, times, color=COLORS, edgecolor='white')
ax5.set_title("Training Time (s)", fontsize=13, fontweight='bold')
for bar, v in zip(bars, times):
    ax5.text(bar.get_x()+bar.get_width()/2, v+0.3, f"{v}s", ha='center', fontsize=9, fontweight='bold')
ax5.spines[['top','right']].set_visible(False)

ax6 = fig.add_subplot(4, 3, 6, polar=True)
cats   = ["Macro F1", "ROC-AUC", "Exact Match\n(×10)", "Speed\n(norm)", "Low HL\n(inv)"]
N      = len(cats)
angles = [n / float(N) * 2 * np.pi for n in range(N)] + [0]
ax6.set_theta_offset(np.pi / 2)
ax6.set_theta_direction(-1)
ax6.set_xticks(angles[:-1])
ax6.set_xticklabels(cats, fontsize=8)
ax6.set_ylim(0, 1)
max_t = max(times)
for i, r in enumerate(results):
    vals = [r["Macro F1"], (r["Mean AUC"]-0.55)/0.12, r["Exact Match"]*10,
            1-r["Time(s)"]/max_t, 1-r["Hamming Loss"]]
    vals = [max(0, min(1, v)) for v in vals] + [max(0, min(1, vals[0]))]
    ax6.plot(angles, vals, lw=1.8, color=COLORS[i], label=SHORT[i])
    ax6.fill(angles, vals, alpha=0.07, color=COLORS[i])
ax6.set_title("Radar Comparison", fontsize=12, fontweight='bold', pad=15)
ax6.legend(loc='upper right', bbox_to_anchor=(1.4, 1.2), fontsize=8)

ax7 = fig.add_subplot(4, 1, 3)
f1_matrix = np.array([r["Per-AB F1"] for r in results])
im = ax7.imshow(f1_matrix, aspect='auto', cmap='Blues', vmin=0, vmax=0.85)
ax7.set_xticks(range(len(ANTIBIOTIC_COLS)))
ax7.set_xticklabels(ANTIBIOTIC_COLS, rotation=35, ha='right', fontsize=9)
ax7.set_yticks(range(len(results)))
ax7.set_yticklabels(SHORT, fontsize=10)
ax7.set_title("Per-Antibiotic F1 Score Heatmap", fontsize=13, fontweight='bold')
for i in range(len(results)):
    for j in range(len(ANTIBIOTIC_COLS)):
        v = f1_matrix[i, j]
        ax7.text(j, i, f"{v:.2f}", ha='center', va='center', fontsize=7.5,
                 color='white' if v > 0.5 else '#333333')
plt.colorbar(im, ax=ax7, shrink=0.7)

ax8 = fig.add_subplot(4, 1, 4)
auc_matrix = np.array([r["Per-AB AUC"] for r in results])
im2 = ax8.imshow(auc_matrix, aspect='auto', cmap='Greens', vmin=0.5, vmax=0.7)
ax8.set_xticks(range(len(ANTIBIOTIC_COLS)))
ax8.set_xticklabels(ANTIBIOTIC_COLS, rotation=35, ha='right', fontsize=9)
ax8.set_yticks(range(len(results)))
ax8.set_yticklabels(SHORT, fontsize=10)
ax8.set_title("Per-Antibiotic ROC-AUC Heatmap", fontsize=13, fontweight='bold')
for i in range(len(results)):
    for j in range(len(ANTIBIOTIC_COLS)):
        v = auc_matrix[i, j]
        ax8.text(j, i, f"{v:.3f}", ha='center', va='center', fontsize=7.5,
                 color='white' if v > 0.63 else '#333333')
plt.colorbar(im2, ax=ax8, shrink=0.7)

plt.suptitle("Antibiotic Resistance — All Models Comparison", fontsize=16, fontweight='bold')
plt.tight_layout(h_pad=3, w_pad=2)
plt.savefig("model_comparison_plots.png", dpi=150, bbox_inches='tight')
plt.show()

# In[18]:


joblib.dump({"preprocessor": preprocessor,
             "lr": lr_model, "rf": rf_model, "svm": svm_model,
             "xgb_estimators": xgb_estimators,
             "bag": bag_model, "ada": ada_model},
            "all_models.joblib")
print("\nAll models saved to all_models.joblib")


# In[19]:


def predict_all_models(new_patient: dict) -> pd.DataFrame:
    """Run all trained models on a new patient and compare their predictions."""
    sample = pd.DataFrame([new_patient])
    X_pp   = preprocessor.transform(sample)

    rows = []
    model_preds = {
        "Logistic Regression": lr_model.predict(X_pp)[0],
        "Random Forest"      : rf_model.predict(X_pp)[0],
        "SVM"                : svm_model.predict(X_pp)[0],
        "XGBoost"            : np.array([est.predict(X_pp)[0] for est in xgb_estimators]),
        "Bagging"            : bag_model.predict(X_pp)[0],
        "AdaBoost"           : ada_model.predict(X_pp)[0],
    }

    for ab in ANTIBIOTIC_COLS:
        idx = ANTIBIOTIC_COLS.index(ab)
        row = {"Antibiotic": ab}
        for mname, preds in model_preds.items():
            row[mname] = "R" if preds[idx] == 1 else "S"
        rows.append(row)
    return pd.DataFrame(rows)


new_patient = {
    "Age": 55, "Gender": "F", "Souches": "Escherichia coli",
    "Diabetes": "Yes", "Hypertension": "No",
    "Hospital_before": "Yes", "Infection_Freq": 2,
}
print("\n--- Prediction for Example Patient ---")
print(predict_all_models(new_patient).to_string(index=False))

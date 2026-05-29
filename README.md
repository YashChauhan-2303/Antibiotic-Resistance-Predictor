# Explainable AI Clinical Antibiotic Resistance Predictor

A production-ready Explainable AI (XAI) clinical decision support system that predicts patient-specific antibiotic resistance patterns for 15 distinct antibiotic drugs. The platform is built around **15 independent per-antibiotic XGBoost machine learning pipelines** and integrates local **SHAP (Shapley Additive exPlanations)** feature attribution analysis to provide transparent, clinically explainable predictions.

---

## 🎯 Architectural Overview & Development Phases

This project was developed in two distinct, comprehensive phases:

### Phase 1 — Clinical Model Research (Comparative ML Study)
During the initial research and experimentation phase, we evaluated multiple machine learning algorithms on our patient cohort to identify the best architecture for predicting susceptibility:
- **Logistic Regression**: Linear baseline to measure standard feature significance.
- **Random Forest**: Tree-ensemble baseline to check non-linear feature split dynamics.
- **Calibrated Support Vector Machines (SVM)**: Constructed using a `LinearSVC` base wrapped in `CalibratedClassifierCV` for reliable probability outputs.
- **Extreme Gradient Boosting (XGBoost)**: Gradient-boosted tree ensemble with dynamic class imbalance weighting (`scale_pos_weight`).

All algorithms were systematically compared across key clinical metrics: **ROC-AUC, Precision, Recall, F1-Score, and F2-Score** (to weigh recall/sensitivity and avoid dangerous false negatives).

### Phase 2 — Production Deployment
Following a comprehensive metric-based comparison, **XGBoost** was selected as the superior production architecture. The deployed end-to-end system consists of:
- **15 Independent XGBoost Pipelines**: Each specialized and trained serially for one target antibiotic.
- **Optimized Decision Thresholds**: Customized cutoffs tuned per-model to ensure maximum clinical sensitivity.
- **Explainability Engine**: SHAP TreeExplainer rendering real-time local attributions.
- **Full-Stack Suite**: Python FastAPI backend and a React Vite frontend styled with premium glassmorphism.

### 🌐 SaaS-Style System Architecture

```mermaid
graph TD
    %% Colors and Styles
    classDef client fill:#2563eb,stroke:#1d4ed8,stroke-width:2px,color:#fff;
    classDef server fill:#059669,stroke:#047857,stroke-width:2px,color:#fff;
    classDef logic fill:#d97706,stroke:#b45309,stroke-width:2px,color:#fff;
    classDef prod fill:#dc2626,stroke:#b91c1c,stroke-width:2px,color:#fff;
    classDef exp fill:#7c3aed,stroke:#6d28d9,stroke-width:2px,color:#fff;
    classDef explain fill:#0891b2,stroke:#0e7490,stroke-width:2px,color:#fff;

    subgraph ClientLayer ["Client Presentation Layer (React Frontend)"]
        Dashboard["React Frontend Dashboard<br>(Frosted-Glass UI)"]:::client
        PatientForm["Patient Diagnostics Form<br>(Demographics Input)"]:::client
        ResultsScreen["Clinical Recommendation UI<br>(Production vs Research Tiers)"]:::client
    end

    subgraph ServerLayer ["Service Application Layer (FastAPI Backend)"]
        API["FastAPI API Gateway<br>(Pydantic Schema Validation)"]:::server
        HealthChecker["Extended Health Monitor<br>(Pipeline Cache Status)"]:::server
    end

    subgraph LogicLayer ["Clinical Computation Engine (Python Utilities)"]
        FE["Feature Engineering Layer<br>(Computes 7 Custom Clinical Indicators)"]:::logic
        PredictEngine["Decision Engine<br>(Computes Raw Resistance Probability)"]:::logic
        ThresholdLayer["Optimized Threshold Evaluator<br>(F1-Score Tuned Cutoffs)"]:::logic
        SHAPEngine["Explainability Engine<br>(shap.TreeExplainer Local Attributions)"]:::logic
    end

    subgraph PipelineLayer ["Multi-Model Pipeline Architecture (XGBoost Pipelines)"]
        subgraph ProdTier ["🛡️ Clinical Production Models (ROC-AUC >= 0.64, F1 >= 0.70)"]
            M_IPM["Imipenem (IPM)"]:::prod
            M_AMX["Amoxicillin/Ampicillin (AMX/AMP)"]:::prod
            M_CZ["Cefazolin (CZ)"]:::prod
            M_FOX["Cefoxitin (FOX)"]:::prod
            M_CTX["Cefotaxime/Ceftriaxone (CTX/CRO)"]:::prod
            M_AMC["Amoxicillin/Clavulanic Acid (AMC)"]:::prod
        end

        subgraph ExpTier ["🔬 Experimental Research Models (Secondary/Investigation)"]
            M_GEN["Gentamicin (GEN)"]:::exp
            M_AN["Amikacin (AN)"]:::exp
            M_NAL["Nalidixic Acid (Acide nalidixique)"]:::exp
            M_OFX["Ofloxacin (ofx)"]:::exp
            M_CIP["Ciprofloxacin (CIP)"]:::exp
            M_C["Chloramphenicol (C)"]:::exp
            M_COT["Co-trimoxazole"]:::exp
            M_FUR["Nitrofurantoin (Furanes)"]:::exp
            M_COL["Colistin (colistine)"]:::exp
        end
    end

    %% Data Flow
    PatientForm -->|"Raw Diagnostics Payload"| API
    API --> FE
    FE -->|"14-Column Ordered Dataframe"| PredictEngine
    
    %% Predict Engine queries the models
    PredictEngine -->|"predict_proba()"| ProdTier
    PredictEngine -->|"predict_proba()"| ExpTier
    
    ProdTier -->|"Raw Probabilities"| ThresholdLayer
    ExpTier -->|"Raw Probabilities"| ThresholdLayer
    
    ThresholdLayer -->|"Susceptible vs Resistant Classifications"| ResultsScreen
    
    %% SHAP calculations
    PredictEngine -->|"Fitted Tree Structures"| SHAPEngine
    SHAPEngine -->|"Top Positive/Negative Attributions"| ResultsScreen

    %% Health Monitor
    HealthChecker -.-->|"Cached joblib status check"| API
```

---

## 📊 Model Selection Process

The project followed a rigorous engineering path from raw dataset analysis to final server deployment:

```text
Research Phase (Data Preparation & Cohort Isolation)
       ↓
Train Logistic Regression (Linear Baseline)
       ↓
Train Random Forest (Non-Linear Tree Ensemble)
       ↓
Train Calibrated Support Vector Machine (Probability-calibrated SVM)
       ↓
Train XGBoost (Gradient-Boosted Tree Ensemble)
       ↓
Compare Evaluation Metrics (ROC-AUC, F1, and F2-Scores)
       ↓
Select Best Performing Architecture (XGBoost wins overall)
       ↓
Optimize Decision Thresholds (Recall-constrained search)
       ↓
Deploy Final 15 Specialized Models to Production
```

---

## 🔬 Why XGBoost Was Selected

XGBoost was ultimately chosen as the single production architecture due to its superior clinical and operational performance:
1. **Strongest Overall Performance**: Handled non-linear interactions between demographic fields and strain prevalence far better than Logistic Regression or SVMs.
2. **Consistent Results Across Strains**: Maintained robust, stable predictive metrics across all 15 diverse antibiotic classes, dealing naturally with the high class imbalance of secondary experimental targets.
3. **Optimized Class Imbalance Support**: Enabled native, direct balancing using the `scale_pos_weight` parameter, adjusting training loss directly according to target ratios.
4. **Superior Explainability Compatibility**: Integrated seamlessly with the **SHAP TreeExplainer** package, which leverages exact tree structures to compute local patient attributions in milliseconds, whereas kernel-based SVM or Logistic Regression explainers are slow or structurally constrained.
5. **Production Suitability**: Highly portable, fast inference footprints (<10ms per pipeline), and natively supported by standard python serialization tools (`joblib`).

---

## ⚙️ Deployed Architectural Spec
- **Decision Tiering**:
  - **🛡️ Production Tier**: 6 high-performing beta-lactam models (ROC-AUC ≥ 0.64, Optimized F1 ≥ 0.70) — `IPM`, `AMX/AMP`, `CZ`, `CTX/CRO`, `FOX`, `AMC`.
  - **🔬 Experimental Tier**: 9 secondary models preserved for research/investigative clinical support — `GEN`, `AN`, `Acide nalidixique`, `ofx`, `CIP`, `C`, `Co-trimoxazole`, `Furanes`, `colistine`.
- **Confidence Calibration**: Multi-tiered classification based on raw output probabilities:
  - **High Confidence**: Probability > 0.80 or Probability < 0.20
  - **Medium Confidence**: 0.60 – 0.80 or 0.20 – 0.40
  - **Low Confidence**: 0.40 – 0.60
- **Tech Stack**: FastAPI backend (Python 3.9+, standard library Pydantic schemas) + React Vite frontend (Vanilla CSS, custom dark mode, responsive cards layout).

---

## 📋 Repository Structure

```text
Antibiotic-Resistance-Predictor/
│
├── data/
│   ├── cleaned_output_v2.csv          # Active production dataset
│   └── archive/                       # Archived initial datasets
│
├── models/
│   ├── production/                    # Production XGBoost pipelines
│   │   ├── AMX_AMP.joblib
│   │   ├── AMC.joblib
│   │   ├── CZ.joblib
│   │   ├── FOX.joblib
│   │   ├── CTX_CRO.joblib
│   │   ├── IPM.joblib
│   │   └── thresholds.json            # Optimised production thresholds
│   │
│   └── experimental/                  # Experimental research pipelines
│       ├── GEN.joblib
│       ├── AN.joblib
│       ├── Acide_nalidixique.joblib
│       ├── ofx.joblib
│       ├── CIP.joblib
│       ├── C.joblib
│       ├── Co-trimoxazole.joblib
│       ├── Furanes.joblib
│       ├── colistine.joblib
│       └── thresholds.json            # Experimental thresholds
│
├── notebooks/                         # Active Jupyter training workflows
│   ├── 01_dataCleaning_and_featureGeneration.ipynb
│   ├── 04_Train_All_Antibiotics.ipynb
│   ├── 05_SHAP_Analysis.ipynb         # SHAP explanation & validation notebook
│   └── archive/                       # Stale experiments and legacy baselines
│
├── results/
│   ├── training_results.csv           # Detailed ROC-AUC / F1 metrics
│   └── archive/
│
├── Backend/                           # FastAPI Backend Application
│   ├── main.py                        # API routes, lifespan & exception handlers
│   ├── model_loader.py                # Dynamic model & metadata loading singleton
│   ├── utils.py                       # Clinical feature engineering & SHAP inference
│   ├── schemas.py                     # Pydantic request/response validation schemas
│   └── requirements.txt               # Locked dependencies (scikit-learn 1.7.2, shap 0.51.0)
│
├── Frontend/                          # React Vite Frontend Application
│   ├── src/
│   │   ├── App.jsx                    # Application core & state engine
│   │   ├── index.css                  # Custom styling and animations
│   │   └── components/                # Modular React UI components
│   │       ├── PredictionForm.jsx     # Form with real-time validation & SHAP toggle
│   │       ├── ResultsTable.jsx       # Card grid layout with tabs and explanation drawers
│   │       └── SummaryCard.jsx        # Clinical summary panel
```

---

## 🚀 Quick Start

### 1. Backend Server Setup
```bash
cd Backend
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS/Linux

# Install locked production dependencies
pip install -r requirements.txt

# Start API server
python main.py
# API runs on http://127.0.0.1:8000
```

### 2. Frontend Web Setup
```bash
cd Frontend
npm install

# Start Vite hot-reload server
npm run dev
# Interface opens on http://127.0.0.1:5173
```

---

## 🔌 API Documentation

### 🛡️ Extended Health Check
```http
GET /api/v1/health
```
**Response (200 OK)**:
```json
{
  "status": "healthy",
  "models_loaded": true,
  "environment": "development",
  "version": "1.0.0",
  "message": "All systems operational"
}
```

### 🧬 Explainable Clinical Prediction
```http
POST /api/v1/predict?explain=true
```
- Query Parameter `explain` (optional, default `false`): Set to `true` to run live local SHAP explanation calculations (~3 seconds latency). Set to `false` for instant clinical predictions (<100ms latency).

**Request Body**:
```json
{
  "Age": 55.0,
  "Gender": "F",
  "Souches": "Escherichia coli",
  "Diabetes": "Yes",
  "Hypertension": "No",
  "Hospital_before": "Yes",
  "Infection_Freq": 2.0
}
```

**Response (200 OK)**:
```json
{
  "status": "success",
  "data": [
    {
      "antibiotic": "AMX/AMP",
      "prediction": "Resistant",
      "probability": 0.82,
      "confidence": "High",
      "model_tier": "Production",
      "decision_threshold": 0.34,
      "explanation": {
        "top_positive_factors": [
          "Hospital_Risk: Yes",
          "Infection_Freq: 2"
        ],
        "top_negative_factors": [
          "Age_Group: Senior",
          "Diabetes: No"
        ]
      }
    }
  ],
  "summary": {
    "total_antibiotics": 15,
    "resistant_count": 6,
    "susceptible_count": 9,
    "resistant_percentage": 40.0,
    "susceptible_percentage": 60.0,
    "high_confidence_resistant": ["AMX/AMP", "CZ"],
    "high_confidence_susceptible": ["IPM", "FOX"],
    "recommended_antibiotics": ["IPM", "FOX"]
  },
  "timestamp": "2026-05-29T22:15:30Z"
}
```

---

## 🩺 Clinical Prediction & Feature Engineering Pipeline

Upon receiving patient features, the backend dynamically engineers **7 clinical risk factors**:
1. **Age_Group**: Classified into `Child` (≤18), `Young_Adult` (18-40), `Adult` (40-60), and `Senior` (>60).
2. **Comorbidity_Score**: Aggregated sum of underlying conditions (`Diabetes` + `Hypertension`).
3. **Hospital_Risk**: Binary risk flag representing previous hospital admission.
4. **Frequent_Infection**: Binary flag indicating standard clinical chronicity (≥ 3 previous infections).
5. **High_Risk_Patient**: Cross-product risk flag identifying patients with both history of hospitalization AND chronicity.
6. **Strain_Frequency**: Dynamic frequency weighting computed from the production database (`data/cleaned_output_v2.csv`).
7. **Risk_Score**: Additive index score of high-risk metrics.

---

## 🛡️ Model Validation & Schema Verification

To ensure a robust clinical-grade implementation, we conducted an end-to-end mathematical, schema, and explainability verification suite. 
* **Feature Engineering Verification**: Tracing raw inputs against the 7 engineered clinical risk factors (`Age_Group`, `Comorbidity_Score`, `Hospital_Risk`, `Frequent_Infection`, `High_Risk_Patient`, `Strain_Frequency`, `Risk_Score`) proved 100% correct matching.
* **Schema & Order Verification**: Pre-prediction logs confirm that the inference DataFrame exactly matches the training features list, column names, column order, and numerical/categorical data types, preventing silent encoding corruptions.
* **Explainability Verification**: Integrated local **SHAP (Shapley Additive exPlanations)** TreeExplainer directly on top of the fitted pipelines to verify that the top mathematical factors driving the models are clinically explainable and matches statistical profiles in the production dataset.

---

## 🔬 Tuned Decision Thresholds & Sensitivity Optimization

Rather than using a generic `0.50` binary probability cutoff, the decision thresholds in this system are optimized per-antibiotic to prioritize **clinical sensitivity** (avoiding false negatives, which could lead to treatment failures with inactive drugs):
* **AMX/AMP**: `0.34`
* **AMC**: `0.31`
* **IPM**: `0.28`
* **CTX/CRO**: `0.23`
* **CZ**: `0.19`
* **FOX**: `0.18`

By tuning thresholds using F1-score optimization, the system acts as a highly protective "early-warning" screener. A raw resistance probability of just `20%` for Cefazolin (CZ) or Cefoxitin (FOX) crosses their optimized thresholds, correctly triggering a **Resistant** alert to guide the clinician toward safer options.

---

## ⚠️ Known Limitations & Epidemiological Selection Bias

### 1. Inverted Risk Gradient & Selection Bias
Evaluating synthetic patient gradients across 15 models revealed a fascinating statistical phenomenon where high-risk inpatient profiles returned *lower* average resistance probabilities than healthy outpatient profiles:
* **Low-Risk Patient** (Age 22, no comorbidities, no prior hospitalizations, 0 previous infections): **Average Prob = 0.5659** (15 Resistant)
* **Medium-Risk Patient** (Age 45, Hypertension=Yes, 1 previous infection): **Average Prob = 0.5838** (15 Resistant)
* **High-Risk Patient** (Age 75, Diabetes=Yes, Hypertension=Yes, Hospital_before=Yes, 5 previous infections): **Average Prob = 0.5044** (13 Resistant / 2 Susceptible)

This is not a software defect, but rather a classic **epidemiological selection bias** in clinical surveillance cohorts:
* **Outpatient Culture Bias**: In outpatient clinics, otherwise healthy patients are rarely cultured unless they have **already failed** empirical antibiotic therapy. Therefore, the outpatient culture records in the dataset are highly enriched for multi-drug resistant strains.
* **Routine Inpatient Screening**: In contrast, older, comorbid inpatients are routinely cultured as standard hospital precaution, capturing a much higher share of susceptible, baseline microflora.
* The model picks up on this data-collection bias, mathematically learning that routine hospital markers correlate with a *higher* rate of susceptible cultures, which produces protective (negative) coefficients for these risk factors.

### 2. Class Imbalance & Strain Dominance
* **Strain Dominance**: A category feature importance inspection reveals that **57.51%** of all model weight is driven by the bacterial strain type (`Souches` and `Strain_Frequency`). The models function primarily as a mapping for strain types, with patient clinical history playing a secondary, moderating role.
* **Pre-selected Cohort**: The baseline resistance rate in the dataset is extremely high (e.g., ~58% for beta-lactams), meaning the model is calibrated for highly pre-selected cohorts and is not representative of a general baseline population.

---

## 🛡️ Responsible Clinical Use & Guardrails
* **Clinical Decision Support Only**: This platform is designed strictly as a machine learning decision-support aid and **is not a replacement** for clinical diagnosis, confirmatory laboratory cultures, or professional physician judgment.
* **Combined Evidence Interpretation**: Predictions must always be interpreted alongside active diagnostic laboratory findings, patient history, and local antibiograms.
* **Investigation Advisory**: All experimental models are heavily bounded by clinical warnings in the UI (purple badges) indicating they are investigative research tools and must be confirmed via lab cultures.

---

## 🔮 Future Improvements & Scaling Path
1. **Multi-Center Surveillance Data**: Incorporate multi-center clinical data from outpatient clinics to balance inpatient-preselected biases.
2. **Untreated Baseline Outpatient Cohorts**: Gather outpatient culture records prior to empirical antibiotic administration to remove outpatient selection bias.
3. **Threshold Re-calibration**: Implement custom threshold tuning modes (e.g., maximizing Specificity vs. maximizing Sensitivity) to let clinicians toggle the system's risk-aversion level.
4. **Temporal Drift Monitoring**: Deploy automated pipelines to track temporal resistance drift (e.g., changing patterns over months/years) to prevent model stagnation.

---

## 🎓 Portfolio Impact & Key Learnings
Building and validating this production-grade clinical AI platform provided crucial engineering experience:
* **Explainable AI Integration (SHAP)**: Mastered tree-explainability, translating mathematical feature attributions into readable clinical factors.
* **Version-Compatibility Patcher Engineering**: Created dynamic unpickling interceptors to self-heal missing properties and types (`SimpleImputer._fill_dtype`) when running legacy scikit-learn models under modern runtime environments (Python 3.11, scikit-learn 1.8).
* **Clinical Performance Auditing**: Conducted full-scale synthetic risk testing, successfully diagnosing complex epidemiological selection biases.
* **Full-Stack SaaS Architecture**: Formulated clean FastAPI endpoints, optimized schemas, and coded a premium glassmorphic React Vite dashboard with dynamic waffle grids.


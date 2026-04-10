# 🚀 ResistAI – Multi-Model Antibiotic Resistance Predictor

A full-stack machine learning web application that predicts antibiotic resistance (R/S) using multiple ML models and provides consensus-based recommendations for better clinical decision support.

## 🧠 Project Overview
ResistAI takes patient data as input and predicts whether a bacterial infection will be:
* **Resistant (R)** ❌
* **Susceptible (S)** ✅

It covers **15 different antibiotics** using an ensemble of **6 machine learning models**.

## ⚙️ Tech Stack
### 🔹 Backend
* **FastAPI**
* **Scikit-learn / XGBoost**
* **Pandas / NumPy**
* **Joblib** (Model persistence)

### 🔹 Frontend
* **React (Vite)**
* **Tailwind CSS**
* **PostCSS**

### 🔹 ML Models Used
* Logistic Regression
* Random Forest
* Support Vector Machine (SVM)
* XGBoost (per antibiotic)
* Bagging Classifier
* AdaBoost

## 📊 Features
* 🔮 **Multi-Antibiotic Prediction**: Predict resistance for 15 drugs at once.
* 🤖 **Ensemble Logic**: Uses 6 ML models simultaneously.
* 🧠 **Consensus System**: Final results based on model agreement.
* 📈 **Confidence Scoring**: Reliability per antibiotic.
* 💡 **Clinical Recommendations**: Highlights Susceptible (✅) options.
* 📥 **Data Portability**: Download results for clinical review.

## 🧪 Input Parameters
The model processes 7 patient features:
1.  **Age**
2.  **Gender**
3.  **Bacterial Strain** (Species)
4.  **Diabetes**
5.  **Hypertension**
6.  **Previous Hospitalization**
7.  **Infection Frequency**

## 📁 Project Structure
```text
ML HOSTING/
├── Backend/                # FastAPI Application
│   ├── main.py             # API Entry point
│   ├── model_loader.py     # Model loading logic
│   ├── utils.py            # Helper functions
│   ├── schemas.py          # Pydantic data models
│   ├── config.py           # Environment configurations
│   ├── all_models.joblib   # Serialized ML models
│   ├── Dockerfile          # Backend containerization
│   └── requirements.txt    # Python dependencies
├── Frontend/               # React + Vite Application
│   ├── src/                # UI Components & Logic
│   ├── tailwind.config.js  # Styling configuration
│   ├── Dockerfile          # Frontend containerization
│   └── package.json        # Node dependencies
├── Model/                  # Data Science & Training
│   ├── ml_project2.py      # Training/Experimental script
│   └── cleaned_output.csv  # Processed dataset
└── docker-compose.yml      # Multi-container orchestration
```

## ⚡ Running Locally

### 🔹 Backend

```bash
cd Backend
python -m venv venv
source venv/bin/activate  # venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

**Backend runs on:** `http://127.0.0.1:8000`

### 🔹 Frontend

```bash
cd Frontend
npm install
npm run dev
```

**Frontend runs on:** `http://127.0.0.1:5173`

### 🔹 Using Docker

```bash
docker-compose up --build
```

**Compose deploys both services automatically.**

---

## ⚠️ Important Notes

### Clinical Disclaimer
⚠️ **Predictions are influenced by historical antibiotic resistance patterns.** Clinical decisions should always be made in consultation with healthcare professionals. This is a decision support tool, not a replacement for professional medical judgment.

### Data Bias
Predictions may be influenced by historical dataset patterns. Some antibiotics may show bias due to class imbalance in training data.

### Model Confidence
Confidence scores indicate agreement among the 6 models. Higher confidence (>80%) suggests stronger consensus.

---

## 🚀 Production Deployment

### Option 1: Render.com (Recommended)
1. Connect your GitHub repository
2. Deploy Backend as a Web Service
3. Deploy Frontend as a Static Site
4. Set required environment variables

### Option 2: Docker

```bash
docker build -t antibiotic-api:1.0.0 ./Backend
docker run -p 8000:8000 antibiotic-api:1.0.0
```

---

## 🔒 Security

- ✅ Input validation with Pydantic
- ✅ Environment-based configuration
- ✅ Error handling (no stack traces in production)
- ✅ CORS configured for frontend
- ✅ No hardcoded secrets
- ✅ Production logging with rotation

---

## 📊 Performance

- **Model Loading:** Pre-loaded at startup (~3-5s)
- **Prediction Time:** 100-500ms per request
- **Scalability:** Stateless, ready for load balancing
- **Caching:** Models cached in memory

---

**Version:** 1.0.0 Production Ready
**Last Updated:** 2026-04-11
**Status:** ✅ Production Ready
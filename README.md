# GlucoSense — Diabetes Risk Screening

GlucoSense is a local Streamlit application that turns routinely recorded health information into a diabetes risk screening estimate. It includes an end-to-end scikit-learn training pipeline, transparent model comparisons, interactive dataset analytics, and patient-friendly result guidance.

> **Clinical notice:** This is an educational screening aid, not a diagnostic device or emergency service. Predictions and general wellbeing suggestions must not replace care from a qualified clinician.

## Highlights

- Premium healthcare-oriented Streamlit interface with responsive navigation and custom styling
- Patient form for gender, age, hypertension, heart disease, smoking history, BMI, HbA1c, and blood glucose
- Probability, risk band, prediction class, and tailored general lifestyle guidance
- Data validation, duplicate removal, missing-value handling, category encoding, and feature scaling
- Candidate model comparison across Logistic Regression, Decision Tree, Random Forest, and optional XGBoost
- Accuracy, precision, recall, F1, ROC–AUC, feature importance, class balance, distributions, and correlation analytics
- Persisted best model pipeline using Joblib

## Project structure

```text
mini 2/
├── app.py                         # Streamlit application entry point
├── train_model.py                 # Model training and comparison command
├── preprocess.py                  # Shared schema validation and preprocessing
├── dataset/
│   └── diabetes_prediction_dataset.csv
├── model/                         # Generated Joblib model and CSV/JSON reports
├── pages/                         # Home, prediction, analytics, about views
├── utils/                         # Clinical guidance and UI components
├── requirements.txt
└── README.md
```

## Run locally

1. Create and activate a virtual environment (recommended).

2. Install the dependencies:

   ```powershell
   python -m pip install -r requirements.txt
   ```

3. Train and save the model artifacts:

   ```powershell
   python train_model.py
   ```

4. Start the application:

   ```powershell
   streamlit run app.py
   ```

Open the local URL shown by Streamlit, usually `http://localhost:8501`.

## Optional XGBoost

The base project does not require XGBoost. To add it to the comparison, install it before training:

```powershell
python -m pip install xgboost
python train_model.py
```

If it is not installed, the training report records it as skipped and continues with the other models.

## Training behaviour

`train_model.py` reads the CSV from `dataset/`, validates its schema, cleans it, removes duplicates, and makes a stratified 80/20 train-test split. Every classifier receives the same pipeline: median imputation and scaling for numeric fields plus most-frequent imputation and one-hot encoding for categorical fields. The candidate with the strongest test ROC–AUC becomes `model/diabetes_model.joblib`.

Generated files include:

- `model/diabetes_model.joblib` — selected fitted pipeline and metadata
- `model/model_metadata.json` — model choice, metrics, data summary, and importances
- `model/model_comparison.csv` — held-out metrics for each trained candidate
- `model/feature_importance.csv` — selected-model feature importance

## Notes on patient data

The application runs locally. Form entries are stored only in Streamlit's active session so the current result can remain visible while navigating pages. No remote data transmission is implemented by this project.

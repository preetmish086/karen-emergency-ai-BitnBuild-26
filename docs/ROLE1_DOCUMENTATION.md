# Role 1 — Data + Baseline ML Documentation

This document provides a complete technical specification of the dataset pipeline, quality audits, baseline machine learning models, evaluation results, and integration interfaces for **Role 1 (Data + Baseline ML)** in *Karen's Ear*.

---

## 1. Pipeline Overview

The Role 1 pipeline converts raw disaster and humanitarian text data into a cleaned, deduplicated, zero-leakage dataset and trains a lightweight CPU-friendly baseline classifier to predict canonical emergency `incident_type` labels.

```text
CrisisLexT26 + HumAID + Sample Reports
                  ↓
       Centralized Label Mapping
                  ↓
       Deterministic Text Preprocessing
                  ↓
           Text Deduplication
                  ↓
     Stratified Train / Val / Test Split
                  ↓
    Synthetic Training Data Augmentation
                  ↓
     Automated Zero-Leakage & Quality Audit
                  ↓
      TF-IDF + Logistic Regression / Naive Bayes
                  ↓
         Model Persistence (joblib)
                  ↓
      Public Inference Interface (EmergencyClassifier)
```

---

## 2. Dataset Sources & Provenance

1. **CrisisLexT26**:
   * **Location**: `temp_crisislex/data/CrisisLexT26/`
   * **Scope**: 26 crisis event directories containing 27,933 raw records.
   * **Quality Filtering**: Strictly filtered to retain records where `Informativeness == "Related and informative"`.
   * **Metadata Preserved**: `source="crisislex"`, `source_event`, `source_label`, `information_source`, `information_type`, `informativeness`, `is_synthetic=False`.

2. **HumAID**:
   * **Location**: `temp_humaid/` (`train.jsonl`, `dev.jsonl`, `test.jsonl`)
   * **Scope**: 76,484 humanitarian crisis tweets.
   * **Filtering & Defensible Mapping**: Mapped to canonical classes via keyword evidence and defensible class mapping to prevent naive false associations.
   * **Metadata Preserved**: `source="humaid"`, `source_split`, `source_label`, `is_synthetic=False`.

3. **Sample Reports**:
   * **Location**: `data/sample/sample_reports.json` (8 canonical report test cases).

---

## 3. Centralized Label Mapping

All records are mapped to the 10 canonical `incident_type` values specified in [DATA_SCHEMA.md](file:///d:/TEMP%20FILES/BIT%20N%20BUILD/karen-emergency-ai-BitnBuild-26/DATA_SCHEMA.md):
`fire`, `explosion`, `accident`, `medical`, `collapse`, `flood`, `crime`, `missing_person`, `unknown`, `other`.

* **Implementation**: [src/data/mapping.py](file:///d:/TEMP%20FILES/BIT%20N%20BUILD/karen-emergency-ai-BitnBuild-26/src/data/mapping.py)
* **Rules**:
  * Event-level high-confidence mappings (e.g. `2012_Colorado_wildfires` → `fire`, `2013_Boston_bombings` → `explosion`, `2013_Spain_train_crash` → `accident`, `2013_LA_airport_shootings` → `crime`, `2013_Savar_building_collapse` → `collapse`).
  * Explicit text evidence keyword override for `medical`, `missing_person`, `crime`, `collapse`, `explosion`, `fire`, `flood`, `accident`.
  * Fallback for ambiguous events to `other`.

---

## 4. Text Preprocessing & Deduplication

* **Preprocessing** ([src/data/preprocessor.py](file:///d:/TEMP%20FILES/BIT%20N%20BUILD/karen-emergency-ai-BitnBuild-26/src/data/preprocessor.py)): Lowercasing, stripping URLs (`https?://\S+`), removing `@user` handles, cleaning RT prefixes, and normalizing whitespace. Crucial emergency terms (`fire`, `explosion`, `injured`, `trapped`, `evacuate`, `missing`, `collapsed`, `ambulance`, `hospital`) are strictly preserved.
* **Leakage Prevention**: Only cleaned text is passed as feature $X$. Metadata fields (`credibility`, `priority`, `severity`, `actionability`, `location`) are strictly excluded.
* **Deduplication** ([src/data/deduplication.py](file:///d:/TEMP%20FILES/BIT%20N%20BUILD/karen-emergency-ai-BitnBuild-26/src/data/deduplication.py)): Normalizes text and deduplicates duplicate tweets to prevent duplicate text leakage across splits.

---

## 5. Train / Validation / Test Splitting & Synthetic Augmentation

* **Real Dataset Split**: 70% Train, 15% Validation, 15% Test using stratified splitting on `incident_type`.
* **Controlled Synthetic Data**: Added **ONLY** to the Training set (`final_train`) to boost underrepresented classes (`medical`, `missing_person`, `crime`, `collapse`, `explosion`).
* **Synthetic Isolation**: Synthetic records (`is_synthetic=True`) are **STRICTLY PROHIBITED** from entering validation or test sets. Validation and Test splits consist of 100% real emergency data.
* **Audit Enforcement**: `DatasetAuditor.audit_splits()` automatically verifies 0 synthetic leakage and 0 text overlap between train/val/test splits.

---

## 6. Model Architecture & Training Results

Two lightweight CPU-friendly scikit-learn baseline models were implemented:

1. **Primary Model**: `TFIDFLogisticRegressionBaseline`
   * TF-IDF: N-gram range (1, 2), Max features 10,000, Sublinear TF scaling.
   * Classifier: Logistic Regression ($C=1.0$, `max_iter=1000`, `random_state=42`).
2. **Secondary Model**: `TFIDFNaiveBayesBaseline`
   * TF-IDF: N-gram range (1, 2), Max features 10,000.
   * Classifier: Multinomial Naive Bayes ($\alpha=1.0$).

### Validation Performance & Model Selection

| Model | Validation Accuracy | Validation Macro F1 | Status |
| :--- | :--- | :--- | :--- |
| **TF-IDF + Logistic Regression** | **95.40%** | **0.7451** | **SELECTED BEST MODEL** |
| TF-IDF + Multinomial Naive Bayes | 87.62% | 0.6700 | Evaluated |

### Final Evaluation on Held-out Real Test Set (4,272 Test Reports)

* **Test Accuracy**: `95.22%`
* **Test Weighted F1**: `95.08%`
* **Test Macro F1**: `74.44%`
* **Test Macro Precision**: `77.28%`
* **Test Macro Recall**: `72.15%`

#### Per-Class Test Performance Matrix

| Incident Type | Precision | Recall | F1-Score | Support |
| :--- | :--- | :--- | :--- | :--- |
| `accident` | 0.9513 | 0.9883 | **0.9695** | 257 |
| `collapse` | 0.9832 | 0.9435 | **0.9630** | 124 |
| `crime` | 0.9885 | 0.9053 | **0.9451** | 95 |
| `explosion` | 1.0000 | 0.7879 | **0.8814** | 165 |
| `fire` | 0.9928 | 0.9385 | **0.9649** | 439 |
| `flood` | 0.9783 | 0.9481 | **0.9630** | 713 |
| `medical` | 0.8982 | 0.7143 | **0.7958** | 210 |
| `other` | 0.9361 | 0.9894 | **0.9620** | 2267 |

---

## 7. Model Persistence

The selected best model artifact is saved using `joblib` at:
`models/baseline_model.joblib`

The model file is excluded from Git via `.gitignore` (`*.joblib`) and can be reproducibly re-trained at any time.

---

## 8. R2 / R3 Integration Interface

Downstream modules (R2 Clustering & Duplicate Detection, R3 Priority Engine & Dashboard) can import `EmergencyClassifier` to classify raw emergency reports:

```python
from src.models.inference import EmergencyClassifier

# Instantiate classifier (loads models/baseline_model.joblib automatically)
classifier = EmergencyClassifier()

# Single prediction
result = classifier.predict_incident("Huge explosion near the central market! Several injured.")
print(result)
# Output:
# {
#   "incident_type": "explosion",
#   "confidence": 0.9412
# }

# Batch prediction
batch_results = classifier.predict_batch([
    "Smoke coming from a building near Station Road, fire trucks needed!",
    "Water rising rapidly near the riverside area!"
])
```

---

## 9. Commands to Reproduce Pipeline & Run Tests

```bash
# 1. Run full master data & ML training pipeline
python scripts/run_role1_pipeline.py

# 2. Run unit tests
python -m unittest discover -s tests -p "test_*.py"
```

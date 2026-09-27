# 🧠 Role 2: Emergency Response Natural Language Intelligence Module
### NLP Incident Understanding, Strict Casualty Extraction & Credibility Assessment
**Team AlgoRhythm // Bit N Build '26 (Track 2: AI & ML)**

---

## 📌 Overview

**Role 2** is a modular, high-throughput Python engine responsible for **Natural Language Understanding (NLU), Hazard Classification, Strict Zero-Hallucination Casualty Extraction, and Multi-Factor Credibility Scoring**.

In an emergency reporting ecosystem, human distress calls are messy, emotional, and fragmented. Role 2 cuts through this noise to:
1. Ingest unstructured citizen distress reports alongside geographic metadata.
2. Accurately categorize the incident into standardized municipal hazard classes.
3. Extract explicit victim, casualty, and trapped entity figures with **strict zero-hallucination guarantees**.
4. Evaluate report completeness and compute an explainable credibility score ($[0.0, 1.0]$) using an 8-factor signal assessor.
5. Provide a standardized, validated Pydantic JSON contract to the priority ranking engine and the SpidyCAD Dispatcher HUD.

---

## 📁 Repository Structure

```
role2/
├── src/
│   ├── preprocessing/
│   │   ├── text_preprocessor.py        # Case folding, slang normalization & word-to-number parsing
│   │   └── __init__.py
│   ├── classification/
│   │   ├── base.py                     # Abstract Base Class for incident classifiers
│   │   ├── incident_classifier.py      # Hybrid pattern-matcher + TF-IDF multi-class classifier
│   │   └── __init__.py
│   ├── extraction/
│   │   ├── base.py                     # Abstract Base Class for entity extractors
│   │   ├── entity_extractor.py         # Pattern-based casualty extractor (Zero-hallucination)
│   │   ├── completeness_evaluator.py   # Information completeness & critical signal scoring
│   │   └── __init__.py
│   ├── credibility/
│   │   ├── base.py                     # Abstract Base Class for credibility scorers
│   │   ├── credibility_scorer.py       # 8-factor multi-signal observation assessor
│   │   └── __init__.py
│   ├── schemas/
│   │   ├── input_schema.py             # Pydantic input payload contract
│   │   ├── output_schema.py            # Pydantic output contract with factor breakdowns
│   │   └── __init__.py
│   └── pipeline/
│       ├── process_report.py           # End-to-end pipeline orchestrator
│       └── __init__.py
├── tests/
│   ├── test_classification.py          # Multi-hazard categorization unit tests (7 tests)
│   ├── test_extraction.py              # Zero-hallucination casualty extraction tests (4 tests)
│   ├── test_credibility_and_pipeline.py# Pipeline orchestration, schema, & score range tests (3 tests)
│   ├── test_location_and_csv.py        # GPS preservation, landmark geocoding & CSV audit tests (5 tests)
│   └── pytest.ini                      # Pytest configuration
├── data/
│   └── sample/
│       └── sample_reports.json         # Representative emergency report test vectors
├── scripts/
│   └── run_demo.py                     # CLI demonstration execution script
├── docs/
│   ├── architecture.md                 # Detailed mathematical formulas & architectural specs
│   └── integration_role3.md            # Downstream contract for priority ranking & spatial HUD
├── requirements.txt
└── README.md
```

---

## 🔍 Core Engineering Principles

### 1. Multi-Hazard Classification
Categorizes raw reports into standardized emergency types:
- `accident`: Vehicle collisions, highway pileups, pedestrian strikes.
- `fire`: Structural blazes, electrical fires, smoke alerts.
- `flood`: Rising water, flash floods, subway station submergence.
- `explosion`: Gas leaks, transformer blasts, detonations.
- `collapse`: Structural failure, scaffolding collapse, trapped in rubble.
- `medical`: Cardiac arrest, unconsciousness, severe trauma.
- `crime`: Active violence, assault, armed robbery.
- `missing_person`: Lost children, elderly wandering.
- `other` / `unknown`: Ambiguous or unclassified distress.

### 2. Strict Zero-Hallucination Policy
In life-or-death emergency dispatch, **hallucinating casualties is unacceptable**. 
- If a reporter states *"There is smoke in my hallway and people are panicking"*, all casualty fields (`total_affected`, `injured`, `dead`, `missing`, `trapped`, `rescued`, `evacuated`) evaluate strictly to **`null`**.
- Unstated numbers are **never assumed or defaulted to zero**.
- Casualties are only extracted when explicitly stated with cardinal numbers or word numbers (e.g., *"3 people trapped"*, *"two dead"*).

### 3. 8-Factor Decomposed Credibility Engine
Single-number credibility scores are unexplainable and brittle. Role 2 decomposes credibility $[0.0, 1.0]$ across 8 explainable signals:
- **First-Person Observation (0.25):** Sensory indicators (*"I see"*, *"right in front of me"*, *"I can smell"* vs hearsay *"someone said"*).
- **Specificity (0.20):** Precise physical details (exact address, floor, vehicle makes, specific landmarks).
- **Actionability (0.15):** Urgent directives (*"need ambulance immediately"*, *"trapped under car"*).
- **Coherence (0.10):** Syntactic structure and semantic clarity.
- **Internal Consistency (0.10):** Absence of contradictory casualty or location claims.
- **Casualty Reporting Signal (0.05):** Grounded casualty details.
- **Location Density Consensus (0.05):** Spatial corroboration with neighboring reports.
- **Information Completeness (0.10):** Availability of essential dispatcher questions (Who, What, Where).

Missing casualty figures do **not** artificially penalize credibility.

---

## ⚡ Quickstart & Testing

### 1. Prerequisites
- Python 3.11+

### 2. Installation
```bash
pip install -r requirements.txt
```

### 3. Run Standalone CLI Demo
```bash
PYTHONPATH=role2:role2/src python role2/scripts/run_demo.py
```

### 4. Execute Full Test Suite (19 / 19 Tests)
```bash
PYTHONPATH=role2:role2/src pytest role2/tests/ -v
```

Output:
```
role2/tests/test_classification.py::test_fire_classification PASSED
role2/tests/test_classification.py::test_accident_classification PASSED
role2/tests/test_classification.py::test_flood_classification PASSED
role2/tests/test_classification.py::test_explosion_classification PASSED
role2/tests/test_classification.py::test_collapse_classification PASSED
role2/tests/test_classification.py::test_medical_classification PASSED
role2/tests/test_classification.py::test_missing_person_classification PASSED
role2/tests/test_extraction.py::test_zero_hallucination_on_unstated_casualties PASSED
role2/tests/test_extraction.py::test_exact_casualty_extraction PASSED
role2/tests/test_extraction.py::test_word_number_parsing PASSED
role2/tests/test_extraction.py::test_trapped_and_injured_entities PASSED
role2/tests/test_credibility_and_pipeline.py::test_credibility_bounds_and_factors PASSED
role2/tests/test_credibility_and_pipeline.py::test_full_pipeline_output_contract PASSED
role2/tests/test_credibility_and_pipeline.py::test_gps_coordinate_preservation PASSED
role2/tests/test_location_and_csv.py::test_explicit_gps_preservation PASSED
role2/tests/test_location_and_csv.py::test_landmark_auto_resolution PASSED
role2/tests/test_location_and_csv.py::test_borough_default_fallback PASSED
role2/tests/test_location_and_csv.py::test_csv_sanitization_removes_newlines PASSED
role2/tests/test_location_and_csv.py::test_csv_strict_four_column_contract PASSED
============================== 19 passed in 3.40s ==============================
```

---

## 🔗 Integration with Main Platform

Role 2 is directly invoked by the root FastAPI backend ([`backend.py`](../backend.py)) on every report ingestion:
```python
from role2.src.pipeline.process_report import run_pipeline

result = run_pipeline(
    text=payload.text,
    latitude=lat,
    longitude=lon,
    location=location,
    gps_xy=gps_xy
)
```
The resulting structured output feeds downstream into:
1. **The Multi-Attribute Priority Engine** to compute dynamic triage ranks.
2. **The SpidyCAD Streamlit HUD** to display categorized incident badges, casualty counters, and credibility metrics.

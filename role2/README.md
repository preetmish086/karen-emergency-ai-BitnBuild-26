# Role 2: Emergency Response Natural Language Intelligence Module

## Overview

**Role 2** is an independent, modular Python framework responsible for **NLP + Incident Understanding + Credibility Assessment** in an Emergency Reporting and Response System.

Role 2 ingests natural language human emergency reports along with authoritative GPS coordinates, classifies the emergency type, extracts explicit casualty/affected entity numbers without hallucination, measures report completeness, computes an explainable credibility score $[0, 1]$, and emits a validated JSON payload.

---

## ⚠️ Scope & Role Boundaries

- **Role 2 Responsibilities**: Ingests single emergency reports; categorizes incident type; extracts affected/injured/dead/trapped counts; evaluates completeness; computes credibility score; preserves GPS; outputs clean JSON contract.
- **Out of Scope (Explicitly Excluded)**:
  - Role 1 (Dataset ingestion & pipeline)
  - Role 3 (Spatial-temporal report clustering)
  - Role 4 (Emergency priority ranking & dashboard UI)
  - Frontend, backend databases, global UI dashboards.

---

## 📁 Repository Structure

```
role2/
├── src/
│   ├── preprocessing/
│   │   ├── text_preprocessor.py      # Natural language normalization & word-number parsing
│   │   └── __init__.py
│   ├── classification/
│   │   ├── base.py                   # Abstract Base Class for classifiers
│   │   ├── incident_classifier.py    # Hybrid pattern + TF-IDF Naive Bayes classifier
│   │   └── __init__.py
│   ├── extraction/
│   │   ├── base.py                   # Abstract Base Class for extractors
│   │   ├── entity_extractor.py       # Strict pattern-based entity extractor (No hallucination)
│   │   ├── completeness_evaluator.py # Information completeness & availability scoring
│   │   └── __init__.py
│   ├── credibility/
│   │   ├── base.py                   # Abstract Base Class for credibility scorers
│   │   ├── credibility_scorer.py     # Decomposed signal credibility assessor
│   │   └── __init__.py
│   ├── schemas/
│   │   ├── input_schema.py           # Pydantic input contract
│   │   ├── output_schema.py          # Pydantic output contract
│   │   └── __init__.py
│   └── pipeline/
│       ├── process_report.py         # End-to-end pipeline orchestrator
│       └── __init__.py
├── tests/
│   ├── test_classification.py        # Fire, accident, flood, explosion, medical, collapse, missing tests
│   ├── test_extraction.py            # Casualty extraction & strict no-hallucination tests
│   ├── test_credibility_and_pipeline.py # GPS preservation, schema validation, score range tests
│   └── pytest.ini
├── data/
│   └── sample/
│       └── sample_reports.json       # Representative emergency report test samples
├── scripts/
│   └── run_demo.py                   # CLI demonstration execution script
├── docs/
│   ├── architecture.md               # Detailed architectural specs & mathematical formulas
│   └── integration_role3.md          # Downstream contract for Role 3 spatial clustering
├── requirements.txt
└── README.md
```

---

## ⚡ Quickstart & Execution

### 1. Prerequisites
- Python 3.11+

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Demo Script
Processes sample emergency reports and outputs formatted JSON:
```bash
python scripts/run_demo.py
```

### 4. Run Test Suite
Runs all 14 unit and integration tests:
```bash
python -m pytest -v
```

---

## 🔍 Key Architecture & Features

### 1. Incident Categorization
Supported categories:
- `accident`, `fire`, `flood`, `medical`, `explosion`, `collapse`, `crime`, `missing_person`, `other`, `unknown`.

### 2. Strict No-Hallucination Policy
- If a reporter says *"I saw a fire break out in my building."*, all casualty fields (`total_affected`, `injured`, `dead`, `missing`, `trapped`, `rescued`, `evacuated`) evaluate to **`null`**.
- Unstated numbers are **never assumed or defaulted to zero**.

### 3. Decomposed Credibility Assessment
Credibility score $[0.0, 1.0]$ is computed using explainable weights:
- `first_person_observation` (0.25)
- `specificity` (0.20)
- `coherence` (0.15)
- `actionability` (0.15)
- `temporal_presence` (0.10)
- `internal_consistency` (0.15)

Missing casualty details do **not** automatically penalize credibility.

### 4. Preserved GPS Metadata
`latitude` and `longitude` are preserved untouched as authoritative location sources.

---

## 📄 License
Role 2 Module for Emergency Response System. Open-Source & Independent.

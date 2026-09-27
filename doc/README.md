# 📚 Karen's Ear // SpidyCAD Documentation & Technical Papers
### Project Documentation, Scientific Paper & Competition Deliverables
**Team AlgoRhythm // Bit N Build '26 (Track 2: Artificial Intelligence & Machine Learning)**

---

## 📌 Overview

This directory houses the comprehensive academic, technical, architectural, and presentation assets for **Karen's Ear (SpidyCAD)**, engineered for the **Bit N Build '26 Hackathon**.

The centerpiece is the complete, publication-grade technical document detailing the system architecture, mathematical formulations, algorithmic trade-offs, and empirical benchmark results across 8,735 NYC emergency incidents.

---

## 📁 Document Catalog & Files

| File | Type | Description |
| :--- | :--- | :--- |
| [`Karens_Ear_AI_Emergency_Dispatch_Assistant_Project_Document.pdf`](Karens_Ear_AI_Emergency_Dispatch_Assistant_Project_Document.pdf) | **PDF** | **Master Publication Document.** Full 8-section technical paper, mathematical proofs, diagrams, and evaluation metrics. |
| [`Karens_Ear_AI_Emergency_Dispatch_Assistant_Project_Document.tex`](Karens_Ear_AI_Emergency_Dispatch_Assistant_Project_Document.tex) | **LaTeX** | Master LaTeX source code structured with IEEE/ACM conference style formatting. |
| [`main.pdf`](main.pdf) & [`main.tex`](main.tex) | **PDF / TeX** | Alternate compilation target synchronized with the project document. |
| [`Problem statement.pdf`](Problem%20statement.pdf) | **PDF** | Official Bit N Build '26 Track 2 Problem Statement & Evaluation Criteria. |
| [`Karens_Ear_AI_Emergency_Dispatch_Assistant_Project_Document.pages`](Karens_Ear_AI_Emergency_Dispatch_Assistant_Project_Document.pages) | **Apple Pages** | Native design source file for layout and typography drafting. |

---

## 📖 Project Document Table of Contents

The master technical paper ([`Karens_Ear_AI_Emergency_Dispatch_Assistant_Project_Document.pdf`](Karens_Ear_AI_Emergency_Dispatch_Assistant_Project_Document.pdf)) is divided into eight formal sections:

1. **Executive Summary & The Problem Statement:**
   - The cognitive bottleneck of 911 dispatch centers during metropolitan disasters.
   - The Spider-Man / Karen AI operational metaphor.
2. **System Architecture & 6-Phase Pipeline:**
   - Detailed breakdown of $\text{Detect} \to \text{Understand} \to \text{Corroborate} \to \text{Predict} \to \text{Rank} \to \text{Dispatch}$.
3. **Tri-State Relevance Gate & Lexical Safety Net:**
   - Decoupled relevance vs priority.
   - Bigram TF-IDF classification and out-of-vocabulary emergency keyword safety netting.
4. **Role 2 Natural Language Understanding & Credibility:**
   - Multi-hazard incident classification.
   - Strict zero-hallucination casualty extraction.
   - 8-factor decomposed credibility mathematical formulation.
5. **Multi-Attribute Priority Engine & Ranking:**
   - Continuous priority score formula ($0.35S + 0.25C + 0.20A + 0.20f(K)$).
   - Random Forest regression vs heuristic tiering.
   - Automated explainable dispatch reasoner.
6. **SpidyCAD Tactical Command HUD & GPS Resolution:**
   - Pydeck 3D NYC radar map rendering with deterministic micro-jitter.
   - Hierarchical geographic resolution (40+ NYC landmarks).
   - Citizen Speech-to-Text and streaming CSV audit logging.
7. **Empirical Benchmarks & Verification:**
   - Full 35-test automated verification suite (`pytest`).
   - Latency profiles (sub-10ms inference per report).
8. **Team AlgoRhythm Responsibilities & Technical Roadmap:**
   - Individual member contributions (Preetika, Rishav, Ojas, Aditya).
   - Future work: Municipal CAD NG911 telephony SIP/RTP integration and dynamic fleet routing via Google OR-Tools.

---

## 🛠️ Compiling the LaTeX Source

If you have a local TeX distribution (e.g. MacTeX, TeX Live) installed:
```bash
pdflatex doc/Karens_Ear_AI_Emergency_Dispatch_Assistant_Project_Document.tex
```

Alternatively, the `.tex` file is self-contained and ready to import directly into [Overleaf](https://www.overleaf.com) for collaborative editing.

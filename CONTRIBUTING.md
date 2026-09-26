# Contributing Guide

### Main Branch

`main` contains stable, integrated code.

Nobody should directly push to `main`.

---

## Feature Branches

Each member works on their own feature branch.

### Member 1 — NLP + Credibility

feature/nlp-credibility
Owns:

src/nlp/
src/credibility/

### Member 2 — Dataset + ML
feature/dataset-ml

Owns:

src/data/
src/models/


### Member 3 — Clustering + Duplicate Detection
feature/clustering

Owns:

src/clustering/


### Member 4 — Priority + Backend + Dashboard
feature/priority-dashboard

Owns:

src/priority/
src/api/
frontend/

## Rules

1. Never push directly to main.
2. Work only on your assigned feature branch.
3. Pull the latest main before starting major work.
4. Commit frequently.
5. Use meaningful commit messages.
6. Push your branch regularly.
7. Create a Pull Request when your module is ready.
8. Another teammate should review before merging.
9. Do not modify another member's module without informing them.
10. Coordinate before changing shared files.
11. Never commit API keys, passwords, .env files, datasets that cannot be redistributed, or large model files.
12. Test your code before opening a Pull Request.


## Commit Message Examples  

feat: add incident classifier
feat: add credibility scoring
feat: implement report clustering
feat: add priority engine
feat: add emergency dashboard
fix: handle missing locations
fix: handle empty reports
docs: update dataset documentation


## Pull Request Process  

1. Push feature branch.
2. Open Pull Request into main.
3. Explain what was changed.
4. Mention any dependencies.
5. Teammate reviews.
6. Fix requested changes.
7. Merge only after review.
8. Delete branch after successful merge if no longer needed.

## Important  

The final data interface is defined in:

DATA_SCHEMA.md

Do not independently change the schema.

---

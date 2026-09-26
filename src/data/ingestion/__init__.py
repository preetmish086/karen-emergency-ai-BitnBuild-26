"""
Data Ingestion package for CrisisLex, HumAID, and sample datasets.
"""
from src.data.ingestion.crisislex import load_crisislex
from src.data.ingestion.humaid import load_humaid
from src.data.ingestion.sample import load_sample

__all__ = ["load_crisislex", "load_humaid", "load_sample"]

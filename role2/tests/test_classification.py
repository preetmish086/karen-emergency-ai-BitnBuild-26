import pytest
from src.classification.incident_classifier import IncidentClassifier
from src.schemas.output_schema import IncidentCategory


@pytest.fixture
def classifier():
    return IncidentClassifier()


def test_fire_classification(classifier):
    res = classifier.classify("I saw a fire break out in my building")
    assert res.type == IncidentCategory.FIRE
    assert res.confidence >= 0.70


def test_accident_classification(classifier):
    res = classifier.classify("I saw a car accident on the highway near main st")
    assert res.type == IncidentCategory.ACCIDENT
    assert res.confidence >= 0.70


def test_flood_classification(classifier):
    res = classifier.classify("Water is entering houses after the river overflowed")
    assert res.type == IncidentCategory.FLOOD
    assert res.confidence >= 0.70


def test_explosion_classification(classifier):
    res = classifier.classify("There was a huge explosion near the central market")
    assert res.type == IncidentCategory.EXPLOSION
    assert res.confidence >= 0.70


def test_medical_classification(classifier):
    res = classifier.classify("My friend is unconscious and needs an immediate ambulance")
    assert res.type == IncidentCategory.MEDICAL
    assert res.confidence >= 0.70


def test_collapse_classification(classifier):
    res = classifier.classify("The building collapsed and people are trapped under rubble")
    assert res.type == IncidentCategory.COLLAPSE
    assert res.confidence >= 0.70


def test_missing_person_classification(classifier):
    res = classifier.classify("My child has been missing since this morning")
    assert res.type == IncidentCategory.MISSING_PERSON
    assert res.confidence >= 0.70

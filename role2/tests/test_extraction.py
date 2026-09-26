import pytest
from src.extraction.entity_extractor import EntityExtractor


@pytest.fixture
def extractor():
    return EntityExtractor()


def test_explicit_casualty_extraction(extractor):
    people = extractor.extract_people("I saw a car accident and 4 people were injured near Times Square.")
    assert people.total_affected == 4
    assert people.injured == 4
    assert people.dead is None
    assert people.missing is None


def test_missing_casualty_information(extractor):
    people = extractor.extract_people("I saw a fire break out in my building.")
    assert people.total_affected is None
    assert people.injured is None
    assert people.dead is None
    assert people.missing is None
    assert people.trapped is None
    assert people.rescued is None
    assert people.evacuated is None


def test_multiple_casualty_categories(extractor):
    people = extractor.extract_people("One person died and two others were injured in a collision.")
    assert people.dead == 1
    assert people.injured == 2
    assert people.total_affected == 3


def test_no_hallucinated_people_counts(extractor):
    """
    CRITICAL RULE TEST:
    Verifies that absence of a reported number does NOT invent/hallucinate default numbers.
    The test MUST fail if the system invents a casualty count.
    """
    text_without_counts = "I saw a fire break out in my building."
    people = extractor.extract_people(text_without_counts)

    # Must be strictly None, not 0, not 5, not 10
    assert people.total_affected is None, "System hallucinated total_affected count!"
    assert people.injured is None, "System hallucinated injured count!"
    assert people.dead is None, "System hallucinated dead count!"
    assert people.missing is None, "System hallucinated missing count!"
    assert people.trapped is None, "System hallucinated trapped count!"

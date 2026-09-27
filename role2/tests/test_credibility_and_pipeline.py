import pytest
from src.pipeline.process_report import EmergencyReportPipeline
from src.schemas.input_schema import EmergencyReportInput
from src.schemas.output_schema import Role2OutputSchema


@pytest.fixture
def pipeline():
    return EmergencyReportPipeline()


def test_gps_preservation(pipeline):
    report = EmergencyReportInput(
        report_id="TEST001",
        text="I saw a fire break out in my building.",
        latitude=40.7580,
        longitude=-73.9855,
        timestamp="2026-09-27T12:00:00Z"
    )
    output = pipeline.process(report)
    assert output.location.latitude == 40.7580
    assert output.location.longitude == -73.9855
    assert output.report_id == "TEST001"


def test_output_schema_validation(pipeline):
    raw_input = {
        "report_id": "TEST002",
        "text": "I saw a car accident and 4 people were injured near Times Square.",
        "latitude": 40.7580,
        "longitude": -73.9855,
        "timestamp": "2026-09-27T12:30:00Z"
    }
    output = pipeline.process(raw_input)
    assert isinstance(output, Role2OutputSchema) or output.__class__.__name__ == "Role2OutputSchema"
    # Validate JSON serializability
    output_dict = output.model_dump()
    assert output_dict["report_id"] == "TEST002"
    assert output_dict["incident"]["type"] == "accident"
    assert output_dict["people"]["total_affected"] == 4


def test_credibility_score_range(pipeline):
    reports = [
        "I saw a car accident and 4 people were injured near Times Square.",
        "I saw a fire break out in my building.",
        "asdfghjkl zxcvbnm",
        "Something weird happened."
    ]
    for text in reports:
        report = EmergencyReportInput(
            report_id="CRED_TEST",
            text=text,
            latitude=12.34,
            longitude=56.78,
            timestamp="2026-09-27T12:00:00Z"
        )
        output = pipeline.process(report)
        score = output.credibility.score
        assert 0.0 <= score <= 1.0, f"Credibility score {score} out of bounds for text: {text}"
        assert isinstance(output.credibility.factors, dict)
        for factor_name, factor_val in output.credibility.factors.items():
            assert 0.0 <= factor_val <= 1.0, f"Factor {factor_name} value {factor_val} out of bounds"

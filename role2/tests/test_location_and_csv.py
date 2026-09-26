import pytest
from src.pipeline.process_report import EmergencyReportPipeline
from src.schemas.input_schema import EmergencyReportInput


@pytest.fixture
def pipeline():
    return EmergencyReportPipeline()


def test_optional_gps_without_coordinates(pipeline):
    """
    Verifies that report processing works cleanly when GPS coordinates are absent/None.
    """
    report = EmergencyReportInput(
        report_id="NOGPS001",
        text="I saw a fire break out in my building near 5th Avenue.",
        latitude=None,
        longitude=None,
        location="5th Avenue, New York",
        timestamp="2026-09-27T12:00:00Z"
    )
    output = pipeline.process(report)

    assert output.location.latitude is None
    assert output.location.longitude is None
    assert output.location.has_gps is False
    assert output.location.text_location == "5th Avenue, New York"
    assert output.information.has_location_information is True


def test_textual_location_extraction_from_text(pipeline):
    """
    Verifies that textual location is extracted directly from human text when no manual metadata is provided.
    """
    report = EmergencyReportInput(
        report_id="TEXTLOC001",
        text="There is a vehicle overturned near Times Square, please send help",
        latitude=None,
        longitude=None
    )
    output = pipeline.process(report)

    assert output.location.has_gps is False
    assert output.location.text_location is not None
    assert "Times Square" in output.location.text_location
    assert output.information.has_location_information is True


def test_location_density_credibility_boost(pipeline):
    """
    USER FEATURE TEST:
    Verifies that credibility increases when multiple reports arrive from the same location within the same time window.
    """
    single_report = EmergencyReportInput(
        report_id="DENSITY_SINGLE",
        text="I saw a fire break out in a house",
        location="Unique Remote Place XYZ 999",
        location_report_count=1
    )
    multi_report = EmergencyReportInput(
        report_id="DENSITY_MULTI",
        text="I saw a fire break out in a house",
        location="Unique Remote Place XYZ 999",
        location_report_count=5
    )

    out_single = pipeline.process(single_report)
    out_multi = pipeline.process(multi_report)

    assert out_single.location.location_report_count == 1
    assert out_multi.location.location_report_count == 5
    assert out_multi.credibility.factors["location_density"] > out_single.credibility.factors["location_density"]
    assert out_multi.credibility.score >= out_single.credibility.score


def test_casualty_reporting_credibility_signal(pipeline):
    """
    USER FEATURE TEST:
    Verifies that explicitly mentioning the number of people affected increases the casualty reporting credibility factor.
    """
    without_casualty = EmergencyReportInput(
        report_id="CASUALTY_NO",
        text="I saw a car accident on the highway near main street",
    )
    with_casualty = EmergencyReportInput(
        report_id="CASUALTY_YES",
        text="I saw a car accident and 4 people were injured near main street",
    )

    out_no = pipeline.process(without_casualty)
    out_yes = pipeline.process(with_casualty)

    assert out_no.people.total_affected is None
    assert out_yes.people.total_affected == 4
    assert out_yes.credibility.factors["casualty_reporting_signal"] == 1.00
    assert out_no.credibility.factors["casualty_reporting_signal"] == 0.50


def test_spatio_temporal_window_separation(pipeline):
    """
    CRITICAL USER BOTTLENECK FIX TEST:
    Verifies that morning and evening reports at the same location are NOT conflated.
    Same location + Same time window (9:00 AM & 9:10 AM) -> Count increments to 2.
    Same location + Different time window (9:00 PM - 12 hours later) -> Count resets to 1.
    """
    pipeline_fresh = EmergencyReportPipeline(window_minutes=30)

    morning_1 = EmergencyReportInput(
        report_id="MORN_1",
        text="Fire broke out near Times Square",
        location="Times Square, New York",
        timestamp="2026-09-27T09:00:00Z"
    )
    morning_2 = EmergencyReportInput(
        report_id="MORN_2",
        text="Smoke seen near Times Square",
        location="Times Square, New York",
        timestamp="2026-09-27T09:10:00Z"
    )
    evening_1 = EmergencyReportInput(
        report_id="EVE_1",
        text="Car crash near Times Square",
        location="Times Square, New York",
        timestamp="2026-09-27T21:00:00Z"
    )

    out_m1 = pipeline_fresh.process(morning_1)
    out_m2 = pipeline_fresh.process(morning_2)
    out_e1 = pipeline_fresh.process(evening_1)

    assert out_m1.location.location_report_count == 1
    assert out_m2.location.location_report_count == 2
    assert out_e1.location.location_report_count == 1, "Evening report wrongly conflated with morning report!"

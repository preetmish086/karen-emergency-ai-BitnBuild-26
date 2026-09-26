# Downstream Integration Contract: Role 2 to Role 3 (Spatial-Temporal Clustering)

## Purpose

Role 2 processes individual emergency reports in isolation and outputs structured JSON. Role 3 receives these processed JSON objects to perform spatial-temporal clustering and report grouping.

Role 2 does **not** perform clustering or priority ranking, but guarantees that all required fields for spatial-temporal grouping are cleanly exposed and validated.

---

## Role 2 Output Payload Schema for Role 3

```json
{
  "report_id": "R001",
  "text": "I saw a car accident and 4 people were injured near Times Square.",
  "incident": {
    "type": "accident",
    "confidence": 0.93
  },
  "people": {
    "total_affected": 4,
    "injured": 4,
    "dead": null,
    "missing": null,
    "trapped": null,
    "rescued": null,
    "evacuated": null
  },
  "information": {
    "has_casualty_information": true,
    "has_affected_count": true,
    "has_injury_information": true,
    "completeness_score": 0.90
  },
  "credibility": {
    "score": 0.94,
    "factors": {
      "first_person_observation": 0.95,
      "specificity": 1.00,
      "coherence": 1.00,
      "actionability": 0.90,
      "temporal_presence": 0.65,
      "internal_consistency": 1.00,
      "information_completeness": 0.90
    }
  },
  "location": {
    "latitude": 40.7580,
    "longitude": -73.9855
  },
  "timestamp": "2026-09-27T12:30:00Z"
}
```

---

## Field Usage Mapping for Role 3

| Field | Type | Role 3 Usage |
| :--- | :--- | :--- |
| `report_id` | `string` | Unique identifier for cluster member tracking |
| `location.latitude` | `float` | Spatial clustering (DBSCAN / Haversine distance) |
| `location.longitude` | `float` | Spatial clustering (DBSCAN / Haversine distance) |
| `timestamp` | `string (ISO)` | Temporal sliding window grouping |
| `incident.type` | `string` | Category-level filtering & cluster homogeneity validation |
| `credibility.score` | `float` | Cluster confidence weighting & spam report filtering |
| `people.total_affected` | `int / null` | Aggregate casualty estimation per cluster |

---

## Recommended Integration Pattern

```python
# Example snippet of how Role 3 can consume Role 2 output
from role2.src.pipeline.process_report import EmergencyReportPipeline

pipeline = EmergencyReportPipeline()

# Ingest single report from Role 1 pipeline or API queue
role2_output = pipeline.process(incoming_report_data)

# Pass structured Pydantic / dict output directly to Role 3 Spatial-Temporal Clustering Engine
role3_cluster_engine.add_report(
    report_id=role2_output.report_id,
    lat=role2_output.location.latitude,
    lon=role2_output.location.longitude,
    timestamp=role2_output.timestamp,
    incident_type=role2_output.incident.type.value,
    credibility=role2_output.credibility.score,
    affected_count=role2_output.people.total_affected
)
```

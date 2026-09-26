# Karen's Ear — Data Schema  

This document defines the common interface between all team modules.  

## Final Report Schema  

Each processed emergency report should follow this structure:  

```json
{
  "report_id": "R001",
  "text": "Explosion near Times Square, multiple people injured",
  "incident_type": "explosion",
  "location": "Times Square",
  "severity": "critical",
  "actionability": "high",
  "credibility": 0.86,
  "priority": 0.93
}
```  

## Fields  

| Field         | Type        | Description                         |
| ------------- | ----------- | ----------------------------------- |
| report_id     | string      | Unique report identifier            |
| text          | string      | Original emergency report           |
| incident_type | string      | Type of incident                    |
| location      | string/null | Extracted location                  |
| severity      | string      | Estimated severity                  |
| actionability | string      | Urgency/actionability of the report |
| credibility   | float       | Credibility confidence from 0 to 1  |
| priority      | float       | Final priority score from 0 to 1    |  


### Allowed Incident Types  
fire
explosion
accident
medical
collapse
flood
crime
missing_person
unknown
other

### Allowed Severity  
low
medium
high
critical

### Allowed Actionability  
low
medium
high

## Numeric Scores  

credibility and priority must be between 0 and 1.

The frontend may display these as percentages.

## Missing Information  

If the model cannot confidently determine a value:

location → null
incident_type → unknown
other categorical fields → use the appropriate fallback value

Models must not hallucinate missing information.

# Important  

Do not change field names or allowed values without discussing it with the entire team.
"""
Controlled Synthetic Data Augmentation Module.
Adds synthetic training examples for underrepresented emergency incident classes.
Guarantees synthetic data isolation from held-out real validation and test sets.
"""
import random
from typing import List, Dict, Any, Tuple

# Pre-defined high-quality, realistic emergency templates for underrepresented canonical classes
SYNTHETIC_TEMPLATES: Dict[str, List[str]] = {
    "medical": [
        "Urgent medical assistance requested at {location}. Multiple victims suffering from severe {symptom}.",
        "Ambulance needed immediately near {location}. Person collapsed and is unresponsive.",
        "Paramedics dispatched to {location} following a severe injury incident.",
        "Casualties reported at {location}. Medical team required on scene immediately.",
        "Emergency medical services attending to injured people near {location}.",
        "Victim bleeding heavily near {location}, requesting immediate triage and transport.",
        "Cardiac emergency reported at {location}. CPR currently being administered.",
        "Medical crew arriving at {location} to treat injured victims."
    ],
    "missing_person": [
        "Missing person report: {name} last seen near {location} wearing {clothing}. Please call emergency services if spotted.",
        "Search party formed near {location} looking for missing individual {name}.",
        "Have you seen {name}? Missing since yesterday afternoon near {location}.",
        "Police requesting public assistance to locate missing person last seen around {location}.",
        "Unaccounted individual reported missing near {location} following recent incident.",
        "Family searching for missing person {name}, last traced to {location}.",
        "Urgent search underway for missing person near {location}."
    ],
    "crime": [
        "Active shooting incident reported near {location}. Stay away from the area.",
        "Police responding to an armed robbery at {location}. Suspect fled on foot.",
        "Gunfire heard near {location}. Multiple emergency police units responding.",
        "Hostage situation developing near {location}. SWAT team deployed to scene.",
        "Assault reported near {location}. Police and emergency medical units on site.",
        "Armed suspect reported near {location}. Authorities advising local lockdown."
    ],
    "collapse": [
        "Building collapse reported at {location}. Emergency crews searching for trapped residents.",
        "Structural failure near {location}. Wall collapsed into street blocking emergency access.",
        "Bridge section collapsed near {location}. Search and rescue teams deployed.",
        "Multi-story structure collapsed near {location} following heavy tremors. People trapped inside.",
        "Roof collapse reported at commercial building near {location}. Firefighters responding."
    ],
    "explosion": [
        "Loud explosion reported near {location}. Thick black smoke rising over the skyline.",
        "Refinery explosion occurred near {location}. Industrial blast felt miles away.",
        "Suspected gas line explosion near {location}. Fire and emergency crews on site.",
        "Blast reported at facility near {location}. Emergency evacuation ordered."
    ],
    "accident": [
        "Multi-car pileup collision on highway near {location}. Traffic completely blocked.",
        "Train derailment reported near {location}. Emergency responders assisting passengers.",
        "Severe vehicle crash near {location}. Road closed in both directions.",
        "Helicopter forced landing and crash near {location}. Emergency crews responding."
    ],
    "fire": [
        "Wildfire spreading rapidly near {location}. Evacuation warning issued for nearby residents.",
        "Commercial building fire near {location}. Multiple fire trucks battling the blaze.",
        "Structure fire reported at residential property near {location}.",
        "Heavy smoke and flames visible near {location}. Firefighters on scene."
    ],
    "flood": [
        "Flash flooding inundating streets near {location}. Water levels rising rapidly.",
        "River overflow causing widespread flooding near {location}. Evacuations underway.",
        "Residential area flooded near {location}. Boats rescuing stranded residents."
    ]
}

LOCATIONS = [
    "Downtown Central", "Station Road", "Highway 101", "West District",
    "Riverside Park", "Market Square", "Industrial Zone", "North Avenue",
    "Metro Terminal", "East Bridge", "Airport Sector"
]

NAMES = ["John", "Sarah", "David", "Emily", "Michael", "Jessica", "Robert"]
CLOTHING = ["a blue jacket and jeans", "a red hoodie", "dark clothing", "a black coat"]
SYMPTOMS = ["burns and fractures", "respiratory distress", "head trauma", "lacerations"]

class SyntheticAugmenter:
    """
    Controlled synthetic dataset generator.
    Augments underrepresented canonical classes for the training split ONLY.
    """

    @classmethod
    def generate_synthetic_samples(
        cls,
        target_counts: Dict[str, int],
        seed: int = 42
    ) -> List[Dict[str, Any]]:
        """
        Generates synthetic records targeting requested counts per canonical incident_type.
        Returns list of synthetic record dicts.
        """
        random.seed(seed)
        synthetic_records: List[Dict[str, Any]] = []
        syn_counter = 1

        for inc_type, target_num in target_counts.items():
            if target_num <= 0:
                continue
            templates = SYNTHETIC_TEMPLATES.get(inc_type, SYNTHETIC_TEMPLATES["medical"])

            for _ in range(target_num):
                template = random.choice(templates)
                loc = random.choice(LOCATIONS)
                name = random.choice(NAMES)
                cloth = random.choice(CLOTHING)
                symp = random.choice(SYMPTOMS)

                text = template.format(
                    location=loc,
                    name=name,
                    clothing=cloth,
                    symptom=symp
                )

                syn_id = f"SYN_{inc_type.upper()}_{syn_counter:04d}"
                syn_counter += 1

                record = {
                    "report_id": syn_id,
                    "text": text,
                    "incident_type": inc_type,
                    "source": "synthetic",
                    "source_event": "synthetic_augmentation",
                    "source_label": f"synthetic_{inc_type}",
                    "is_synthetic": True
                }
                synthetic_records.append(record)

        return synthetic_records

    @classmethod
    def augment_training_set(
        cls,
        real_train_records: List[Dict[str, Any]],
        augmentation_ratio: float = 0.15,
        seed: int = 42
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Calculates class imbalances in real_train_records and generates targeted synthetic examples.
        Appends synthetic records ONLY to training data.
        Returns (augmented_train_records, summary_stats).
        """
        from collections import Counter
        class_counts = Counter([r.get("incident_type", "other") for r in real_train_records])
        total_real = len(real_train_records)

        target_total_synthetic = int(total_real * augmentation_ratio)
        if target_total_synthetic <= 0 or not class_counts:
            return real_train_records, {"synthetic_added": 0}

        max_count = max(class_counts.values())
        needed_counts: Dict[str, int] = {}

        # Prioritize classes below median count
        for inc_type in ["medical", "missing_person", "crime", "collapse", "explosion", "accident", "fire", "flood"]:
            curr = class_counts.get(inc_type, 0)
            diff = max(0, (max_count // 2) - curr)
            if diff > 0:
                needed_counts[inc_type] = diff

        # Scale to match target_total_synthetic
        total_needed = sum(needed_counts.values())
        if total_needed > 0:
            scale = target_total_synthetic / total_needed
            final_target_counts = {k: max(1, int(v * scale)) for k, v in needed_counts.items()}
        else:
            final_target_counts = {k: int(target_total_synthetic / 8) for k in ["medical", "missing_person", "crime", "collapse"]}

        synthetic_records = cls.generate_synthetic_samples(final_target_counts, seed=seed)
        augmented_train = list(real_train_records) + synthetic_records

        stats = {
            "real_train_count": total_real,
            "synthetic_added_count": len(synthetic_records),
            "final_train_count": len(augmented_train),
            "synthetic_ratio": len(synthetic_records) / len(augmented_train) if augmented_train else 0.0,
            "synthetic_per_class": dict(Counter([r["incident_type"] for r in synthetic_records]))
        }

        return augmented_train, stats

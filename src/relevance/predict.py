from src.relevance.relevance_model import RelevanceModel


MODEL_PATH = "models/relevance_model.pkl"


def main():

    model = RelevanceModel()

    model.load(
        MODEL_PATH
    )

    reports = [

        # Strong emergency
        "building on fire near Times Square people trapped",

        # Different wording for explosion
        "wtf something blew up near the station",

        # Different wording for flood
        "water is coming into the subway and rising fast",

        # Uncertain report
        "heard a huge boom near 42nd, not sure what happened",

        # Possible medical emergency
        "someone dropped to the ground outside Penn Station",

        # Normal / irrelevant
        "traffic is terrible near Central Park today",

        # Hard negative
        "movie crew is filming an explosion scene near Times Square",

        # Hard negative
        "fire safety drill scheduled at JFK tomorrow",

        # Ambiguous
        "sirens everywhere near Wall Street, no idea what's going on",

        # Normal
        "beautiful weather in Manhattan today"
    ]

    print(
        "\n===== RELEVANCE ANALYSIS =====\n"
    )

    for text in reports:

        result = model.predict_one(
            text
        )

        print(
            f"Report: {text}"
        )

        print(
            f"Relevance Level: "
            f"{result['relevance_level'].upper()}"
        )

        print(
            f"ML Level: "
            f"{result['ml_level']}"
        )

        print(
            f"ML Confidence: "
            f"{result['ml_confidence']}"
        )

        print(
            f"Relevance Score: "
            f"{result['relevance_score']}"
        )

        print(
            f"Emergency Signal: "
            f"{result['emergency_signal']}"
        )

        print()


if __name__ == "__main__":
    main()
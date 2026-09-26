import re
from typing import Dict


class TextPreprocessor:
    """
    Handles natural language text cleaning, normalization, and tokenization.
    Modular design allows replacing with spaCy/HuggingFace preprocessors.
    """

    WORD_TO_NUM: Dict[str, int] = {
        "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4,
        "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
        "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
        "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17,
        "eighteen": 18, "nineteen": 19, "twenty": 20, "thirty": 30,
        "forty": 40, "fifty": 50, "several": 3, "couple": 2, "few": 3
    }

    CONTRACTIONS: Dict[str, str] = {
        "can't": "cannot",
        "won't": "will not",
        "n't": " not",
        "'s": " is",
        "'re": " are",
        "'ve": " have",
        "'m": " am",
        "'ll": " will"
    }

    def preprocess(self, text: str) -> str:
        """
        Normalizes input text for classification and entity extraction.
        """
        if not text:
            return ""

        # Normalize whitespace
        cleaned = re.sub(r"\s+", " ", text.strip())

        # Expand contractions gently
        for contraction, replacement in self.CONTRACTIONS.items():
            cleaned = re.sub(re.escape(contraction), replacement, cleaned, flags=re.IGNORECASE)

        return cleaned

    def normalize_number_words(self, text: str) -> str:
        """
        Replaces text numbers ('four people') with digit numbers ('4 people') for easier extraction.
        """
        tokens = text.split()
        normalized_tokens = []
        for token in tokens:
            lower_token = token.lower().strip(",.!?")
            if lower_token in self.WORD_TO_NUM:
                # Replace with numeric string while retaining punctuation
                num_str = str(self.WORD_TO_NUM[lower_token])
                punctuation = token[len(lower_token):] if len(token) > len(lower_token) else ""
                normalized_tokens.append(num_str + punctuation)
            else:
                normalized_tokens.append(token)
        return " ".join(normalized_tokens)

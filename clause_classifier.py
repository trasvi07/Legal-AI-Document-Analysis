"""
clause_classifier.py
---------------------
Identifies and classifies key clause types in a legal document:
payment, confidentiality, liability, termination.

Approach: hybrid keyword + sentence-level classification.
Why not a pure ML classifier? Training a real clause-classification model
needs a labeled legal dataset (thousands of annotated clauses), which we
don't have. A hybrid rule + keyword approach is the honest, practical
choice for a student project — and it's still a legitimate NLP technique
used in real legal-tech tools before/alongside ML classifiers.

spaCy is used here for sentence segmentation (splitting a chunk of text
into individual sentences), which is more reliable than naive splitting
on periods (legal text has abbreviations like "Rs." that break naive
splitting).
"""

import spacy

# Keyword signatures for each clause type.
# Real legal clause classifiers use much larger keyword banks + trained
# classifiers; this is a starting set covering common contract language.
CLAUSE_KEYWORDS = {
    "payment": [
        "payment", "pay", "rent", "fee", "invoice", "salary", "compensation",
        "amount due", "penalty", "late fee", "installment",
    ],
    "confidentiality": [
        "confidential", "non-disclosure", "nda", "proprietary",
        "trade secret", "disclose", "third party",
    ],
    "liability": [
        "liable", "liability", "damages", "indemnify", "indemnification",
        "responsible for", "not be held liable", "limitation of liability",
    ],
    "termination": [
        "terminate", "termination", "notice period", "cancel", "cancellation",
        "expiration", "breach", "forfeit",
    ],
}


class ClauseClassifier:
    def __init__(self):
        # Load spaCy's small English model for sentence segmentation.
        # Run: python -m spacy download en_core_web_sm  (one-time setup)
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            raise RuntimeError(
                "spaCy model 'en_core_web_sm' not found.\n"
                "Run this once: python -m spacy download en_core_web_sm"
            )

    def _classify_sentence(self, sentence: str) -> list[str]:
        """Return which clause types a single sentence matches (can be more than one)."""
        sentence_lower = sentence.lower()
        matched_types = []

        for clause_type, keywords in CLAUSE_KEYWORDS.items():
            if any(keyword in sentence_lower for keyword in keywords):
                matched_types.append(clause_type)

        return matched_types

    def classify_document(self, full_text: str) -> dict:
        """
        Classify every sentence in the document, grouped by clause type.

        Returns:
            {
                "payment": ["sentence 1...", "sentence 2..."],
                "confidentiality": [...],
                "liability": [...],
                "termination": [...],
                "unclassified": [...]   # sentences that matched no clause type
            }
        """
        doc = self.nlp(full_text)
        results = {clause_type: [] for clause_type in CLAUSE_KEYWORDS}
        results["unclassified"] = []

        for sent in doc.sents:
            sentence_text = sent.text.strip()
            if len(sentence_text) < 10:  # skip near-empty/junk fragments
                continue

            matched = self._classify_sentence(sentence_text)
            if matched:
                for clause_type in matched:
                    results[clause_type].append(sentence_text)
            else:
                results["unclassified"].append(sentence_text)

        return results


if __name__ == "__main__":
    import sys
    sys.path.append(".")
    from pdf_extractor import extract_full_text

    if len(sys.argv) < 2:
        print("Usage: python clause_classifier.py <path_to_pdf>")
        sys.exit(1)

    text = extract_full_text(sys.argv[1])
    classifier = ClauseClassifier()
    results = classifier.classify_document(text)

    for clause_type, sentences in results.items():
        if clause_type == "unclassified":
            continue
        print(f"\n=== {clause_type.upper()} ({len(sentences)} sentence(s)) ===")
        for s in sentences:
            print(f"  - {s}")

"""
risk_detector.py
-----------------
Flags potentially risky or unfair clauses using pattern matching, and
provides a plain-language explanation of why each flagged clause matters.

Why rule-based and not ML here?
"Risky clause detection" is subjective and context-dependent — what's
risky in a rental agreement differs from what's risky in an NDA. A
transparent, explainable rule-based approach is actually preferable for
a legal-adjacent tool: users (and interviewers) can see exactly WHY
something was flagged, rather than trusting an opaque model's guess.
This is also what real legal-tech tools (e.g., contract review software)
do for a first-pass "red flag" scan before human review.
"""

RISK_PATTERNS = [
    {
        "keywords": ["sole discretion", "at its discretion"],
        "risk": "One party has unilateral decision-making power with no clear limits.",
        "suggestion": "Ask for specific criteria or conditions instead of open-ended discretion.",
    },
    {
        "keywords": ["shall not be held liable", "no liability", "waives all liability"],
        "risk": "This clause removes one party's responsibility for damages or harm, even in cases that might otherwise be their fault.",
        "suggestion": "Check if the liability waiver has reasonable exceptions (e.g., gross negligence).",
    },
    {
        "keywords": ["automatically renew", "auto-renewal", "automatic renewal"],
        "risk": "The contract may renew without your active consent unless you cancel in time.",
        "suggestion": "Note the cancellation deadline and set a reminder before it passes.",
    },
    {
        "keywords": ["forfeit", "non-refundable"],
        "risk": "You may lose money already paid, with no way to get it back under certain conditions.",
        "suggestion": "Check exactly which conditions trigger forfeiture before agreeing.",
    },
    {
        "keywords": ["irrevocable", "cannot be terminated", "no right to terminate"],
        "risk": "You may be locked into this agreement with limited or no ability to exit.",
        "suggestion": "Look for any exit clauses or negotiate one before signing.",
    },
    {
        "keywords": ["penalty", "late fee"],
        "risk": "Financial penalties apply for missed deadlines — confirm the exact amount and grace period.",
        "suggestion": "Check whether the penalty amount is proportional and capped.",
    },
    {
        "keywords": ["indemnify", "indemnification", "hold harmless"],
        "risk": "You may be responsible for covering the other party's legal costs or losses in a dispute.",
        "suggestion": "Understand the scope — is it limited to your own wrongdoing, or open-ended?",
    },
]


def detect_risks(full_text: str) -> list[dict]:
    """
    Scan document text for risky clause patterns.

    Returns a list of:
        {
            "matched_phrase": "...",
            "risk": "plain language explanation",
            "suggestion": "what to check or ask about"
        }
    """
    text_lower = full_text.lower()
    findings = []

    for pattern in RISK_PATTERNS:
        for keyword in pattern["keywords"]:
            if keyword in text_lower:
                findings.append({
                    "matched_phrase": keyword,
                    "risk": pattern["risk"],
                    "suggestion": pattern["suggestion"],
                })
                break  # one match per pattern is enough, avoid duplicate spam

    return findings


if __name__ == "__main__":
    import sys
    sys.path.append(".")
    from pdf_extractor import extract_full_text

    if len(sys.argv) < 2:
        print("Usage: python risk_detector.py <path_to_pdf>")
        sys.exit(1)

    text = extract_full_text(sys.argv[1])
    findings = detect_risks(text)

    if not findings:
        print("No risky patterns detected in this document.")
    else:
        print(f"Found {len(findings)} potential risk(s):\n")
        for f in findings:
            print(f"Matched phrase: '{f['matched_phrase']}'")
            print(f"  Risk: {f['risk']}")
            print(f"  Suggestion: {f['suggestion']}\n")

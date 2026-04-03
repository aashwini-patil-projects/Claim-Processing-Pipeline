from typing import Dict, List

def segregate_claims(text: str) -> List[Dict[str, str]]:
    """
    Simple text segregation function (not currently used in main workflow).
    Kept for reference or future use.
    """
    sections = text.split("\n\n")
    claims = []
    for section in sections:
        if section.strip():
            claims.append({"content": section.strip()})
    return claims

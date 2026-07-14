def calculate_nps(responses: list) -> float:
    """NPS = % Promoters minus % Detractors. Scores are on a 1-5 scale."""
    total = len(responses)
    if total == 0:
        return 0.0
    promoters = sum(1 for r in responses if r["score"] >= 4.5)
    detractors = sum(1 for r in responses if r["score"] <= 3.0)
    return round(((promoters - detractors) / total) * 100, 1)

def categorize_nps(score: float) -> str:
    if score >= 4.5:
        return "Promoter"
    elif score >= 3.5:
        return "Passive"
    return "Detractor"

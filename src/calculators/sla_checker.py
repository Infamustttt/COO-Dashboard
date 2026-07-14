def check_sla_compliance(sla: dict) -> str:
    actual = sla["actual_value"]
    target = sla["target_value"]
    sla_type = sla["sla_type"]

    # higher is better: uptime, scores, delivery %
    if sla_type in ["Uptime", "CSAT", "Delivery"]:
        if actual >= target:
            return "Met"
        elif actual >= target * 0.95:
            return "At Risk"
        return "Breached"

    # lower is better: response/resolution times
    if sla_type in ["Response Time", "Resolution Time"]:
        if actual <= target:
            return "Met"
        elif actual <= target * 1.10:
            return "At Risk"
        return "Breached"

    return "Unknown"

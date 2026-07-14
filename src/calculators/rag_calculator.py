from datetime import date

def calculate_rag(project: dict) -> tuple[str, str]:
    budget_pct = project["budget_consumed_pct"]
    overdue = project["overdue_tasks"]
    end_date = project["expected_end_date"]
    if hasattr(end_date, "date"):
        end_date = end_date.date()
    days_to_end = (end_date - date.today()).days
    completion = project["completion_pct"]

    if budget_pct >= 95:
        return "RED", f"Budget at {budget_pct:.0f}%, immediate review needed"
    if overdue >= 5:
        return "RED", f"{overdue} overdue tasks, delivery at risk"
    if days_to_end <= 0 and completion < 95:
        return "RED", "Milestone missed, project overdue"

    if budget_pct >= 80:
        return "AMBER", f"Budget at {budget_pct:.0f}%, monitor closely"
    if overdue >= 2:
        return "AMBER", f"{overdue} overdue tasks, attention needed"
    if days_to_end <= 7 and completion < 80:
        return "AMBER", "Milestone due within 7 days, completion low"

    return "GREEN", "On track"

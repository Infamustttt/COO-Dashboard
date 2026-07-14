from datetime import date

def calculate_utilization_status(allocation_pct: float) -> str:
    if allocation_pct > 100:
        return "Over-allocated"
    elif allocation_pct >= 75:
        return "Optimal"
    elif allocation_pct >= 40:
        return "Under-utilized"
    return "Bench"

def calculate_bench_days(bench_since: date) -> int:
    if bench_since is None:
        return 0
    return (date.today() - bench_since).days

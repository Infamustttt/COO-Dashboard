import pytest
from datetime import date, timedelta
from src.calculators.rag_calculator import calculate_rag

def base_project(**overrides):
    p = {
        "budget_consumed_pct": 50,
        "overdue_tasks": 0,
        "expected_end_date": date.today() + timedelta(days=30),
        "completion_pct": 60,
    }
    p.update(overrides)
    return p

def test_green():
    assert calculate_rag(base_project())[0] == "GREEN"

def test_red_budget():
    assert calculate_rag(base_project(budget_consumed_pct=96))[0] == "RED"

def test_red_overdue():
    assert calculate_rag(base_project(overdue_tasks=5))[0] == "RED"

def test_red_missed_milestone():
    assert calculate_rag(base_project(expected_end_date=date.today() - timedelta(days=1), completion_pct=80))[0] == "RED"

def test_amber_budget():
    assert calculate_rag(base_project(budget_consumed_pct=82))[0] == "AMBER"

def test_amber_overdue():
    assert calculate_rag(base_project(overdue_tasks=3))[0] == "AMBER"

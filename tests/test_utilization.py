import pytest
from src.calculators.utilization import calculate_utilization_status

def test_over_allocated():
    assert calculate_utilization_status(110) == "Over-allocated"

def test_optimal():
    assert calculate_utilization_status(80) == "Optimal"

def test_under_utilized():
    assert calculate_utilization_status(60) == "Under-utilized"

def test_bench():
    assert calculate_utilization_status(30) == "Bench"

def test_boundary_optimal():
    assert calculate_utilization_status(75) == "Optimal"

def test_boundary_bench():
    assert calculate_utilization_status(39) == "Bench"

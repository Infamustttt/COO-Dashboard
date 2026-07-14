import pytest
from src.calculators.sla_checker import check_sla_compliance

def test_uptime_met():
    assert check_sla_compliance({"sla_type": "Uptime", "actual_value": 99.9, "target_value": 99.5}) == "Met"

def test_uptime_breached():
    assert check_sla_compliance({"sla_type": "Uptime", "actual_value": 90.0, "target_value": 99.5}) == "Breached"

def test_uptime_at_risk():
    assert check_sla_compliance({"sla_type": "Uptime", "actual_value": 94.6, "target_value": 99.5}) == "At Risk"

def test_response_time_met():
    assert check_sla_compliance({"sla_type": "Response Time", "actual_value": 3, "target_value": 4}) == "Met"

def test_response_time_breached():
    assert check_sla_compliance({"sla_type": "Response Time", "actual_value": 10, "target_value": 4}) == "Breached"

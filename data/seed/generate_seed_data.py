"""
Run this once to generate realistic fake data CSVs.
Usage: python data/seed/generate_seed_data.py
"""
import pandas as pd
import random
from faker import Faker
from datetime import date, timedelta
import os

fake = Faker()
random.seed(42)
Faker.seed(42)

OUT = os.path.dirname(__file__)

CLIENTS = [f"Client {chr(65+i)}" for i in range(10)]
SKILLS = ["Python", "Java", "React", "DevOps", "QA", "Data Engineering", "Cloud", "Scrum Master", "BA", "UI/UX"]
DEPARTMENTS = ["Engineering", "QA", "DevOps", "Data", "Design", "PMO"]
PHASES = ["Discovery", "Development", "UAT", "Go-Live"]
TASK_TYPES = ["Development", "Testing", "Meetings", "Admin"]
SLA_TYPES = ["Uptime", "Response Time", "Resolution Time", "Delivery"]

def rand_date(start_offset=-180, end_offset=180):
    return date.today() + timedelta(days=random.randint(start_offset, end_offset))

# Projects
projects = []
for i in range(35):
    budget_pct = round(random.uniform(30, 110), 1)
    overdue = random.randint(0, 8)
    start = rand_date(-300, -30)
    end = rand_date(10, 200)
    completion = round(random.uniform(10, 100), 1)
    projects.append({
        "project_id": f"PROJ-{i+1:03}",
        "project_name": f"{random.choice(CLIENTS)} {fake.bs().title()} Platform",
        "client_name": random.choice(CLIENTS),
        "delivery_unit": random.choice(["DU-North", "DU-South", "DU-East"]),
        "project_manager": fake.name(),
        "start_date": start,
        "expected_end_date": end,
        "current_phase": random.choice(PHASES),
        "rag_status": "GREEN",  # recalculated by pipeline
        "completion_pct": completion,
        "planned_hours": random.randint(500, 5000),
        "actual_hours": random.randint(200, 5500),
        "budget_total": random.randint(100000, 2000000),
        "budget_consumed_pct": budget_pct,
        "open_issues": random.randint(0, 20),
        "overdue_tasks": overdue,
        "risk_flag": "",
        "last_updated": date.today(),
    })
pd.DataFrame(projects).to_csv(f"{OUT}/projects.csv", index=False)
print(f"Generated {len(projects)} projects")

# Employees
employees = []
for i in range(120):
    alloc = round(random.uniform(0, 130), 1)
    bench_since = rand_date(-90, -1) if alloc < 40 else None
    employees.append({
        "employee_id": f"EMP-{i+1:04}",
        "full_name": fake.name(),
        "email": fake.email(),
        "designation": random.choice(["Junior Dev", "Senior Dev", "Tech Lead", "QA Engineer", "DevOps Engineer", "BA", "PM"]),
        "department": random.choice(DEPARTMENTS),
        "practice_area": random.choice(["Cloud", "Data", "Web", "Mobile", "ERP"]),
        "reporting_manager": fake.name(),
        "employment_type": random.choice(["Full-time", "Contract"]),
        "location": random.choice(["Bangalore", "Hyderabad", "Pune", "Chennai", "Remote"]),
        "skills": random.sample(SKILLS, k=random.randint(2, 4)),
        "total_allocation_pct": alloc,
        "utilization_status": "Optimal",  # recalculated by pipeline
        "bench_since": bench_since,
        "availability_date": rand_date(0, 60),
        "status": random.choices(["Active", "Active", "Active", "On Leave", "Exited"], k=1)[0],
        "joining_date": rand_date(-1000, -30),
        "last_updated": date.today(),
    })
pd.DataFrame(employees).to_csv(f"{OUT}/employees.csv", index=False)
print(f"Generated {len(employees)} employees")

# CSAT responses (6 months)
responses = []
for i in range(200):
    # weighted toward positive scores to simulate a healthy business
    score = round(random.choices(
        [random.uniform(4.5, 5.0), random.uniform(3.5, 4.4), random.uniform(1.0, 3.4)],
        weights=[50, 30, 20]
    )[0], 1)
    # map 1-5 to NPS 1-10 scale for categorization
    nps_score = score * 2
    responses.append({
        "client_name": random.choice(CLIENTS),
        "project_id": random.choice([p["project_id"] for p in projects]),
        "survey_date": rand_date(-180, 0),
        "survey_type": random.choice(["CSAT", "NPS", "QBR"]),
        "score": score,
        "nps_category": "Promoter" if nps_score >= 9 else ("Passive" if nps_score >= 7 else "Detractor"),
        "feedback_text": fake.sentence(nb_words=20),
        "sentiment": random.choice(["Positive", "Neutral", "Negative"]),
        "key_themes": random.sample(["Delivery", "Communication", "Quality", "Support", "Pricing"], k=2),
        "follow_up_required": score < 7,
        "follow_up_owner": fake.name(),
        "follow_up_status": random.choice(["Open", "In Progress", "Closed"]),
        "account_manager": fake.name(),
    })
pd.DataFrame(responses).to_csv(f"{OUT}/csat_responses.csv", index=False)
print(f"Generated {len(responses)} CSAT responses")

# SLAs
slas = []
SLA_TYPE_CODES = {"Uptime": "UPT", "Response Time": "RSP", "Resolution Time": "RSL", "Delivery": "DEL"}

for i, client in enumerate(CLIENTS):
    for sla_type in SLA_TYPES:
        target = 99.5 if sla_type == "Uptime" else (4 if sla_type == "Response Time" else (24 if sla_type == "Resolution Time" else 95))
        actual = round(target * random.uniform(0.88, 1.05), 2)
        slas.append({
            "sla_id": f"SLA-{i+1:02}-{SLA_TYPE_CODES[sla_type]}",
            "client_name": client,
            "project_id": random.choice([p["project_id"] for p in projects]),
            "sla_type": sla_type,
            "sla_description": f"{sla_type} commitment for {client}",
            "measurement_period": "Monthly",
            "target_value": target,
            "actual_value": actual,
            "compliance_status": "Met",  # recalculated by checker
            "breach_count": random.randint(0, 3),
            "breach_dates": None,
            "has_penalty": random.choice([True, False]),
            "penalty_amount": round(random.uniform(0, 50000), 2),
            "assigned_owner": fake.name(),
            "last_checked": date.today(),
        })
pd.DataFrame(slas).to_csv(f"{OUT}/slas.csv", index=False)
print(f"Generated {len(slas)} SLA records")

# Escalations
escalations = []
for i in range(25):
    escalations.append({
        "title": fake.bs().title(),
        "raised_by": fake.name(),
        "raised_date": rand_date(-30, 0),
        "project_id": random.choice([p["project_id"] for p in projects]),
        "escalation_type": random.choice(["SLA Breach", "Delivery Risk", "People", "Financial"]),
        "severity": random.choice(["P1", "P2", "P3"]),
        "status": random.choice(["Open", "In Progress", "Resolved"]),
        "assigned_owner": fake.name(),
        "resolution_target": rand_date(0, 14),
        "resolution_notes": "",
        "days_open": random.randint(0, 20),
        "resolution_date": None,
        "root_cause": fake.sentence(),
        "preventive_action": fake.sentence(),
        "auto_triggered": random.choice([True, False]),
        "trigger_source": random.choice(["SLA_BREACH", "RED_PROJECT", "LOW_NPS", None]),
    })
pd.DataFrame(escalations).to_csv(f"{OUT}/escalations.csv", index=False)
print(f"Generated {len(escalations)} escalations")

# Timesheets (last 8 weeks)
timesheets = []
emp_ids = [e["employee_id"] for e in employees[:80]]
proj_ids = [p["project_id"] for p in projects]
for emp_id in emp_ids:
    for week_offset in range(8):
        week_end = date.today() - timedelta(weeks=week_offset)
        # randomly skip some to simulate missing submissions
        if random.random() < 0.15:
            continue
        timesheets.append({
            "employee_id": emp_id,
            "week_ending_date": week_end,
            "project_id": random.choice(proj_ids),
            "task_type": random.choice(TASK_TYPES),
            "hours_logged": round(random.uniform(20, 45), 1),
            "is_billable": random.choice([True, False]),
            "approved_by": fake.name(),
            "approval_status": random.choice(["Approved", "Pending"]),
            "submission_date": week_end - timedelta(days=random.randint(0, 3)),
            "submission_status": random.choice(["On Time", "On Time", "Late"]),
            "notes": "",
        })
pd.DataFrame(timesheets).to_csv(f"{OUT}/timesheets.csv", index=False)
print(f"Generated {len(timesheets)} timesheet rows")

# Onboarding tracker
onboarding = []
new_emp_ids = [e["employee_id"] for e in employees if e["status"] == "Active"][:15]
for emp_id in new_emp_ids:
    checklist = round(random.uniform(20, 100), 0)
    onboarding.append({
        "employee_id": emp_id,
        "joining_date": rand_date(-60, 0),
        "assigned_buddy": fake.name(),
        "assigned_manager": fake.name(),
        "laptop_issued": checklist > 30,
        "email_created": checklist > 20,
        "system_access": '{"jira": true, "slack": true, "confluence": false}',
        "induction_done": checklist > 60,
        "policies_signed": checklist > 50,
        "first_project_assigned": checklist > 80,
        "checklist_pct": checklist,
        "onboarding_score": round(random.uniform(3, 5), 1),
        "status": "Completed" if checklist == 100 else "In Progress",
    })
pd.DataFrame(onboarding).to_csv(f"{OUT}/onboarding.csv", index=False)
print(f"Generated {len(onboarding)} onboarding records")

# SOPs
sops = []
sop_data = [
    ("Resource Allocation Process", "HR", "v1.2"),
    ("Escalation Handling Protocol", "Delivery", "v2.0"),
    ("Client Review Cadence", "Client Management", "v1.0"),
    ("Onboarding Checklist", "HR", "v3.1"),
    ("SLA Review Process", "Delivery", "v1.5"),
]
for i, (title, category, version) in enumerate(sop_data):
    sops.append({
        "sop_id": f"SOP-{i+1:02}",
        "title": title,
        "category": category,
        "version": version,
        "owner": fake.name(),
        "last_updated": rand_date(-90, -1),
        "applicable_to": ["All"],
        "document_url": f"https://notion.so/sop-{i+1}",
        "status": "Active",
        "related_escalation_type": random.choice(["SLA Breach", "Delivery Risk", "People", None]),
    })
pd.DataFrame(sops).to_csv(f"{OUT}/sops.csv", index=False)
print(f"Generated {len(sops)} SOPs")

print("\nAll seed data generated in data/seed/")

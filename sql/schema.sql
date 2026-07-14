CREATE TABLE IF NOT EXISTS projects (
    project_id          VARCHAR(50) PRIMARY KEY,
    project_name        VARCHAR(255) NOT NULL,
    client_name         VARCHAR(255),
    delivery_unit       VARCHAR(100),
    project_manager     VARCHAR(100),
    start_date          DATE,
    expected_end_date   DATE,
    current_phase       VARCHAR(50),
    rag_status          VARCHAR(10),
    completion_pct      FLOAT,
    planned_hours       FLOAT,
    actual_hours        FLOAT,
    budget_total        FLOAT,
    budget_consumed_pct FLOAT,
    open_issues         INTEGER,
    overdue_tasks       INTEGER,
    risk_flag           TEXT,
    last_updated        TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS employees (
    employee_id         VARCHAR(50) PRIMARY KEY,
    full_name           VARCHAR(255) NOT NULL,
    email               VARCHAR(255),
    designation         VARCHAR(100),
    department          VARCHAR(100),
    practice_area       VARCHAR(100),
    reporting_manager   VARCHAR(100),
    employment_type     VARCHAR(50),
    location            VARCHAR(100),
    skills              TEXT[],
    total_allocation_pct FLOAT,
    utilization_status  VARCHAR(30),
    bench_since         DATE,
    availability_date   DATE,
    status              VARCHAR(30),
    joining_date        DATE,
    last_updated        TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS employee_allocations (
    id                  SERIAL PRIMARY KEY,
    employee_id         VARCHAR(50) REFERENCES employees(employee_id),
    project_id          VARCHAR(50) REFERENCES projects(project_id),
    allocation_pct      FLOAT,
    start_date          DATE,
    end_date            DATE,
    role_on_project     VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS slas (
    sla_id              VARCHAR(50) PRIMARY KEY,
    client_name         VARCHAR(255),
    project_id          VARCHAR(50),
    sla_type            VARCHAR(100),
    sla_description     TEXT,
    measurement_period  VARCHAR(30),
    target_value        FLOAT,
    actual_value        FLOAT,
    compliance_status   VARCHAR(20),
    breach_count        INTEGER DEFAULT 0,
    breach_dates        DATE[],
    has_penalty         BOOLEAN,
    penalty_amount      FLOAT,
    assigned_owner      VARCHAR(100),
    last_checked        TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS csat_responses (
    response_id         SERIAL PRIMARY KEY,
    client_name         VARCHAR(255),
    project_id          VARCHAR(50),
    survey_date         DATE,
    survey_type         VARCHAR(30),
    score               FLOAT,
    nps_category        VARCHAR(20),
    feedback_text       TEXT,
    sentiment           VARCHAR(20),
    key_themes          TEXT[],
    follow_up_required  BOOLEAN,
    follow_up_owner     VARCHAR(100),
    follow_up_status    VARCHAR(30),
    account_manager     VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS escalations (
    escalation_id       SERIAL PRIMARY KEY,
    title               VARCHAR(255),
    raised_by           VARCHAR(100),
    raised_date         TIMESTAMP DEFAULT NOW(),
    project_id          VARCHAR(50),
    escalation_type     VARCHAR(50),
    severity            VARCHAR(10),
    status              VARCHAR(30),
    assigned_owner      VARCHAR(100),
    resolution_target   DATE,
    resolution_notes    TEXT,
    days_open           INTEGER,
    resolution_date     TIMESTAMP,
    root_cause          TEXT,
    preventive_action   TEXT,
    auto_triggered      BOOLEAN DEFAULT FALSE,
    trigger_source      VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS timesheets (
    id                  SERIAL PRIMARY KEY,
    employee_id         VARCHAR(50) REFERENCES employees(employee_id),
    week_ending_date    DATE,
    project_id          VARCHAR(50),
    task_type           VARCHAR(50),
    hours_logged        FLOAT,
    is_billable         BOOLEAN,
    approved_by         VARCHAR(100),
    approval_status     VARCHAR(20),
    submission_date     TIMESTAMP,
    submission_status   VARCHAR(20),
    notes               TEXT
);

CREATE TABLE IF NOT EXISTS onboarding_tracker (
    id                  SERIAL PRIMARY KEY,
    employee_id         VARCHAR(50) REFERENCES employees(employee_id),
    joining_date        DATE,
    assigned_buddy      VARCHAR(100),
    assigned_manager    VARCHAR(100),
    laptop_issued       BOOLEAN DEFAULT FALSE,
    email_created       BOOLEAN DEFAULT FALSE,
    system_access       JSONB,
    induction_done      BOOLEAN DEFAULT FALSE,
    policies_signed     BOOLEAN DEFAULT FALSE,
    first_project_assigned BOOLEAN DEFAULT FALSE,
    checklist_pct       FLOAT,
    onboarding_score    FLOAT,
    status              VARCHAR(30),
    created_at          TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sent_emails (
    id           SERIAL PRIMARY KEY,
    to_addr      VARCHAR(255) NOT NULL,
    subject      VARCHAR(500) NOT NULL,
    body         TEXT,
    related_type VARCHAR(50),
    related_id   VARCHAR(50),
    sent_by      VARCHAR(100),
    sent_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sops (
    sop_id              VARCHAR(50) PRIMARY KEY,
    title               VARCHAR(255),
    category            VARCHAR(100),
    version             VARCHAR(20),
    owner               VARCHAR(100),
    last_updated        DATE,
    applicable_to       TEXT[],
    document_url        TEXT,
    status              VARCHAR(30),
    related_escalation_type VARCHAR(50)
);

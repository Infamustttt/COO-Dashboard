"""Idempotent startup migrations: safe to run on every boot."""
from src.db.queries import query_df, execute

def run_migrations():
    # Outbox table for the in-app email composer (demo mode).
    execute("""
        CREATE TABLE IF NOT EXISTS sent_emails (
            id           SERIAL PRIMARY KEY,
            to_addr      VARCHAR(255) NOT NULL,
            subject      VARCHAR(500) NOT NULL,
            body         TEXT,
            related_type VARCHAR(50),
            related_id   VARCHAR(50),
            sent_by      VARCHAR(100),
            sent_at      TIMESTAMP DEFAULT NOW()
        )
    """)

    # Seed employee_allocations from timesheet history if empty, so the
    # employee drawer has real "currently working on" data.
    count = int(query_df("SELECT COUNT(*) AS c FROM employee_allocations").iloc[0]["c"])
    if count == 0:
        execute("""
            INSERT INTO employee_allocations
                (employee_id, project_id, allocation_pct, start_date, role_on_project)
            SELECT
                t.employee_id,
                t.project_id,
                ROUND((e.total_allocation_pct / GREATEST(cnt.n, 1))::numeric, 1),
                MIN(t.week_ending_date) - INTERVAL '7 days',
                e.designation
            FROM timesheets t
            JOIN employees e ON e.employee_id = t.employee_id
            JOIN (
                SELECT employee_id, COUNT(DISTINCT project_id) AS n
                FROM timesheets GROUP BY employee_id
            ) cnt ON cnt.employee_id = t.employee_id
            JOIN projects p ON p.project_id = t.project_id
            WHERE e.total_allocation_pct > 0
            GROUP BY t.employee_id, t.project_id, e.total_allocation_pct,
                     e.designation, cnt.n
        """)
        print("[startup] seeded employee_allocations from timesheets")

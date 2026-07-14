from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from api.deps import current_user
from src.db.queries import query_df, execute, fetch_one

router = APIRouter()

@router.get("")
def get_employees(user=Depends(current_user)):
    df = query_df("""
        SELECT employee_id, full_name, email, designation, department,
               practice_area, employment_type, location, skills,
               total_allocation_pct, utilization_status,
               bench_since::text, availability_date::text, status
        FROM employees
        ORDER BY utilization_status, full_name
    """)
    return df.to_dict(orient="records")

@router.get("/summary")
def get_employees_summary(user=Depends(current_user)):
    df = query_df("""
        SELECT
            COUNT(*) FILTER (WHERE status='Active')                        AS active,
            COUNT(*) FILTER (WHERE utilization_status='Bench')             AS bench,
            COUNT(*) FILTER (WHERE utilization_status='Over-allocated')    AS over_allocated,
            COUNT(*) FILTER (WHERE utilization_status='Optimal')           AS optimal,
            COUNT(*) FILTER (WHERE utilization_status='Under-utilised')    AS under_utilised,
            ROUND(AVG(total_allocation_pct) FILTER (WHERE status='Active')::numeric, 1) AS avg_allocation
        FROM employees
    """)
    return df.to_dict(orient="records")[0]

@router.get("/by-department")
def get_by_department(user=Depends(current_user)):
    df = query_df("""
        SELECT department, COUNT(*) as count
        FROM employees WHERE status='Active'
        GROUP BY department ORDER BY count DESC
    """)
    return df.to_dict(orient="records")


# ---------- interactive: employee drawer / assign-from-bench ----------

def _utilization_band(pct: float) -> str:
    if pct <= 0:
        return "Bench"
    if pct < 70:
        return "Under-utilised"
    if pct <= 100:
        return "Optimal"
    return "Over-allocated"

@router.get("/{employee_id}/detail")
def get_employee_detail(employee_id: str, user=Depends(current_user)):
    emp = fetch_one("""
        SELECT employee_id, full_name, email, designation, department,
               practice_area, reporting_manager, employment_type, location,
               skills, total_allocation_pct, utilization_status,
               bench_since::text, availability_date::text, status,
               joining_date::text
        FROM employees WHERE employee_id = :id
    """, {"id": employee_id})
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    allocations = query_df("""
        SELECT a.project_id, p.project_name, p.client_name, p.rag_status,
               a.allocation_pct, a.role_on_project, a.start_date::text
        FROM employee_allocations a
        JOIN projects p ON p.project_id = a.project_id
        WHERE a.employee_id = :id AND (a.end_date IS NULL OR a.end_date >= CURRENT_DATE)
        ORDER BY a.allocation_pct DESC
    """, {"id": employee_id}).to_dict(orient="records")

    return {"employee": emp, "allocations": allocations}

@router.get("/{employee_id}/recommendations")
def get_recommendations(employee_id: str, user=Depends(current_user)):
    emp = fetch_one(
        "SELECT total_allocation_pct FROM employees WHERE employee_id = :id",
        {"id": employee_id})
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    headroom = max(0.0, 100.0 - float(emp["total_allocation_pct"] or 0))
    if headroom <= 0:
        return {"headroom": 0, "projects": []}

    projects = query_df("""
        SELECT p.project_id, p.project_name, p.client_name, p.rag_status,
               p.overdue_tasks, p.open_issues, p.completion_pct, p.project_manager
        FROM projects p
        WHERE p.rag_status IN ('RED', 'AMBER')
          AND p.project_id NOT IN (
              SELECT project_id FROM employee_allocations
              WHERE employee_id = :id AND (end_date IS NULL OR end_date >= CURRENT_DATE)
          )
        ORDER BY CASE p.rag_status WHEN 'RED' THEN 1 ELSE 2 END,
                 p.overdue_tasks DESC, p.open_issues DESC
        LIMIT 5
    """, {"id": employee_id}).to_dict(orient="records")

    for p in projects:
        p["reason"] = (
            f"{p['rag_status']} · {p['overdue_tasks']} overdue tasks · "
            f"{p['open_issues']} open issues · {p['completion_pct']:.0f}% complete"
        )
    return {"headroom": headroom, "projects": projects}

class AssignRequest(BaseModel):
    project_id: str
    allocation_pct: float = 50.0

@router.post("/{employee_id}/assign")
def assign_to_project(employee_id: str, req: AssignRequest, user=Depends(current_user)):
    emp = fetch_one("""
        SELECT employee_id, designation, total_allocation_pct
        FROM employees WHERE employee_id = :id
    """, {"id": employee_id})
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    project = fetch_one("""
        SELECT project_id, project_name, rag_status, overdue_tasks,
               open_issues, budget_consumed_pct
        FROM projects WHERE project_id = :pid
    """, {"pid": req.project_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    current = float(emp["total_allocation_pct"] or 0)
    pct = max(5.0, min(float(req.allocation_pct), 100.0 - current))
    if pct <= 0:
        raise HTTPException(status_code=422, detail="Employee has no allocation headroom")

    already = fetch_one("""
        SELECT id FROM employee_allocations
        WHERE employee_id = :id AND project_id = :pid
          AND (end_date IS NULL OR end_date >= CURRENT_DATE)
    """, {"id": employee_id, "pid": req.project_id})
    if already:
        raise HTTPException(status_code=409, detail="Already allocated to this project")

    # 1. allocation row
    execute("""
        INSERT INTO employee_allocations
            (employee_id, project_id, allocation_pct, start_date, role_on_project)
        VALUES (:id, :pid, :pct, CURRENT_DATE, :role)
    """, {"id": employee_id, "pid": req.project_id, "pct": pct, "role": emp["designation"]})

    # 2. employee: new allocation total + recomputed band
    new_total = round(current + pct, 1)
    new_band = _utilization_band(new_total)
    execute("""
        UPDATE employees
        SET total_allocation_pct = :total, utilization_status = :band,
            bench_since = CASE WHEN :total > 0 THEN NULL ELSE bench_since END,
            last_updated = NOW()
        WHERE employee_id = :id
    """, {"total": new_total, "band": new_band, "id": employee_id})

    # 3. project: added capacity reduces backlog and can lift RAG
    new_overdue = max(0, int(project["overdue_tasks"]) - 3)
    new_issues = max(0, int(project["open_issues"]) - 2)
    budget = float(project["budget_consumed_pct"] or 0)
    if budget >= 95 or new_overdue >= 5:
        new_rag = "RED"
    elif budget >= 80 or new_overdue >= 2:
        new_rag = "AMBER"
    else:
        new_rag = "GREEN"
    execute("""
        UPDATE projects
        SET overdue_tasks = :od, open_issues = :oi, rag_status = :rag,
            last_updated = NOW()
        WHERE project_id = :pid
    """, {"od": new_overdue, "oi": new_issues, "rag": new_rag, "pid": req.project_id})

    return {
        "ok": True,
        "employee": {"employee_id": employee_id, "total_allocation_pct": new_total,
                     "utilization_status": new_band},
        "project": {"project_id": req.project_id, "rag_status": new_rag,
                    "overdue_tasks": new_overdue, "open_issues": new_issues,
                    "previous_rag": project["rag_status"]},
        "allocated_pct": pct,
    }

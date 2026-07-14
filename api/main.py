import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.auth import router as auth_router
from api.routes.projects    import router as projects_router
from api.routes.employees   import router as employees_router
from api.routes.csat        import router as csat_router
from api.routes.slas        import router as slas_router
from api.routes.escalations import router as escalations_router
from api.routes.timesheets  import router as timesheets_router
from api.routes.onboarding  import router as onboarding_router
from api.routes.sops        import router as sops_router
from api.routes.briefing    import router as briefing_router
from api.routes.emails      import router as emails_router
from api.migrations import run_migrations

app = FastAPI(title="COO Operations Centre API", version="2.0.0")

@app.on_event("startup")
def _startup_migrations():
    try:
        run_migrations()
    except Exception as e:
        print(f"[startup] migration failed: {e}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router,        prefix="/api/auth",        tags=["auth"])
app.include_router(projects_router,    prefix="/api/projects",    tags=["projects"])
app.include_router(employees_router,   prefix="/api/employees",   tags=["employees"])
app.include_router(csat_router,        prefix="/api/csat",        tags=["csat"])
app.include_router(slas_router,        prefix="/api/slas",        tags=["slas"])
app.include_router(escalations_router, prefix="/api/escalations", tags=["escalations"])
app.include_router(timesheets_router,  prefix="/api/timesheets",  tags=["timesheets"])
app.include_router(onboarding_router,  prefix="/api/onboarding",  tags=["onboarding"])
app.include_router(sops_router,        prefix="/api/sops",        tags=["sops"])
app.include_router(briefing_router,    prefix="/api/briefing",    tags=["briefing"])
app.include_router(emails_router,      prefix="/api/emails",      tags=["emails"])

@app.get("/api/health")
def health():
    return {"status": "ok"}

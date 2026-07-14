import os
import json
import re
import openai
from datetime import date

# Pages that exist in the frontend router, with display labels.
PAGES = {
    "projects":    "Project Delivery",
    "resources":   "Resource Utilization",
    "sla":         "SLA Compliance",
    "csat":        "Client Satisfaction",
    "escalations": "Escalations",
    "timesheets":  "Timesheets",
    "people":      "People Ops",
}

def _extract_json(text: str) -> dict:
    """Parse JSON from a model reply, tolerating ```json fences."""
    text = text.strip()
    fence = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
    if fence:
        text = fence.group(1)
    return json.loads(text)

def generate_weekly_briefing(metrics: dict) -> dict:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set")
    client = openai.OpenAI(
        api_key=api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )

    page_list = ", ".join(f'"{k}" ({v})' for k, v in PAGES.items())

    prompt = f"""
You are a senior operations analyst preparing a weekly briefing for the COO
of a 2,500-person IT services company. Today is {date.today()}.

Here is this week's operational data:

DELIVERY:
- Total active projects: {metrics['total_projects']}
- RED projects: {metrics['red']}
- AMBER projects: {metrics['amber']}
- GREEN projects: {metrics['green']}

RESOURCES:
- Average utilization: {metrics['avg_utilization']:.1f}%
- Employees on bench: {metrics['bench_count']}
- Over-allocated employees: {metrics['over_allocated']}

SLAs & CLIENT:
- SLA compliance rate: {metrics['sla_compliance']:.1f}%
- SLA breaches this week: {metrics['sla_breaches']}
- Average CSAT score: {metrics['avg_csat']:.2f}/5

ESCALATIONS:
- Open escalations: {metrics['open_escalations']}
- P1 escalations: {metrics['p1_count']}

Respond with ONLY valid JSON, no markdown, no code fences, matching exactly
this schema:

{{
  "summary": "2-3 plain sentences on overall operational health. No markdown.",
  "emergencies": [
    {{
      "title": "Short emergency title (max 8 words)",
      "points": ["2-4 short bullet points, plain text, specific numbers"],
      "action": "One recommended action with an owner",
      "page": "one key from the allowed list below"
    }}
  ]
}}

Rules:
- List the top 3 emergencies requiring COO attention, most severe first.
- "page" must be exactly one of: {page_list}.
  Pick the page where the COO can investigate that emergency.
- Plain text only inside strings: no asterisks, no markdown, no headers.
- Be direct and specific. Avoid filler phrases.
"""

    response = client.chat.completions.create(
        model="gemini-flash-latest",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    data = _extract_json(response.choices[0].message.content)

    # Validate shape and page keys so the frontend never gets garbage.
    if "summary" not in data or "emergencies" not in data:
        raise ValueError("Model response missing required keys")
    for e in data["emergencies"]:
        if e.get("page") not in PAGES:
            e["page"] = "projects"
        e["page_label"] = PAGES[e["page"]]
    return data

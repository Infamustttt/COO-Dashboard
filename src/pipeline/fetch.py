"""
Fetches raw data from all external APIs.
In demo mode, this step is skipped and seed data is used instead.
"""
from src.integrations.jira_client import JiraClient
from src.integrations.hrms_client import HRMSClient
from src.integrations.survey_client import SurveyClient
import os

def fetch_all():
    jira = JiraClient()
    hrms = HRMSClient()
    survey = SurveyClient()

    projects = jira.get_all_projects()
    employees = hrms.get_all_employees()
    responses = survey.get_responses(os.getenv("TYPEFORM_FORM_ID"))

    return {
        "projects": projects,
        "employees": employees,
        "survey_responses": responses
    }

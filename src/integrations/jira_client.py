import requests
import base64
import os

class JiraClient:
    def __init__(self):
        email = os.getenv("JIRA_EMAIL")
        token = os.getenv("JIRA_API_TOKEN")
        self.base_url = os.getenv("JIRA_BASE_URL")
        credentials = base64.b64encode(f"{email}:{token}".encode()).decode()
        self.headers = {
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/json"
        }

    def get_all_projects(self):
        response = requests.get(f"{self.base_url}/project", headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_issues_for_project(self, project_key: str):
        response = requests.get(
            f"{self.base_url}/search",
            headers=self.headers,
            params={
                "jql": f"project = {project_key}",
                "fields": "summary,status,assignee,duedate,priority,timespent,timeoriginalestimate",
                "maxResults": 500
            }
        )
        response.raise_for_status()
        return response.json()["issues"]

    def get_worklogs_for_issue(self, issue_id: str):
        response = requests.get(
            f"{self.base_url}/issue/{issue_id}/worklog",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()["worklogs"]

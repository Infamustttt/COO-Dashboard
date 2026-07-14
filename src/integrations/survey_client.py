import requests
import os

class SurveyClient:
    def __init__(self):
        self.token = os.getenv("TYPEFORM_API_TOKEN")
        self.base_url = "https://api.typeform.com"
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def get_responses(self, form_id: str, since: str = None):
        params = {"page_size": 200}
        if since:
            params["since"] = since
        response = requests.get(
            f"{self.base_url}/forms/{form_id}/responses",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()["items"]

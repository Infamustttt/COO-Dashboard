import requests
import os

class HRMSClient:
    def __init__(self):
        self.api_key = os.getenv("HRMS_API_KEY")
        company = os.getenv("HRMS_COMPANY_SLUG")
        self.base_url = f"https://api.bamboohr.com/api/gateway.php/{company}/v1"
        self.headers = {"Accept": "application/json"}
        self.auth = (self.api_key, "x")

    def get_all_employees(self):
        response = requests.get(
            f"{self.base_url}/employees/directory",
            headers=self.headers,
            auth=self.auth
        )
        response.raise_for_status()
        return response.json()["employees"]

    def get_employee_details(self, employee_id: str):
        fields = "firstName,lastName,jobTitle,department,location,hireDate,employmentHistoryStatus"
        response = requests.get(
            f"{self.base_url}/employees/{employee_id}",
            headers=self.headers,
            auth=self.auth,
            params={"fields": fields}
        )
        response.raise_for_status()
        return response.json()

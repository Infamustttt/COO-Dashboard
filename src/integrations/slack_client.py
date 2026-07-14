import requests
import os

class SlackClient:
    def __init__(self):
        self.token = os.getenv("SLACK_BOT_TOKEN")
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def send_message(self, channel: str, text: str, blocks: list = None):
        payload = {"channel": channel, "text": text}
        if blocks:
            payload["blocks"] = blocks
        response = requests.post(
            "https://slack.com/api/chat.postMessage",
            headers=self.headers,
            json=payload
        )
        return response.json()

    def send_dm(self, user_email: str, text: str):
        # look up user ID by email first
        lookup = requests.get(
            "https://slack.com/api/users.lookupByEmail",
            headers=self.headers,
            params={"email": user_email}
        )
        user_id = lookup.json()["user"]["id"]
        return self.send_message(channel=user_id, text=text)

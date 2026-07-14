import os
import json
import openai

def analyze_feedback(feedback_text: str) -> dict:
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    prompt = f"""
Analyze this client feedback and return a JSON object with:
- "sentiment": one of "Positive", "Neutral", "Negative"
- "themes": a list of 1-3 short theme labels (e.g. "Delivery delays", "Good PM", "Communication gaps")

Feedback: "{feedback_text}"

Return ONLY valid JSON, no explanation.
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return json.loads(response.choices[0].message.content)

import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class AIService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

    def _clean_json_text(self, text: str) -> str:
        cleaned = text.strip()

        if cleaned.startswith("```json"):
            cleaned = cleaned.removeprefix("```json").strip()

        if cleaned.startswith("```"):
            cleaned = cleaned.removeprefix("```").strip()

        if cleaned.endswith("```"):
            cleaned = cleaned.removesuffix("```").strip()

        return cleaned

    def explain_predictions(self, predictions: list[dict]) -> dict:
        compact_predictions = predictions[:20]

        prompt = f"""
You are an F1 qualifying prediction analyst.

Explain the following predicted qualifying order in concise, user-friendly language.

Rules:
- Do not claim certainty.
- Do not invent weather, upgrades, penalties, crashes, grid penalties, or live practice data.
- Use only the supplied prediction fields.
- Mention uncertainty where appropriate.
- Return valid JSON only.
- Do not wrap the JSON in markdown fences.

Predictions:
{json.dumps(compact_predictions, indent=2)}

Return JSON in this exact shape:
{{
  "summary": "2-3 sentence overview",
  "driver_explanations": [
    {{
      "driver": "VER",
      "predicted_position": 1,
      "explanation": "Short explanation"
    }}
  ]
}}
"""

        response = self.client.responses.create(
            model=self.model,
            input=prompt,
        )

        text = self._clean_json_text(response.output_text)

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {
                "summary": text,
                "driver_explanations": [],
            }
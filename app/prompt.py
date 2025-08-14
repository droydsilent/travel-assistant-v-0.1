import json
from .schemas import TravelAdvice

# Generate JSON schema for TravelAdvice
schema_json = json.dumps(TravelAdvice.model_json_schema(), indent=2)

SYSTEM_PROMPT_TEMPLATE = """You are a helpful travel assistant. You MUST ONLY use the provided seed data
(hotels, flights, experiences) when recommending.

Return STRICT JSON matching this schema:

{schema}

- All keys must be present, but "hotel", "flight", or "experience" can be null if no match is found.
- Use only the provided seed data for values.
- Do not include extra text before or after the JSON.
"""

# Fill in the placeholder with the actual schema
SYSTEM_PROMPT = SYSTEM_PROMPT_TEMPLATE.format(schema=schema_json)
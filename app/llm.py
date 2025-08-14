import openai
import json
from pydantic import ValidationError
from schemas import TravelAdvice
from prompt import SYSTEM_PROMPT
from services.logger_setup import get_logger

logger = get_logger(__name__)

def call_llm_with_seed(query, seed_snippets):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"User query: {query}\n\nRelevant seed data:\n{seed_snippets}"}
    ]
    resp = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0,
        response_format={"type": "json_object"}
    )

    raw_output = resp.choices[0].message.content
    logger.info(f"LLM response: {raw_output}")
    # Parse JSON and validate against TravelAdvice
    try:
        parsed_json = json.loads(raw_output)
        advice = TravelAdvice(**parsed_json)
        return advice
    except json.JSONDecodeError as e:
        raise ValueError(f"Model did not return valid JSON: {e}\nOutput:\n{raw_output}")
    except ValidationError as e:
        raise ValueError(f"Model JSON failed schema validation: {e}\nOutput:\n{raw_output}")
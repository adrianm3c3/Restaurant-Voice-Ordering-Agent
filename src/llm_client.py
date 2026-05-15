import json
import logging

from openai import OpenAI

from src.config import CONFIG


logger = logging.getLogger(__name__)


def build_client():
    return OpenAI(
        base_url=CONFIG["api"]["base_url"],
        api_key=CONFIG["api"]["api_key"],
        timeout=10.0,
        max_retries=0,
    )


client = build_client()


def get_default_model(model_name=None):
    return (
        model_name
        or CONFIG["model"].get("agent")
        or CONFIG["model"].get("parser")
        or CONFIG["model"].get("name")
    )


def chat_completion(
    system_prompt,
    user_prompt,
    model_name=None,
    temperature=None,
    max_tokens=None,
):
    try:
        default_model = get_default_model(model_name)

        if not default_model:
            raise ValueError("No model name found in CONFIG['model'].")

        final_temperature = (
            temperature
            if temperature is not None
            else CONFIG["generation"]["temperature"]
        )

        final_max_tokens = (
            max_tokens
            if max_tokens is not None
            else CONFIG["generation"]["max_tokens"]
        )

        logger.info(
            "Sending LLM request",
            extra={
                "model": default_model,
                "temperature": final_temperature,
                "max_tokens": final_max_tokens,
            },
        )

        response = client.chat.completions.create(
            model=default_model,
            temperature=final_temperature,
            max_tokens=final_max_tokens,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

        content = response.choices[0].message.content

        if not content:
            logger.warning("LLM returned empty response")
            return ""

        cleaned = content.strip()

        logger.info(
            "LLM response received",
            extra={
                "response_length": len(cleaned),
            },
        )

        return cleaned

    except Exception as e:
        logger.exception("LLM call failed")
        raise RuntimeError(f"LLM call failed: {e}") from e


def extract_json_from_text(text):
    if not text:
        return None

    text = text.strip()

    try:
        return json.loads(text)
    except Exception:
        pass

    if text.startswith("```"):
        cleaned = (
            text.replace("```json", "")
            .replace("```JSON", "")
            .replace("```", "")
            .strip()
        )

        try:
            return json.loads(cleaned)
        except Exception:
            pass

    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1 and end >= start:
        candidate = text[start:end + 1]

        try:
            return json.loads(candidate)
        except Exception:
            pass

    start = text.find("[")
    end = text.rfind("]")

    if start != -1 and end != -1 and end >= start:
        candidate = text[start:end + 1]

        try:
            return json.loads(candidate)
        except Exception:
            pass

    return None
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from trampomemo.core.provider_errors import ProviderError


def post_openai_json(*, url: str, api_key: str, payload: dict, provider: str) -> dict:
    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = _read_error_detail(exc)
        raise ProviderError(
            _provider_error_message(status_code=exc.code, detail=detail),
            provider=provider,
            status_code=exc.code,
        ) from exc
    except URLError as exc:
        raise ProviderError(
            f"{provider} provider is unavailable: {exc.reason}",
            provider=provider,
        ) from exc


def _read_error_detail(exc: HTTPError) -> str:
    try:
        payload = json.loads(exc.read().decode("utf-8"))
    except json.JSONDecodeError, UnicodeDecodeError:
        return exc.reason
    error = payload.get("error", {})
    return error.get("message") or exc.reason


def _provider_error_message(*, status_code: int, detail: str) -> str:
    if status_code in {401, 403}:
        return f"OpenAI authentication failed: {detail}"
    if status_code == 429:
        return f"OpenAI rate limit reached: {detail}"
    if status_code == 404:
        return f"OpenAI model or endpoint was not found: {detail}"
    if status_code >= 500:
        return f"OpenAI provider is temporarily unavailable: {detail}"
    return f"OpenAI provider request failed: {detail}"

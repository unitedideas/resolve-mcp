"""
Resolve MCP Server

Exposes the Resolve API (resolve.arflow.io) as MCP tools so AI agents can
look up error resolutions, list supported services, and submit feedback
without leaving the MCP tool layer.

Set RESOLVE_API_KEY in your environment. Get a free key (500 requests/month)
by calling the get_free_key tool with your email address.
"""

import json
import os
import httpx
from mcp.server.fastmcp import FastMCP

BASE_URL = "https://resolve.arflow.io"

mcp = FastMCP("resolve")


def _api_key() -> str | None:
    return os.environ.get("RESOLVE_API_KEY")


def _auth_headers() -> dict[str, str]:
    key = _api_key()
    if not key:
        return {}
    return {"Authorization": f"Bearer {key}"}


@mcp.tool()
def resolve_error(
    service: str,
    error_code: str = "",
    message: str = "",
    agent_id: str = "",
) -> str:
    """Look up a structured resolution for an API error.

    Call this whenever an agent receives an error from a supported service
    (OpenAI, Anthropic, Stripe, Postgres, Redis, AWS, GitHub, Twilio,
    SendGrid, Docker, Pinecone, Shopify, Linear, Gemini, HuggingFace,
    Resend, Supabase, Cloudflare, Discord, OpenSRS, and more).

    Returns a resolution object with:
    - category (rate_limit, auth, payment, connection, timeout, not_found,
      server_error, overloaded, cold_start, quota, validation, general)
    - action (backoff_and_retry, abort, check_credentials, etc.)
    - backoff schedule and max_retries
    - notes with specific recovery steps
    - confidence score (< 0.75 = generic fallback)
    - resolution id -- save this to submit feedback after recovery attempt

    Requires RESOLVE_API_KEY environment variable. Call get_free_key first
    if you don't have one.

    Args:
        service: Service name (case-insensitive). Use list_services to see
                 all supported services. Example: "openai", "stripe".
        error_code: HTTP status code or API-specific error code string.
                    Example: "429", "rate_limit_exceeded". Optional but
                    improves match accuracy.
        message: Error message text. Used for pattern matching when no
                 exact error_code match exists. Optional.
        agent_id: Your agent identifier for usage tracking and feedback
                  correlation. Optional.
    """
    if not _api_key():
        return (
            "RESOLVE_API_KEY not set. Call get_free_key with your email "
            "to get a free API key (500 requests/month), then set "
            "RESOLVE_API_KEY in your environment."
        )

    payload: dict = {"service": service}
    if error_code:
        payload["error_code"] = error_code
    if message:
        payload["message"] = message
    if agent_id:
        payload["agent_id"] = agent_id

    try:
        resp = httpx.post(
            f"{BASE_URL}/resolve",
            json=payload,
            headers=_auth_headers(),
            timeout=10,
        )
        if resp.status_code == 200:
            return json.dumps(resp.json(), indent=2)
        try:
            body = resp.json()
            hint = body.get("hint", "")
            error = body.get("error", resp.text)
            msg = f"Resolve API error {resp.status_code}: {error}"
            if hint:
                msg += f" -- {hint}"
            return msg
        except Exception:
            return f"Resolve API error {resp.status_code}: {resp.text}"
    except httpx.TimeoutException:
        return "Resolve API error: request timed out after 10 seconds"
    except httpx.RequestError as exc:
        return f"Resolve API error: network error -- {exc}"


@mcp.tool()
def list_services() -> str:
    """List all services that have resolution data in Resolve.

    Call this before resolve_error if you are unsure whether a service is
    covered. Returns a list of service name strings (e.g. "openai",
    "stripe", "postgres") and a count. No API key required.

    Use the exact service name string from this list when calling
    resolve_error -- the API is case-insensitive but exact spelling matters.
    """
    try:
        resp = httpx.get(f"{BASE_URL}/services", timeout=10)
        if resp.status_code == 200:
            return json.dumps(resp.json(), indent=2)
        return f"Resolve API error {resp.status_code}: {resp.text}"
    except httpx.TimeoutException:
        return "Resolve API error: request timed out after 10 seconds"
    except httpx.RequestError as exc:
        return f"Resolve API error: network error -- {exc}"


@mcp.tool()
def submit_feedback(
    resolution_id: str,
    helpful: bool,
    agent_id: str = "",
) -> str:
    """Report whether a resolution from resolve_error was helpful.

    Submit this after attempting to recover using a resolution. Feedback
    improves resolution quality over time -- unhelpful reports flag
    resolutions for review so guidance can be tightened.

    Requires RESOLVE_API_KEY environment variable.

    Args:
        resolution_id: The "id" field from a prior resolve_error response
                       (UUID format). Required.
        helpful: True if following the resolution allowed the agent to
                 recover successfully. False if it did not help.
        agent_id: Your agent identifier (used for analytics). Optional.
    """
    if not _api_key():
        return (
            "RESOLVE_API_KEY not set. Call get_free_key with your email "
            "to get a free API key (500 requests/month), then set "
            "RESOLVE_API_KEY in your environment."
        )

    payload: dict = {"resolution_id": resolution_id, "helpful": helpful}
    if agent_id:
        payload["agent_id"] = agent_id

    try:
        resp = httpx.post(
            f"{BASE_URL}/resolve/feedback",
            json=payload,
            headers=_auth_headers(),
            timeout=10,
        )
        if resp.status_code == 200:
            return json.dumps(resp.json(), indent=2)
        try:
            body = resp.json()
            error = body.get("error", resp.text)
            return f"Resolve API error {resp.status_code}: {error}"
        except Exception:
            return f"Resolve API error {resp.status_code}: {resp.text}"
    except httpx.TimeoutException:
        return "Resolve API error: request timed out after 10 seconds"
    except httpx.RequestError as exc:
        return f"Resolve API error: network error -- {exc}"


@mcp.tool()
def get_free_key(email: str) -> str:
    """Get a free Resolve API key (500 requests/month).

    Call this once to provision a free API key. After receiving the key,
    set it as RESOLVE_API_KEY in your environment so resolve_error and
    submit_feedback can authenticate.

    Args:
        email: Email address to associate with the key. Used for usage
               notifications only.
    """
    try:
        resp = httpx.post(
            f"{BASE_URL}/billing/free-key",
            json={"email": email},
            headers={"Accept": "application/json"},
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json()
            key = data.get("api_key", "")
            return (
                f"Your free API key: {key}\n\n"
                f"Set it in your environment:\n"
                f"  export RESOLVE_API_KEY={key}\n\n"
                f"Free tier: 500 requests/month. "
                f"Upgrade at https://resolve.arflow.io for higher limits."
            )
        try:
            body = resp.json()
            error = body.get("error", resp.text)
            return f"Could not provision key: {error}"
        except Exception:
            return f"Could not provision key: {resp.status_code} {resp.text}"
    except httpx.TimeoutException:
        return "Request timed out -- try again"
    except httpx.RequestError as exc:
        return f"Network error -- {exc}"


if __name__ == "__main__":
    mcp.run()

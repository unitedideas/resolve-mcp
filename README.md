# Resolve MCP Server

[![PyPI](https://img.shields.io/pypi/v/resolve-mcp)](https://pypi.org/project/resolve-mcp/)
[![Python](https://img.shields.io/badge/python-3.10+-blue)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-compatible-purple)](https://modelcontextprotocol.io)

Structured error recovery for AI agents. When your agent hits a 429, a connection timeout, or an auth failure, Resolve returns a resolution playbook -- not a generic error message.

Works with Claude Code, Claude Desktop, Cursor, Windsurf, and any MCP-compatible client.

## The problem

AI agents crash on API errors they could recover from. A `429 Too Many Requests` from OpenAI needs exponential backoff. A Stripe `authentication_error` needs credential rotation. A Postgres `ECONNREFUSED` needs a connection pool reset. But agents don't know any of this -- they either retry blindly or give up.

## The solution

Resolve provides structured resolution playbooks for 20+ services. Each resolution includes:

- **Category** -- `rate_limit`, `auth`, `payment`, `connection`, `timeout`, `server_error`, `overloaded`, `quota`, `validation`, and more
- **Action** -- `backoff_and_retry`, `abort`, `check_credentials`, `switch_region`, etc.
- **Backoff schedule** -- exact delays in seconds (e.g., `[1, 2, 4, 8, 16]`)
- **Max retries** -- how many attempts before giving up
- **Recovery notes** -- specific steps for the service and error code
- **Confidence score** -- below 0.75 means generic fallback; above means high-confidence match

## Tools

| Tool | Description |
|---|---|
| `resolve_error` | Look up a resolution for a service + error code/message. Returns structured playbook. |
| `list_services` | List all 20+ supported services. No API key required. |
| `submit_feedback` | Report whether a resolution helped. Improves quality over time. |
| `get_free_key` | Provision a free API key (500 req/month) with just an email. |

## Supported services

`anthropic` `aws` `cloudflare` `discord` `docker` `gemini` `github` `huggingface` `linear` `openai` `opensrs` `pinecone` `postgres` `redis` `resend` `sendgrid` `shopify` `stripe` `supabase` `twilio`

## Quick start

### 1. Install

```bash
pip install resolve-mcp
```

Or run directly with uvx (no install needed):

```bash
uvx resolve-mcp
```

### 2. Get a free API key

From your terminal:

```bash
curl -s -X POST https://resolve.arflow.io/billing/free-key \
  -H 'Content-Type: application/json' \
  -d '{"email":"you@example.com"}' | jq -r .api_key
```

Or call the `get_free_key` tool from within your MCP client -- no terminal needed.

### 3. Configure your client

#### Claude Code

```bash
claude mcp add resolve -e RESOLVE_API_KEY=rsl_your_key -- python -m resolve_mcp
```

Or add to `.claude/settings.json`:

```json
{
  "mcpServers": {
    "resolve": {
      "command": "python",
      "args": ["-m", "resolve_mcp"],
      "env": {
        "RESOLVE_API_KEY": "rsl_your_key_here"
      }
    }
  }
}
```

#### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "resolve": {
      "command": "python",
      "args": ["-m", "resolve_mcp"],
      "env": {
        "RESOLVE_API_KEY": "rsl_your_key_here"
      }
    }
  }
}
```

#### Cursor / Windsurf / any MCP client

```json
{
  "resolve": {
    "command": "python",
    "args": ["-m", "resolve_mcp"],
    "env": {
      "RESOLVE_API_KEY": "rsl_your_key_here"
    }
  }
}
```

#### Standalone (stdio)

```bash
RESOLVE_API_KEY=rsl_your_key python -m resolve_mcp
```

## Usage examples

**Agent hits a rate limit:**

```
Agent: "I got a 429 from OpenAI"
-> resolve_error(service="openai", error_code="429")

Returns:
{
  "category": "rate_limit",
  "action": "backoff_and_retry",
  "backoff_schedule": [1, 2, 4, 8, 16],
  "max_retries": 5,
  "notes": "Token-per-minute limit. Reduce batch size or switch to a higher-tier key.",
  "confidence": 0.95
}
```

**Agent gets an auth failure:**

```
Agent: "Stripe returned authentication_error"
-> resolve_error(service="stripe", error_code="authentication_error")

Returns:
{
  "category": "auth",
  "action": "check_credentials",
  "backoff_schedule": [],
  "max_retries": 0,
  "notes": "API key is invalid or revoked. Verify the key starts with sk_live_ or sk_test_. Check Stripe dashboard for key status.",
  "confidence": 0.92
}
```

**Feedback loop:**

```
Agent: "The resolution worked."
-> submit_feedback(resolution_id="3fa85f64-...", helpful=true)
```

## Why not just hardcode retry logic?

You can. But then you maintain retry strategies for every service your agent calls, across every error code, and update them when services change their rate limit behavior. Resolve centralizes this so your agent code stays clean and the resolution data stays current.

## API

The MCP server wraps the [Resolve REST API](https://resolve.arflow.io):

| Endpoint | Method | Auth required |
|---|---|---|
| `/resolve` | POST | Yes |
| `/services` | GET | No |
| `/resolve/feedback` | POST | Yes |
| `/billing/free-key` | POST | No |

Full OpenAPI spec: [resolve.arflow.io/openapi.json](https://resolve.arflow.io/openapi.json)

## Pricing

| Plan | Requests/month | Price |
|---|---|---|
| Free | 500 | $0 |
| Pro | 50,000 | $29/mo |
| Fleet | 500,000 | $99/mo |

Get started free: [resolve.arflow.io](https://resolve.arflow.io)

## Contributing

Issues and PRs welcome. If you want resolution data for a service we don't cover yet, open an issue with the service name and common error codes.

## License

MIT

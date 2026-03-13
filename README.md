# Resolve MCP Server

<!-- mcp-name: io.github.unitedideas/resolve -->

MCP server for the [Resolve](https://resolve.arflow.io) agent error resolution API. Install it in Claude Code, Claude Desktop, or any MCP client and your agent can look up error resolutions, list supported services, and submit feedback without leaving the tool layer.

## Tools

| Tool | Description |
|---|---|
| `resolve_error` | Given a service and error code/message, returns a structured resolution with action, backoff schedule, and recovery notes |
| `list_services` | Lists all services that have resolution data (20+ services). No API key required. |
| `submit_feedback` | Reports whether a resolution was helpful -- improves quality over time |
| `get_free_key` | Provisions a free API key (500 requests/month) with just an email address |

## Supported services

anthropic, aws, cloudflare, discord, docker, gemini, github, huggingface, linear, openai, opensrs, pinecone, postgres, redis, resend, sendgrid, shopify, stripe, supabase, twilio

## Quick start

```bash
pip install resolve-error-mcp
```

Get an API key (free, 500 requests/month):

```bash
export RESOLVE_API_KEY=$(curl -s -X POST https://resolve.arflow.io/billing/free-key \
  -H 'Content-Type: application/json' \
  -d '{"email":"you@example.com"}' | jq -r .api_key)
```

Or call the `get_free_key` tool from within your MCP client.

## Install

### Claude Code

```bash
claude mcp add resolve -- python -m server
```

Or add to `.claude/settings.json`:

```json
{
  "mcpServers": {
    "resolve": {
      "command": "python",
      "args": ["-m", "server"],
      "env": {
        "RESOLVE_API_KEY": "rsl_your_key_here"
      }
    }
  }
}
```

### Claude Desktop

```bash
mcp install server.py --name resolve
```

Or add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "resolve": {
      "command": "python",
      "args": ["/path/to/server.py"],
      "env": {
        "RESOLVE_API_KEY": "rsl_your_key_here"
      }
    }
  }
}
```

### Run standalone (stdio)

```bash
RESOLVE_API_KEY=rsl_... python server.py
```

## Usage example

Once installed, your agent can ask:

> "I got a 429 from OpenAI -- how should my agent handle it?"

The MCP client calls `resolve_error(service="openai", error_code="429")` and returns a structured resolution with backoff schedule, retry strategy, and confidence score.

After the agent attempts recovery:

> "The resolution worked. Submit positive feedback for resolution id `3fa85f64-...`."

Calls `submit_feedback(resolution_id="3fa85f64-...", helpful=True)`.

## Pricing

- **Free**: 500 requests/month (get a key via `get_free_key` tool)
- **Pro**: $29/month -- 50,000 requests
- **Fleet**: $99/month -- 500,000 requests

https://resolve.arflow.io

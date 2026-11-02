"""Explicit opt-in tool-call round-trip probe with a harmless fixture-free tool."""

import json
import os
import ssl
import sys

import httpx
import truststore

key = os.getenv("META_API_KEY")
if not key:
    sys.exit("META_API_KEY is not configured. Live Meta verification remains pending.")
model = os.getenv("META_MODEL", "muse-spark-1.3")
client = httpx.Client(
    base_url="https://api.meta.ai/v1",
    headers={"Authorization": f"Bearer {key}"},
    timeout=60,
    verify=truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT),
)
tools = [
    {
        "type": "function",
        "function": {
            "name": "add_minor_units",
            "description": "Add two integer amounts expressed in minor currency units.",
            "parameters": {
                "type": "object",
                "properties": {"a": {"type": "integer"}, "b": {"type": "integer"}},
                "required": ["a", "b"],
            },
        },
    }
]
messages = [{"role": "user", "content": "Use the tool to add 12345 and 67890, then state the sum."}]
called = False
for _ in range(5):
    response = client.post(
        "/chat/completions", json={"model": model, "messages": messages, "tools": tools}
    )
    if response.status_code != 200:
        sys.exit(f"Tool probe failed: HTTP {response.status_code}. Response body omitted.")
    message = response.json()["choices"][0]["message"]
    if not message.get("tool_calls"):
        print(message["content"])
        break
    messages.append(message)
    for call in message["tool_calls"]:
        args = json.loads(call["function"]["arguments"])
        called = True
        messages.append(
            {"role": "tool", "tool_call_id": call["id"], "content": str(args["a"] + args["b"])}
        )
sys.exit(0 if called else "Model answered without calling the tool; round-trip not verified.")

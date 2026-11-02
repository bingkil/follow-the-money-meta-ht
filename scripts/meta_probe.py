"""Explicit opt-in connectivity probe; never prints credentials."""

import os
import ssl
import sys

import httpx
import truststore

key = os.getenv("META_API_KEY")
if not key:
    sys.exit("META_API_KEY is not configured. Live Meta verification remains pending.")
response = httpx.post(
    "https://api.meta.ai/v1/chat/completions",
    headers={"Authorization": f"Bearer {key}"},
    json={
        "model": os.getenv("META_MODEL", "muse-spark-1.3"),
        "messages": [{"role": "user", "content": "Reply with the word ready."}],
    },
    timeout=30,
    # OS store so corporate TLS-inspection roots are trusted; verification stays on.
    verify=truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT),
)
if response.status_code != 200:
    sys.exit(f"Meta probe failed: HTTP {response.status_code}. Response body omitted.")
print(response.json()["choices"][0]["message"]["content"])

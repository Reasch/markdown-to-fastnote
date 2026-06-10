#!/usr/bin/env python3
"""
Fast Note Sync - Push Markdown notes to the fast-note-sync service (Obsidian can sync)

Usage:
    python sync_note.py --file <markdown-file-path> --vault <vault-name> --path <remote-path>
    python sync_note.py --content "content" --vault <vault-name> --path <remote-path>

Examples:
    python sync_note.py --file ./note.md --vault note --path "AI Study/test.md"
    python sync_note.py --content "# Hello" --vault note --path "test/hello.md"
"""

import argparse
import hashlib
import json
import os
import sys
import time
import requests
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Default configuration
DEFAULT_BASE_URL = os.environ.get("FNS_BASE_URL", "http://192.168.1.254:9100")
DEFAULT_CREDENTIALS = os.environ.get("FNS_CREDENTIALS", "test")
DEFAULT_PASSWORD = os.environ.get("FNS_PASSWORD", "test")


def java_hashcode(s: str) -> int:
    """Compute Java-style String.hashCode() (32-bit signed integer)"""
    h = 0
    for c in s:
        h = (31 * h + ord(c)) & 0xFFFFFFFF
    # Convert to signed 32-bit
    if h >= 0x80000000:
        h -= 0x100000000
    return h


def login(base_url: str, credentials: str, password: str) -> str:
    """Login and obtain token"""
    url = f"{base_url}/api/user/login?_={int(time.time() * 1000)}_crtdcclq1vr&lang=zh-CN"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
        "Content-Type": "application/json",
        "X-Client": "WebGui",
    }
    payload = {
        "credentials": credentials,
        "password": password,
        "remember": False,
        "tokenId": 1,
    }

    resp = requests.post(url, headers=headers, json=payload, verify=False, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    # Try to extract token from common fields
    token = None
    if isinstance(data, dict):
        token = data.get("token") or data.get("accessToken") or data.get("data", {}).get("token") if isinstance(data.get("data"), dict) else None
        if not token and isinstance(data.get("data"), str):
            token = data["data"]

    if not token:
        print(f"❌ Login failed, response: {json.dumps(data, ensure_ascii=False)}", file=sys.stderr)
        sys.exit(1)

    return token


def sync_note(
    base_url: str,
    token: str,
    vault: str,
    path: str,
    content: str,
) -> dict:
    """Sync note to fast-note-sync"""
    path_hash = java_hashcode(path)
    content_hash = java_hashcode(content)
    timestamp = str(int(time.time() * 1000))

    url = f"{base_url}/api/note?_={timestamp}&lang=zh-CN"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
        "Lang": "zh-CN",
        "X-Client": "WebGui",
    }
    payload = {
        "vault": vault,
        "path": path,
        "content": content,
        "pathHash": str(path_hash),
        "contentHash": str(content_hash),
    }

    resp = requests.post(url, headers=headers, json=payload, verify=False, timeout=15)
    resp.raise_for_status()
    return resp.json()


def main():
    parser = argparse.ArgumentParser(description="Sync Markdown notes to the fast-note-sync service")
    parser.add_argument("--file", "-f", help="Markdown file path")
    parser.add_argument("--content", "-c", help="Pass content directly (use --file or --content)")
    parser.add_argument("--vault", "-v", default="note", help="Vault name (default: note)")
    parser.add_argument("--path", "-p", required=True, help="Remote save path, e.g. 'AI Study/test.md'")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Service URL")
    parser.add_argument("--credentials", default=DEFAULT_CREDENTIALS, help="Login username")
    parser.add_argument("--password", default=DEFAULT_PASSWORD, help="Login password")

    args = parser.parse_args()

    # Get content
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            content = f.read()
    elif args.content:
        content = args.content
    else:
        print("❌ Please specify --file or --content", file=sys.stderr)
        sys.exit(1)

    # Login
    print(f"🔐 Logging in {args.base_url} ...")
    token = login(args.base_url, args.credentials, args.password)
    print(f"✅ Login successful, token obtained")

    # Sync note
    print(f"📝 Syncing note → {args.vault}/{args.path} ...")
    result = sync_note(args.base_url, token, args.vault, args.path, content)
    print(f"✅ Sync successful!")
    print(f"   Response: {json.dumps(result, ensure_ascii=False, indent=2)}")


if __name__ == "__main__":
    main()

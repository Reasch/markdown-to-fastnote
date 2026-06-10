# Markdown to FastNote

Push Markdown notes to the Fast-Note-Sync service for Obsidian auto-sync.

> [中文](README_ZH.md)

## Installation

```bash
pip install requests urllib3
```

## Quick Start

```bash
# Configure via environment variables
export FNS_CREDENTIALS="your-username"
export FNS_PASSWORD="your-password"
export FNS_BASE_URL="http://192.168.1.254:9100"

# Sync local file
python3 scripts/sync_note.py -f ./articles/test.md -p "AI Study/test.md"

# Write content directly
python3 scripts/sync_note.py -c "# Hello World" -p "test/hello.md"

# Specify vault (default: note)
python3 scripts/sync_note.py -f note.md -p "daily/2024-01-01.md" -v myvault
```

## Parameters

| Parameter | Short | Required | Description |
|-----------|-------|----------|-------------|
| `--file` | `-f` | One of two | Local Markdown file path |
| `--content` | `-c` | One of two | Pass text content directly |
| `--path` | `-p` | ✅ | Remote save path, e.g. `AI Study/test.md` |
| `--vault` | `-v` | ❌ | Vault name, default `note` |
| `--base-url` | — | ❌ | Service URL (default from env `FNS_BASE_URL`, fallback `http://192.168.100.106:9100`) |
| `--credentials` | — | ❌ | Login username (default from env `FNS_CREDENTIALS`) |
| `--password` | — | ❌ | Login password (default from env `FNS_PASSWORD`) |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `FNS_CREDENTIALS` | Login username |
| `FNS_PASSWORD` | Login password |
| `FNS_BASE_URL` | Service URL |

## Workflow

1. Read content (from file or `--content` argument)
2. Call `/api/user/login` to obtain JWT token
3. Compute `path` and `content` hashes using Java `String.hashCode()`
4. Call `/api/note` with token to write note
5. Output sync result

## Notes

- Remote paths are auto-created by the server — no manual directory creation needed
- Requests skip SSL certificate verification by default (for intranet self-signed certs)
- `pathHash` / `contentHash` use the Java `String.hashCode()` algorithm (multiply by 31, 32-bit signed integer)

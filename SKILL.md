---
name: markdown-to-fastnote
description: Push Markdown notes to the Fast-Note-Sync service for Obsidian sync. Use when the user says "sync notes to obsidian", "write to fast-note", "save to note service", or "markdown to fastnote".
---

# Markdown to FastNote

Push Markdown content to the Fast-Note-Sync service, which Obsidian can auto-sync.

## Use Cases

- User wants to sync a Markdown file to Obsidian
- User wants to write content to the note service
- Auto-sync after converting WeChat articles to Markdown

## Usage

```bash
python3 scripts/sync_note.py --file <local-file> --path <remote-path>
python3 scripts/sync_note.py --content "content" --path <remote-path>
```

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--file` / `-f` | One of two | Local Markdown file path |
| `--content` / `-c` | One of two | Pass text content directly |
| `--path` / `-p` | ✅ | Remote save path, e.g. `AI Study/test.md` |
| `--vault` / `-v` | ❌ | Vault name, default `note` |
| `--base-url` | ❌ | Service URL (default from env `FNS_BASE_URL`, fallback `http://192.168.100.106:9100`) |
| `--credentials` | ❌ | Login username (default from env `FNS_CREDENTIALS`) |
| `--password` | ❌ | Login password (default from env `FNS_PASSWORD`) |

## Examples

```bash
# Sync local file
python3 scripts/sync_note.py -f ./articles/test.md -p "AI Study/test.md"

# Write content directly
python3 scripts/sync_note.py -c "# Hello World" -p "test/hello.md"

# Specify vault
python3 scripts/sync_note.py -f note.md -p "daily/2024-01-01.md" -v myvault
```

## Workflow

1. Read content (from file or --content argument)
2. Call login API to obtain JWT token
3. Compute pathHash and contentHash (Java hashCode algorithm)
4. Call note API to write note
5. Output sync result

## Environment Variables

Set environment variables to avoid passing credentials in plaintext:

```bash
export FNS_CREDENTIALS="username"
export FNS_PASSWORD="password"
export FNS_BASE_URL="http://192.168.1.254:9100"
```

## Notes

- Remote directories are auto-created — no manual setup needed
- pathHash/contentHash use the Java String.hashCode() algorithm
- SSL certificate verification is skipped by default (intranet service)

# Markdown to FastNote

Push Markdown notes and images to the Fast-Note-Sync service for Obsidian auto-sync.

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

# Sync article with images as a folder
python3 scripts/sync_note.py -f ./article.md -p "AI Study/RAG/article.md" -i ./img1.png ./img2.png

# Auto-detect local image references in Markdown
python3 scripts/sync_note.py -f ./article.md -p "AI Study/RAG/article.md" --auto-images
```

## Parameters

| Parameter | Short | Required | Description |
|-----------|-------|----------|-------------|
| `--file` | `-f` | One of two | Local Markdown file path |
| `--content` | `-c` | One of two | Pass text content directly |
| `--path` | `-p` | ✅ | Remote save path, e.g. `AI Study/test.md` |
| `--images` | `-i` | ❌ | Image files to upload alongside note (space-separated) |
| `--auto-images` | — | ❌ | Auto-detect local image references in Markdown, upload them and rewrite paths to relative |
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
2. Collect images (`--images` or `--auto-images`)
3. Call `/api/user/login` to obtain JWT token
4. If images exist, convert path to folder structure and upload each image via `/api/file`
5. In `--auto-images` mode, rewrite image references in Markdown to relative paths
6. Call `/api/note` to write note
7. Output sync results

## Notes

- Remote paths are auto-created by the server — no manual directory creation needed
- Requests skip SSL certificate verification by default (for intranet self-signed certs)
- `pathHash` / `contentHash` use the Java `String.hashCode()` algorithm (multiply by 31, 32-bit signed integer)
- Articles with images are stored in folder form: `ArticleName/ArticleName.md` with images alongside
- File uploads use streaming reads, suitable for large files

---
name: markdown-to-fastnote
description: 将 Markdown 笔记推送到 Fast-Note-Sync 服务，供 Obsidian 同步。当用户说"同步笔记到 obsidian"、"写入 fast-note"、"保存到笔记服务"、"markdown to fastnote"时使用。
---

# Markdown to FastNote

将 Markdown 内容和图片推送到 Fast-Note-Sync 服务，Obsidian 可自动同步。

## 使用场景

- 用户想把某个 Markdown 文件同步到 Obsidian
- 用户想把一段内容写入笔记服务
- 用户想同步带图片的文章（图片与笔记放在同一目录）
- 微信文章转 Markdown 后自动同步

## 使用方法

```bash
# 同步笔记
python3 scripts/sync_note.py --file <本地文件> --path <远程路径>
python3 scripts/sync_note.py --content "内容" --path <远程路径>

# 同步带图片的文章（手动指定图片）
python3 scripts/sync_note.py --file <本地文件> --path "folder/article.md" --images ./img1.png ./img2.png

# 同步带图片的文章（自动识别 Markdown 中的本地图片引用）
python3 scripts/sync_note.py --file <本地文件> --path "folder/article.md" --auto-images
```

## 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `--file` / `-f` | 二选一 | 本地 Markdown 文件路径 |
| `--content` / `-c` | 二选一 | 直接传入文本内容 |
| `--path` / `-p` | ✅ | 远程保存路径，如 `AI Study/test.md` |
| `--images` / `-i` | ❌ | 要一起上传的图片文件，多个用空格分隔 |
| `--auto-images` | ❌ | 自动从 Markdown 内容中识别本地图片引用并上传，同时将引用路径替换为相对路径 |
| `--vault` / `-v` | ❌ | Vault 名称，默认 `note` |
| `--base-url` | ❌ | 服务地址（默认从环境变量 `FNS_BASE_URL` 读取，回退 `http://192.168.100.106:9100`） |
| `--credentials` | ❌ | 登录用户名（默认从环境变量 `FNS_CREDENTIALS` 读取） |
| `--password` | ❌ | 登录密码（默认从环境变量 `FNS_PASSWORD` 读取） |

## 示例

```bash
# 同步本地文件
python3 scripts/sync_note.py -f ./articles/test.md -p "AI Study/test.md"

# 直接写入内容
python3 scripts/sync_note.py -c "# Hello World" -p "test/hello.md"

# 指定 vault
python3 scripts/sync_note.py -f note.md -p "daily/2024-01-01.md" -v myvault

# 带图片的文章，手动指定图片
python3 scripts/sync_note.py -f ./article.md -p "AI Study/RAG/article.md" -i ./img1.png ./img2.png

# 带图片的文章，自动识别本地图片引用
python3 scripts/sync_note.py -f ./article.md -p "AI Study/RAG/article.md" --auto-images
```

## 工作流程

1. 读取内容（从文件或 --content 参数）
2. 收集图片（--images 指定 或 --auto-images 自动从 Markdown 提取）
3. 调用登录 API 获取 JWT token
4. 如果有图片，将图片上传到笔记的同级目录
5. 如果使用 --auto-images，自动将 Markdown 中的图片引用替换为相对路径（仅文件名）
6. 调用 note API 写入笔记
7. 输出同步结果

## 环境变量

```bash
export FNS_CREDENTIALS="username"
export FNS_PASSWORD="password"
export FNS_BASE_URL="http://192.168.1.254:9100"
```

## 注意事项

- 远程目录无需手动创建，服务端自动建
- pathHash/contentHash 使用 Java String.hashCode() 算法
- 默认跳过 SSL 证书验证（内网服务）
- 带图片的文章以文件夹形式存储：`文章名/文章名.md` + 图片文件
- 图片上传使用流式读取，支持大文件
- `--auto-images` 仅识别 `![alt](本地路径)` 格式的图片引用，网络 URL 会被忽略

# Markdown to FastNote

将 Markdown 笔记推送到 Fast-Note-Sync 服务，供 Obsidian 自动拉取。

> [English](README.md)

## 安装

```bash
pip install requests urllib3
```

## 快速开始

```bash
# 通过环境变量配置
export FNS_CREDENTIALS="your-username"
export FNS_PASSWORD="your-password"
export FNS_BASE_URL="http://192.168.1.254:9100"

# 同步本地文件
python3 scripts/sync_note.py -f ./articles/test.md -p "AI Study/test.md"

# 直接写入内容
python3 scripts/sync_note.py -c "# Hello World" -p "test/hello.md"

# 指定 vault（默认 note）
python3 scripts/sync_note.py -f note.md -p "daily/2024-01-01.md" -v myvault
```

## 参数

| 参数 | 简写 | 必填 | 说明 |
|------|------|------|------|
| `--file` | `-f` | 二选一 | 本地 Markdown 文件路径 |
| `--content` | `-c` | 二选一 | 直接传入文本内容 |
| `--path` | `-p` | ✅ | 远程保存路径，如 `AI Study/test.md` |
| `--vault` | `-v` | ❌ | Vault 名称，默认 `note` |
| `--base-url` | — | ❌ | 服务地址（默认从环境变量 `FNS_BASE_URL` 读取，回退 `http://192.168.100.106:9100`） |
| `--credentials` | — | ❌ | 登录用户名（默认从环境变量 `FNS_CREDENTIALS` 读取） |
| `--password` | — | ❌ | 登录密码（默认从环境变量 `FNS_PASSWORD` 读取） |

## 环境变量

| 变量 | 说明 |
|------|------|
| `FNS_CREDENTIALS` | 登录用户名 |
| `FNS_PASSWORD` | 登录密码 |
| `FNS_BASE_URL` | 服务地址 |

## 工作流程

1. 读取内容（从文件或 `--content` 参数）
2. 调用 `/api/user/login` 获取 JWT token
3. 对 `path` 和 `content` 分别计算 Java `String.hashCode()`
4. 携带 token 调用 `/api/note` 写入笔记
5. 输出同步结果

## 注意事项

- 远程路径无需手动创建，服务端自动建目录
- 请求默认跳过 SSL 证书验证（适配内网自签名证书）
- `pathHash` / `contentHash` 使用 Java `String.hashCode()` 算法（乘 31、32 位有符号整数）

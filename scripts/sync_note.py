#!/usr/bin/env python3
"""
Fast Note Sync - 将 Markdown 笔记和文件同步到 fast-note-sync 服务（Obsidian 可同步）

用法:
    python sync_note.py --file <markdown文件路径> --path <远程路径>
    python sync_note.py --content "内容" --path <远程路径>
    python sync_note.py --file ./article.md --path "folder/article.md" --images ./img1.png ./img2.png
    python sync_note.py --file ./article.md --path "folder/article.md" --auto-images

示例:
    python sync_note.py --file ./note.md --path "AI Study/test.md"
    python sync_note.py --content "# Hello" --path "test/hello.md"
    python sync_note.py -f ./article.md -p "AI Study/RAG/article.md" -i ./img1.png ./img2.png
    python sync_note.py -f ./article.md -p "AI Study/RAG/article.md" --auto-images
"""

import argparse
import json
import mimetypes
import os
import re
import sys
import time
import requests
import urllib3

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 默认配置
DEFAULT_BASE_URL = os.environ.get("FNS_BASE_URL", "http://192.168.1.254:9100")
DEFAULT_CREDENTIALS = os.environ.get("FNS_CREDENTIALS", "test")
DEFAULT_PASSWORD = os.environ.get("FNS_PASSWORD", "test")


def java_hashcode(s: str) -> int:
    """计算 Java 风格的 String.hashCode()（32位有符号整数）"""
    h = 0
    for c in s:
        h = (31 * h + ord(c)) & 0xFFFFFFFF
    # 转为有符号32位
    if h >= 0x80000000:
        h -= 0x100000000
    return h


def login(base_url: str, credentials: str, password: str) -> str:
    """登录获取 token"""
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

    # 尝试从常见字段提取 token
    token = None
    if isinstance(data, dict):
        token = data.get("token") or data.get("accessToken") or data.get("data", {}).get("token") if isinstance(data.get("data"), dict) else None
        if not token and isinstance(data.get("data"), str):
            token = data["data"]

    if not token:
        print(f"❌ 登录失败，响应: {json.dumps(data, ensure_ascii=False)}", file=sys.stderr)
        sys.exit(1)

    return token


def sync_note(
    base_url: str,
    token: str,
    vault: str,
    path: str,
    content: str,
) -> dict:
    """同步笔记到 fast-note-sync"""
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


def upload_file(
    base_url: str,
    token: str,
    vault: str,
    path: str,
    file_path: str,
) -> dict:
    """上传文件（图片等）到 fast-note-sync"""
    timestamp = str(int(time.time() * 1000))
    url = f"{base_url}/api/file?_={timestamp}&lang=zh-CN"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
        "Authorization": f"Bearer {token}",
        "X-Client": "WebGui",
    }

    # 获取文件时间戳（毫秒）
    stat = os.stat(file_path)
    ctime_ms = str(int(stat.st_ctime * 1000))
    mtime_ms = str(int(stat.st_mtime * 1000))

    # 推断 MIME 类型
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type is None:
        mime_type = "application/octet-stream"

    filename = os.path.basename(file_path)

    with open(file_path, "rb") as f:
        files = {
            "file": (filename, f, mime_type),
        }
        data = {
            "vault": vault,
            "path": path,
            "ctime": ctime_ms,
            "mtime": mtime_ms,
        }
        resp = requests.post(url, headers=headers, files=files, data=data, verify=False, timeout=60)

    resp.raise_for_status()
    return resp.json()


def _get_image_paths_from_content(content: str) -> list[str]:
    """从 Markdown 内容中提取本地图片引用路径"""
    images = []
    # 匹配 ![alt](path) 格式
    for match in re.finditer(r'!\[.*?\]\(([^)]+)\)', content):
        image_path = match.group(1)
        images.append(image_path)
    return images


def main():
    parser = argparse.ArgumentParser(description="同步 Markdown 笔记到 fast-note-sync 服务")
    parser.add_argument("--file", "-f", help="Markdown 文件路径")
    parser.add_argument("--content", "-c", help="直接传入内容（与 --file 二选一）")
    parser.add_argument("--vault", "-v", default="note", help="Vault 名称（默认: note）")
    parser.add_argument("--path", "-p", required=True, help="远程保存路径，如 'AI Study/test.md'")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="服务地址")
    parser.add_argument("--credentials", default=DEFAULT_CREDENTIALS, help="登录用户名")
    parser.add_argument("--password", default=DEFAULT_PASSWORD, help="登录密码")
    parser.add_argument("--images", "-i", nargs="*", default=None, help="要一起上传的图片文件（多个用空格分隔）")
    parser.add_argument("--auto-images", action="store_true", help="自动从 Markdown 内容中识别本地图片引用并上传")

    args = parser.parse_args()

    # 获取内容
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            content = f.read()
    elif args.content:
        content = args.content
    else:
        print("❌ 请指定 --file 或 --content", file=sys.stderr)
        sys.exit(1)

    # 收集待上传的图片
    image_files = list(args.images) if args.images else []

    if args.auto_images:
        # 从 Markdown 内容中提取本地图片路径
        for img_path in _get_image_paths_from_content(content):
            if os.path.isfile(img_path) and img_path not in image_files:
                image_files.append(img_path)

    has_images = len(image_files) > 0

    # 登录
    print(f"🔐 登录 {args.base_url} ...")
    token = login(args.base_url, args.credentials, args.password)
    print(f"✅ 登录成功，获取 token")

    # 带图片时，图片放到笔记的同级目录
    if has_images:
        note_dir = os.path.dirname(args.path)
        note_path = args.path

        # 上传图片到笔记同级目录
        for img_path in image_files:
            img_filename = os.path.basename(img_path)
            img_remote_path = f"{note_dir}/{img_filename}" if note_dir else img_filename
            print(f"🖼️  上传图片 {img_filename} → {args.vault}/{img_remote_path} ...")
            result = upload_file(args.base_url, token, args.vault, img_remote_path, img_path)
            print(f"   ✅ 图片上传成功")

        # 调整 Markdown 中的图片引用为相对路径（同目录，直接用文件名）
        if args.file and args.auto_images:
            for img_file in image_files:
                img_filename = os.path.basename(img_file)
                content = re.sub(
                    rf'!\[([^\]]*)\]\({re.escape(img_file)}\)',
                    rf'![\1]({img_filename})',
                    content
                )
    else:
        note_path = args.path

    # 同步笔记
    print(f"📝 同步笔记 → {args.vault}/{note_path} ...")
    result = sync_note(args.base_url, token, args.vault, note_path, content)
    print(f"✅ 同步成功！")
    print(f"   响应: {json.dumps(result, ensure_ascii=False, indent=2)}")


if __name__ == "__main__":
    main()

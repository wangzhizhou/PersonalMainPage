#!/usr/bin/env python3
"""解析当前仓库实际使用的站点地址。

优先级：
    1. 环境变量 SITE_URL / SITE_CNAME
    2. GitHub Pages API 中配置的 custom domain / html_url
    3. gh-pages 分支中的 CNAME 文件
    4. GitHub Pages 默认地址（<owner>.github.io/<repo>/）

用法:
    python3 scripts/resolve_site_url.py
    python3 scripts/resolve_site_url.py --cname
    python3 scripts/resolve_site_url.py --json
    python3 scripts/resolve_site_url.py --tsv
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from urllib.parse import urlsplit

API_ROOT = "https://api.github.com"


def git_remote_repo() -> str | None:
    try:
        remote = subprocess.check_output(
            ["git", "remote", "get-url", "origin"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return None

    match = re.search(r"github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?$", remote)
    if not match:
        return None
    return f"{match.group(1)}/{match.group(2)}"


def repo_slug(explicit: str | None) -> str:
    if explicit:
        return explicit.strip().strip("/")

    env_repo = os.environ.get("GITHUB_REPOSITORY", "").strip()
    if env_repo:
        return env_repo

    repo = git_remote_repo()
    if repo:
        return repo

    raise RuntimeError("无法确定 GitHub 仓库，请设置 GITHUB_REPOSITORY 或使用 --repo")


def github_token() -> str | None:
    for key in ("GITHUB_TOKEN", "GH_TOKEN"):
        token = os.environ.get(key, "").strip()
        if token:
            return token

    try:
        token = subprocess.check_output(
            ["gh", "auth", "token"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        return token or None
    except Exception:
        return None


def fetch_pages_config(repo: str, token: str | None):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "jokerhub-site-resolver",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = urllib.request.Request(f"{API_ROOT}/repos/{repo}/pages", headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.load(response), None
    except urllib.error.HTTPError as error:
        return None, error.code
    except Exception as error:  # noqa: BLE001 - 网络异常统一降级处理
        print(f"[site] 读取 GitHub Pages 配置失败: {error}", file=sys.stderr)
        return None, None


def normalize_url(url: str, cname: str = "") -> tuple[str, str]:
    cname = cname.strip()
    if cname:
        host = re.sub(r"^https?://", "", cname).strip().strip("/")
        return f"https://{host}/", host

    url = url.strip()
    if not url:
        return "", ""

    parsed = urlsplit(url if "://" in url else f"https://{url}")
    scheme = parsed.scheme if parsed.scheme in ("http", "https") else "https"
    path = parsed.path.rstrip("/")
    return f"{scheme}://{parsed.netloc}{path}/", ""


def host_from_url(url: str) -> str:
    parsed = urlsplit(url)
    return (parsed.hostname or "").strip()


def is_default_pages_host(host: str) -> bool:
    return host.endswith(".github.io")


def default_pages_url(repo: str) -> str:
    owner, name = repo.split("/", 1)
    owner = owner.lower()
    if name.lower() == f"{owner}.github.io":
        return f"https://{owner}.github.io/"
    return f"https://{owner}.github.io/{name}/"


def gh_pages_cname() -> str:
    for ref in ("origin/gh-pages", "gh-pages"):
        try:
            value = subprocess.check_output(
                ["git", "show", f"{ref}:CNAME"],
                text=True,
                stderr=subprocess.DEVNULL,
            ).strip()
        except Exception:
            continue
        if value:
            return value
    return ""


def resolve(repo: str) -> dict[str, str]:
    env_url = os.environ.get("SITE_URL", "").strip()
    env_cname = os.environ.get("SITE_CNAME", "").strip()
    if env_url or env_cname:
        url, cname = normalize_url(env_url, env_cname)
        if not cname:
            host = host_from_url(url)
            if host and not is_default_pages_host(host):
                cname = host
        return {"url": url, "cname": cname, "source": "environment"}

    token = github_token()
    pages, status = fetch_pages_config(repo, token)

    if pages is not None:
        cname = (pages.get("cname") or "").strip()
        html_url = (pages.get("html_url") or "").strip()
        if cname:
            url, cname = normalize_url("", cname)
            return {"url": url, "cname": cname, "source": "pages-api"}
        if html_url:
            url, cname = normalize_url(html_url)
            if not cname:
                host = host_from_url(url)
                if host and not is_default_pages_host(host):
                    cname = host
            return {"url": url, "cname": cname, "source": "pages-api"}

    # 认证失败通常意味着 token 权限不足；此时继续猜测域名风险很大。
    if token and status in (401, 403, 500, 502, 503, 504):
        raise RuntimeError(
            f"GitHub Pages API 请求失败（HTTP {status}），请检查 GITHUB_TOKEN 的 pages: read 权限，"
            "或通过 SITE_URL / SITE_CNAME 显式指定站点域名"
        )

    cname = gh_pages_cname()
    if cname:
        url, cname = normalize_url("", cname)
        return {"url": url, "cname": cname, "source": "gh-pages-cname"}

    return {"url": default_pages_url(repo), "cname": "", "source": "default-pages"}


def main() -> int:
    parser = argparse.ArgumentParser(description="解析当前仓库的站点地址")
    parser.add_argument("--repo", help="GitHub 仓库，格式 owner/repo；默认从 CI 环境或 git remote 推断")
    parser.add_argument("--cname", action="store_true", help="只输出自定义域名")
    parser.add_argument("--json", action="store_true", help="输出 JSON")
    parser.add_argument("--tsv", action="store_true", help="输出 URL<TAB>CNAME")
    args = parser.parse_args()

    try:
        result = resolve(repo_slug(args.repo))
    except Exception as error:  # noqa: BLE001 - CLI 统一输出错误
        print(f"[site] {error}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result, ensure_ascii=False))
    elif args.tsv:
        print(f"{result['url']}\t{result['cname']}")
    elif args.cname:
        print(result["cname"])
    else:
        print(result["url"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

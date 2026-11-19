#!/usr/bin/env python3
"""列出 GitHub 账号 / 组织下带产品页的仓库，便于维护产品全览数据。

用法:
    python3 scripts/sync_github_products.py
    python3 scripts/sync_github_products.py --json
    GITHUB_TOKEN=ghp_xxx python3 scripts/sync_github_products.py

说明:
    - 默认检查 wangzhizhou、EasyIndie、OrzMC、OrzGeeker 四个来源。
    - 只列出 has_pages 为真或填写了 homepage 的仓库。
    - 输出的是候选清单，最终展示内容维护在 Orz/data/showcase.yaml。
    - 未认证请求受 GitHub API 速率限制，必要时设置 GITHUB_TOKEN。
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

DEFAULT_OWNERS = ["wangzhizhou", "EasyIndie", "OrzMC", "OrzGeeker"]
API_ROOT = "https://api.github.com"


def api_get(url: str):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "jokerhub-showcase-sync",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response), response.headers
    except urllib.error.HTTPError as error:
        print(f"GitHub API 请求失败: {url} -> HTTP {error.code}", file=sys.stderr)
        raise


def owner_repos(owner: str):
    info, _ = api_get(f"{API_ROOT}/users/{owner}")
    endpoint = "orgs" if info.get("type") == "Organization" else "users"

    repos = []
    page = 1
    while True:
        url = (
            f"{API_ROOT}/{endpoint}/{owner}/repos"
            f"?per_page=100&page={page}&sort=updated&type=public"
        )
        data, _ = api_get(url)
        if not data:
            break
        repos.extend(data)
        if len(data) < 100:
            break
        page += 1
    return repos


def collect(owners):
    rows = []
    for owner in owners:
        for repo in owner_repos(owner):
            homepage = (repo.get("homepage") or "").strip()
            if not (repo.get("has_pages") or homepage):
                continue

            pages_url = f"https://{owner.lower()}.github.io/{repo['name']}/"
            rows.append(
                {
                    "owner": owner,
                    "repo": repo["name"],
                    "product_page": homepage or pages_url,
                    "fallback_pages": "" if homepage else pages_url,
                    "github": repo["html_url"],
                    "description": repo.get("description") or "",
                    "fork": repo.get("fork", False),
                    "archived": repo.get("archived", False),
                    "updated": (repo.get("pushed_at") or "")[:10],
                }
            )
    return rows


def print_table(rows):
    header = f"{'OWNER/REPO':38} {'PAGE':52} FLAGS"
    print(header)
    print("-" * len(header))
    for row in rows:
        name = f"{row['owner']}/{row['repo']}"
        page = row["product_page"]
        flags = []
        if row["fork"]:
            flags.append("fork")
        if row["archived"]:
            flags.append("archived")
        print(f"{name:38} {page:52} {','.join(flags)}")
        if row["description"]:
            print(f"{'':38} {row['description']}")


def main():
    parser = argparse.ArgumentParser(description="收集 GitHub 上带产品页的仓库")
    parser.add_argument(
        "--owner",
        action="append",
        dest="owners",
        help="GitHub 账号或组织，可重复指定；默认检查四个已知来源",
    )
    parser.add_argument("--json", action="store_true", help="以 JSON 输出")
    args = parser.parse_args()

    owners = args.owners or DEFAULT_OWNERS
    rows = collect(owners)

    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
    else:
        print_table(rows)
        print(f"\n共 {len(rows)} 个带产品页的仓库，来源：{', '.join(owners)}")


if __name__ == "__main__":
    main()

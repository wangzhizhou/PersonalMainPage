#!/usr/bin/env bash
# -*- coding: utf-8 -*-
#
# 本地一键发布：构建 Hugo 站点并推送到 gh-pages 分支。
# 在 CI 环境中只负责构建，部署由 GitHub Actions 完成。
#
# 用法:
#   ./publish_site.sh

set -euo pipefail

cd "$(dirname "$0")"

PUBLIC_DIR="Orz/public"
DEPLOY_DIR=".deploy/gh-pages"

if ! command -v hugo >/dev/null 2>&1; then
  echo "未找到 hugo，请先安装：https://gohugo.io/installation/" >&2
  exit 1
fi

if [ -z "${CI:-}" ] && [ -n "$(git status --porcelain)" ]; then
  echo "工作区有未提交的改动，请先提交后再发布。" >&2
  exit 1
fi

echo "==> 同步主题子模块"
git submodule update --init --recursive

echo "==> 同步 gh-pages 参考"
git fetch origin gh-pages:refs/remotes/origin/gh-pages --depth=1 || true

echo "==> 构建站点"
./scripts/build_site.sh

if [ -n "${CI:-}" ]; then
  echo "==> CI 环境：构建完成，部署交给 GitHub Actions"
  exit 0
fi

echo "==> 准备 gh-pages 工作树"
git fetch origin gh-pages || true
git worktree remove --force "${DEPLOY_DIR}" 2>/dev/null || true
rm -rf "${DEPLOY_DIR}"
if git rev-parse --verify --quiet origin/gh-pages >/dev/null; then
  git worktree add --force -B gh-pages "${DEPLOY_DIR}" origin/gh-pages
else
  git worktree add --force -B gh-pages "${DEPLOY_DIR}"
fi

trap 'git worktree remove --force "${DEPLOY_DIR}" 2>/dev/null || true' EXIT INT TERM

# 用最新构建结果覆盖工作树内容（保留 .git）
find "${DEPLOY_DIR}" -mindepth 1 -maxdepth 1 ! -name .git -exec rm -rf {} +
cp -R "${PUBLIC_DIR}/." "${DEPLOY_DIR}/"

echo "==> 提交并推送"
if [ -z "$(git -C "${DEPLOY_DIR}" status --porcelain)" ]; then
  echo "站点内容没有变化，无需发布。"
else
  git -C "${DEPLOY_DIR}" add --all
  git -C "${DEPLOY_DIR}" commit -m "deploy: $(date '+%Y-%m-%d %H:%M:%S')"
  git push origin gh-pages
  if [ -f "${PUBLIC_DIR}/CNAME" ]; then
    echo "==> 发布完成：https://$(cat "${PUBLIC_DIR}/CNAME")"
  else
    echo "==> 发布完成：当前仓库未配置自定义域名"
  fi
fi

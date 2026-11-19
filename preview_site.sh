#!/usr/bin/env bash
# -*- coding: utf-8 -*-
#
# 本地预览：启动 Hugo 开发服务器并自动打开浏览器。
#
# 用法:
#   ./preview_site.sh            # http://localhost:1313
#   PORT=8080 ./preview_site.sh  # 指定端口

set -euo pipefail

cd "$(dirname "$0")"

PORT="${PORT:-1313}"

if ! command -v hugo >/dev/null 2>&1; then
  echo "未找到 hugo，请先安装：https://gohugo.io/installation/" >&2
  exit 1
fi

echo "==> 同步主题子模块"
git submodule update --init --recursive

echo "==> 启动预览：http://localhost:${PORT}（Ctrl+C 退出）"
hugo --source Orz server \
  --buildDrafts \
  --port "${PORT}" \
  --bind 127.0.0.1 \
  --baseURL "http://localhost:${PORT}/" &
SERVER_PID=$!

cleanup() {
  kill "${SERVER_PID}" 2>/dev/null || true
  wait "${SERVER_PID}" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

sleep 2
if command -v open >/dev/null 2>&1; then
  open "http://localhost:${PORT}"
elif command -v xdg-open >/dev/null 2>&1; then
  xdg-open "http://localhost:${PORT}" >/dev/null 2>&1 || true
fi

wait "${SERVER_PID}"

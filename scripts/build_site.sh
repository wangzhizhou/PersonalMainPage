#!/usr/bin/env bash
# 构建生产站点。
#
# 站点域名不写死在仓库里：
#   1. 优先使用 SITE_URL / SITE_CNAME 环境变量
#   2. 其次读取 GitHub Pages 仓库设置中的自定义域名
#   3. 再次读取 gh-pages 分支中的 CNAME
#   4. 最后回退到 <owner>.github.io/<repo>/
#
# 用法:
#   ./scripts/build_site.sh
#   SITE_URL=https://example.com/ ./scripts/build_site.sh

set -euo pipefail

cd "$(dirname "$0")/.."

if ! command -v python3 >/dev/null 2>&1; then
  echo "未找到 python3，无法解析站点域名。" >&2
  exit 1
fi

if [ -n "${GITHUB_ENV:-}" ]; then
  # CI 中先刷新 gh-pages 参考，供 API 不可用时回退读取 CNAME
  git fetch origin gh-pages:refs/remotes/origin/gh-pages --depth=1 >/dev/null 2>&1 || true
fi

site_json="$(python3 scripts/resolve_site_url.py --json)"
site_url="$(python3 -c 'import json,sys; print(json.load(sys.stdin)["url"])' <<<"${site_json}")"
site_cname="$(python3 -c 'import json,sys; print(json.load(sys.stdin)["cname"])' <<<"${site_json}")"
site_source="$(python3 -c 'import json,sys; print(json.load(sys.stdin)["source"])' <<<"${site_json}")"

echo "==> 站点地址: ${site_url}（来源: ${site_source}）"

rm -rf Orz/public
hugo --source Orz \
  --environment production \
  --baseURL "${site_url}" \
  --minify \
  --gc \
  "$@"

if [ -n "${site_cname}" ]; then
  printf '%s\n' "${site_cname}" > Orz/public/CNAME
  echo "==> CNAME: ${site_cname}"
else
  echo "==> 当前仓库未配置自定义域名，不生成 CNAME"
fi

if [ -n "${GITHUB_ENV:-}" ]; then
  {
    echo "SITE_URL=${site_url}"
    echo "SITE_CNAME=${site_cname}"
  } >> "${GITHUB_ENV}"
fi

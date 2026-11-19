# PersonalMainPage · JokerHub

王志舟（Joker）的个人主页，同时作为个人产品与项目的展示入口。

站点使用 [Hugo](https://gohugo.io/) + [Personal Web](https://github.com/bjacquemet/personal-web) 主题构建，最终以纯静态页面的形式部署在 GitHub Pages 上。

- 线上域名：构建时自动读取仓库 **Settings → Pages** 的自定义域名；未配置时使用 `<owner>.github.io/<repo>/`
- 备案信息：京ICP备18007462号-2

## 页面结构

首页由三部分组成，全部由数据驱动，改内容不需要动模板：

1. **个人 Hero**：姓名、一句话介绍、技术栈与行动按钮
2. **产品与项目**：读取 `Orz/data/products.yaml` 自动生成产品卡片
3. **关于本站 / 最新文章**：站点简介与博客文章列表（有文章时自动出现）

此外还有：

- `/products/`：产品与项目全览，汇总个人账号与各组织下有产品页的项目，含功能要点与外链
- `/about/`：个人简介与产品清单
- `/post/`：博客列表
- `/404.html`：404 页面（会带出最新一篇文章）

## 目录说明

```
.
├── Orz/                        # Hugo 站点根目录
│   ├── config.toml             # 站点配置（信息、菜单、侧边栏、社交链接）
│   ├── content/                # 页面内容（Markdown）
│   ├── data/
│   │   ├── products.yaml       # 首页精选产品数据
│   │   └── showcase.yaml       # 产品全览页数据（分组 / 功能 / 外链）
│   ├── layouts/                # 项目级模板，会覆盖主题同名模板
│   │   ├── index.html          # 首页布局
│   │   ├── products/list.html  # 产品全览页布局
│   │   ├── partials/home/      # 首页 Hero 与产品卡片
│   │   ├── partials/products/  # 产品全览卡片
│   │   ├── partials/head/      # SEO / meta 信息
│   │   └── shortcodes/         # 兼容新版 Hugo 的短代码覆盖
│   ├── static/
│   │   ├── css/custom.css      # 首页、产品卡片与产品全览页样式
│   │   ├── js/main.js          # 移动端菜单交互
│   │   └── images/             # 图片资源
│   └── themes/personal/        # 主题子模块，不要直接修改
├── scripts/
│   ├── build_site.sh           # 解析域名并构建生产站点
│   ├── resolve_site_url.py     # 从 Pages 配置 / CNAME 解析站点地址
│   └── sync_github_products.py # 收集 GitHub 上带产品页的仓库
├── preview_site.sh             # 本地预览
├── publish_site.sh             # 本地一键发布到 gh-pages
└── .github/workflows/hugo.yml  # GitHub Actions 自动构建与部署
```

## 本地开发

依赖：

- Hugo extended ≥ 0.156（CI 固定使用 `0.165.0`）
- Git（用于拉取主题子模块）

```bash
# 首次拉取代码后初始化主题
git submodule update --init --recursive

# 启动本地预览（自动打开浏览器）
./preview_site.sh

# 或指定端口
PORT=8080 ./preview_site.sh
```

预览地址：<http://localhost:1313>

只构建不启动服务：

```bash
./scripts/build_site.sh
# 站点地址与 CNAME 会根据 GitHub Pages 配置自动解析
# 产物位于 Orz/public/
```

> 仓库里不再写死站点域名。生产构建必须使用 `scripts/build_site.sh`，它会自动解析当前仓库实际配置的域名。

## 维护产品展示

产品相关数据分两层：首页只展示精选产品，完整清单放在产品全览页。

### 首页精选产品

编辑 `Orz/data/products.yaml`，新增一条记录即可出现在首页：

```yaml
- name: 产品名称
  tagline: 一句话介绍
  description: 详细介绍
  url: https://example.com
  icon: "🚀"          # 卡片图标（emoji）
  category: App      # App / 站点 / 内容 ...
  status: 已上架      # 可选状态标签
  tags: ["Swift", "iOS"]
  featured: true     # 是否在首页展示
```

字段含义见文件顶部注释。产品卡片的链接均以新窗口打开。

### 产品全览页

`/products/` 页面读取 `Orz/data/showcase.yaml`，按个人账号与组织分组展示：

- `groups`：来源分组，包含名称、图标、简介、官网与 GitHub 地址
- `products`：产品和项目，包含状态、简介、功能要点、标签与多个外链
- `links`：每个产品的外链入口，`primary: true` 会显示为高亮主按钮

新增产品时，在对应 `group.products` 下追加记录；新增组织时在 `groups` 下追加一个分组。修改后运行 `./preview_site.sh` 即可预览。

### 同步 GitHub 产品清单

`scripts/sync_github_products.py` 会扫描个人账号和各组织下所有带 `homepage` 或 GitHub Pages 的仓库：

```bash
python3 scripts/sync_github_products.py

# 查看 JSON，便于脚本处理
python3 scripts/sync_github_products.py --json

# 遇到 API 速率限制时指定 token
GITHUB_TOKEN=ghp_xxx python3 scripts/sync_github_products.py
```

输出会标记 `fork` 与 `archived` 仓库，便于判断哪些适合收进产品全览页。脚本只负责收集候选，最终展示内容仍以 `showcase.yaml` 的人工整理为准。

## 域名解析

仓库不再写死主站域名。每次生产构建时，`scripts/build_site.sh` 会按以下优先级解析：

1. 环境变量 `SITE_URL` / `SITE_CNAME`
2. GitHub Pages API 中当前仓库配置的 custom domain / html_url
3. `gh-pages` 分支中的 `CNAME`
4. GitHub Pages 默认地址 `<owner>.github.io/<repo>/`

解析逻辑位于 `scripts/resolve_site_url.py`。CI 使用 `GITHUB_TOKEN` 的 `pages: read` 权限读取仓库 Pages 配置；本地发布会通过已登录的 `gh` CLI 获取 token。

检查当前会使用的地址：

```bash
python3 scripts/resolve_site_url.py --json
```

如需临时覆盖，也可以在 GitHub 仓库的 **Variables** 中设置 `SITE_URL` / `SITE_CNAME`，或使用环境变量：

构建时会自动：

- 将解析出的地址作为 Hugo `--baseURL`
- 若配置了自定义域名，生成 `Orz/public/CNAME`
- 若没有自定义域名，则不生成 CNAME，使用 GitHub Pages 默认地址

临时覆盖域名：

```bash
SITE_URL=https://example.com/ ./scripts/build_site.sh
```

## 自动化流程

### GitHub Actions（推荐）

工作流文件：`.github/workflows/hugo.yml`

- **push 到 `main`**：构建站点 → 部署到 `gh-pages` 分支（`force_orphan`，保持分支干净）
- **Pull Request**：只构建并检查产物，不部署，用于提前发现构建错误
- **手动触发**：Actions 页面 `Run workflow`
- 只在 `Orz/**`、发布脚本或工作流本身变化时触发
- 使用 `concurrency` 取消同一分支上的重复构建

部署完成后 GitHub Pages 会自动更新为仓库 **Settings → Pages** 中配置的域名。

> 首次配置时，需要在仓库 **Settings → Pages** 中选择 `Deploy from a branch`，分支为 `gh-pages`，目录为 `/ (root)`。

### 本地发布

```bash
./publish_site.sh
```

脚本会：

1. 检查工作区是否干净
2. 同步主题子模块，并解析当前 Pages 域名
3. 重新构建 `Orz/public`，按需生成 `CNAME`
4. 将 `Orz/public` 同步到 `.deploy/gh-pages` 工作树
5. 提交并推送到 `gh-pages` 分支

> 注意：本地发布要求工作区没有未提交改动；CI 环境中脚本只执行构建。

## 常见修改

| 需求 | 位置 |
| --- | --- |
| 修改姓名、简介、技术栈 | `Orz/config.toml` 的 `[params.intro]`、`[params.home]` |
| 增删首页精选产品 | `Orz/data/products.yaml` |
| 增删产品全览内容 | `Orz/data/showcase.yaml` |
| 同步 GitHub 产品候选 | `python3 scripts/sync_github_products.py` |
| 修改侧边栏菜单 / 社交链接 | `Orz/config.toml` 的 `[menu.main]`、`[params.social]` |
| 修改首页样式 | `Orz/static/css/custom.css` |
| 修改域名 | GitHub **Settings → Pages → Custom domain**；构建时自动读取，无需改代码 |
| 临时覆盖域名 | `SITE_URL=https://example.com/ ./scripts/build_site.sh` |
| 修改备案信息 | `Orz/layouts/partials/footer.html` 与 `config.toml` |

## 技术说明

- 主题通过 Git submodule 引入；自定义样式和模板都放在项目目录中覆盖，升级主题不会丢失。
- 主题原 `tweet-single` 短代码使用了已移除的 `getJSON`，项目内已用 `resources.GetRemote` 覆盖实现，因此可以跟随新版 Hugo。
- 站点构建无需 Node.js，产物为纯静态文件。

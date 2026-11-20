# PersonalMainPage · JokerHub

王志舟（Joker）的个人主页，同时作为个人产品与项目的展示入口。

站点使用 [Hugo](https://gohugo.io/) + [PaperMod](https://github.com/adityatelange/hugo-PaperMod) 构建，产品展示为主，博客为辅，最终以纯静态页面的形式部署在 GitHub Pages 上。

- 线上域名：构建时自动读取仓库 **Settings → Pages** 的自定义域名；未配置时使用 `<owner>.github.io/<repo>/`
- 备案信息：京ICP备18007462号-2

## 设计方向

- **产品优先**：首页只保留个人介绍、6 个精选产品、简历入口和文章入口
- **低信息密度**：产品页按组织折叠，功能详情再按产品折叠
- **博客为辅**：保留 `/post/` 文章入口，但不再是站点主结构
- **简历托管**：`/resume/` 提供网页简历、PDF 下载与打印导出
- **现代视觉**：PaperMod 提供顶部导航、深浅色切换、响应式布局和 SEO 基础
- **中文友好**：系统字体栈 + 16px 正文，避免依赖 Google Fonts
- **可维护**：产品数据与视觉层分离，改内容不需要改模板

## 页面结构

- `/`：Hero 个人介绍、6 个精选产品、最近文章（有文章时出现）
- `/products/`：产品与项目全览，按组织分组；默认展开第一组，功能详情再按产品折叠
- `/resume/`：网页简历，支持下载 PDF 或打印导出
- `/about/`：个人简介与产品清单
- `/post/`：文章列表（博客为辅）
- `/404.html`：自定义 404 页面

## 目录说明

```
.
├── Orz/                          # Hugo 站点根目录
│   ├── config.toml               # 站点配置（PaperMod 参数、菜单、社交链接）
│   ├── content/                  # 页面内容（Markdown）
│   │   ├── about.md              # 关于我
│   │   ├── resume.md             # 简历页入口（type: resume）
│   │   ├── products/_index.md    # 产品全览页内容
│   │   └── post/_index.md        # 文章索引
│   ├── data/
│   │   ├── products.yaml         # 首页精选产品数据
│   │   ├── resume.yaml           # 简历内容（技能 / 项目 / 链接）
│   │   └── showcase.yaml         # 产品全览页数据（分组 / 功能 / 外链）
│   ├── assets/css/extended/
│   │   └── custom.css            # 自定义设计系统与组件样式
│   ├── layouts/
│   │   ├── index.html            # 自定义首页布局
│   │   ├── 404.html              # 自定义 404
│   │   ├── products/list.html    # 产品全览页布局
│   │   ├── resume/single.html    # 简历页布局与打印样式
│   │   ├── _partials/
│   │   │   └── extend_footer.html # 自定义页脚
│   │   └── partials/
│   │       ├── icon.html         # Lucide 内联 SVG 图标映射
│   │       ├── home/             # 首页 Hero 与产品卡片
│   │       └── products/         # 产品全览卡片
│   ├── static/
│   │   ├── icons/                # Lucide 图标许可证
│   │   ├── images/               # 头像、favicon、备案图标
│   │   └── resume/               # 简历 PDF
│   └── themes/PaperMod/          # 主题子模块，不要直接修改
├── scripts/
│   ├── build_site.sh             # 解析域名并构建生产站点
│   ├── resolve_site_url.py       # 从 Pages 配置 / CNAME 解析站点地址
│   └── sync_github_products.py   # 收集 GitHub 上带产品页的仓库
├── preview_site.sh               # 本地预览
├── publish_site.sh               # 本地一键发布到 gh-pages
└── .github/workflows/hugo.yml    # GitHub Actions 自动构建与部署
```

## 本地开发

依赖：

- Hugo extended ≥ 0.158（PaperMod 最低要求，CI 固定使用 `0.165.0`）
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

## 简历托管

简历页地址：<https://profile.jokerhub.cn/resume/>

- 页面内容在 `Orz/data/resume.yaml`，修改技能、项目、链接即可
- 页面布局在 `Orz/layouts/resume/single.html`
- PDF 文件放在 `Orz/static/resume/wangzhizhou-resume.pdf`
- 构建时如果 PDF 存在，会自动显示「下载 PDF」按钮；不存在时仍可用「打印 / 导出 PDF」

更新简历后重新生成 PDF：

```bash
# 1. 使用线上域名构建，保证 PDF 内部链接指向正式站点
./scripts/build_site.sh

# 2. 启动本地静态服务
python3 -m http.server 8080 --directory Orz/public

# 3. 打开 http://localhost:8080/resume/
#    点击「打印 / 导出 PDF」，在打印对话框中选择「存储为 PDF」
#    将文件覆盖保存到 Orz/static/resume/wangzhizhou-resume.pdf

# 4. 重新构建，把新 PDF 同步到产物目录
./scripts/build_site.sh
```

打印样式会自动隐藏导航、页脚和按钮，按 A4 单页排版输出。

## 图标

产品与项目图标使用 [Lucide](https://lucide.dev/) 的内联 SVG，不依赖系统 emoji，因此在 macOS、Windows、Linux 和移动端显示一致。

- 图标名写在 `Orz/data/products.yaml` 和 `Orz/data/showcase.yaml` 的 `icon` 字段
- 图标路径映射在 `Orz/layouts/partials/icon.html`
- Lucide 图标使用 ISC License，部分源自 Feather 的图标为 MIT；完整许可证见 `Orz/static/icons/LICENSE.txt`
- 未找到图标名时会回退到 `package`

新增图标时，从 Lucide 复制 SVG 内部的路径节点，追加到 `icon.html` 的 `$icons` 字典即可；不需要引入外部图标库或字体。

## 主题与样式

主题通过 Git submodule 引入：

```text
Orz/themes/PaperMod
```

PaperMod 负责：

- 顶部导航与菜单
- 深浅色主题切换
- 博客列表与文章页
- SEO、RSS、sitemap、搜索基础

站点自己的设计系统位于：

```text
Orz/assets/css/extended/custom.css
```

主要覆盖：

- PaperMod 的宽度、颜色、圆角、字体变量
- 首页 Hero、产品卡片、产品全览页
- 顶部导航的毛玻璃效果与选中态
- 中文系统字体栈
- 深色模式下的配色
- 移动端响应式

常用设计变量在文件顶部：

```css
--main-width: 1120px;
--accent: #c81e3a;
--theme: #f7f8fa;
--entry: #ffffff;
```

修改主题变量即可整体调整主色、背景和内容宽度。

页脚使用 `Orz/layouts/_partials/extend_footer.html` 自定义，PaperMod 默认页脚通过 `hideFooter = true` 关闭；备案信息维护在 `Orz/config.toml` 的 `[params.legal]`。

## 维护产品展示

产品相关数据分两层：首页只展示精选产品，完整清单放在产品全览页。

### 首页精选产品

编辑 `Orz/data/products.yaml`，新增一条记录即可出现在首页：

```yaml
- name: 产品名称
  tagline: 一句话介绍
  description: 详细介绍
  url: https://example.com
  icon: "rocket"      # 卡片图标（Lucide 图标名）
  category: App      # App / 工具 / 游戏 / 站点 / 内容 ...
  status: 已上架      # 可选状态标签
  tags: ["Swift", "iOS"]
  featured: true     # 是否在首页展示；false 时只出现在产品全览页
```

字段含义见文件顶部注释。首页只展示 `featured: true` 的产品，产品卡片的链接均以新窗口打开。

### 产品全览页

`/products/` 页面读取 `Orz/data/showcase.yaml`，按个人账号与组织分组展示：

- `groups`：来源分组，包含名称、图标、简介、官网与 GitHub 地址
- `products`：产品和项目，包含状态、简介、功能要点、标签与多个外链
- `links`：每个产品的外链入口，`primary: true` 会显示为高亮主按钮

新增产品时，在对应 `group.products` 下追加记录；新增组织时在 `groups` 下追加一个分组。产品页默认只展开第一组，其他组织按需展开；产品描述和功能要点再收进「查看详情」，保持列表简洁。

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

如需临时覆盖，可以在 GitHub 仓库的 **Variables** 中设置 `SITE_URL` / `SITE_CNAME`，或使用环境变量：

```bash
SITE_URL=https://example.com/ ./scripts/build_site.sh
```

构建时会自动：

- 将解析出的地址作为 Hugo `--baseURL`
- 若配置了自定义域名，生成 `Orz/public/CNAME`
- 若没有自定义域名，则不生成 CNAME，使用 GitHub Pages 默认地址

## 自动化流程

### GitHub Actions（推荐）

工作流文件：`.github/workflows/hugo.yml`

- **push 到 `main`**：构建站点 → 部署到 `gh-pages` 分支（`force_orphan`，保持分支干净）
- **Pull Request**：只构建并检查产物，不部署，用于提前发现构建错误
- **手动触发**：Actions 页面 `Run workflow`
- 只在 `Orz/**`、`scripts/**`、发布脚本或工作流本身变化时触发
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
| 修改姓名、简介、技术栈 | `Orz/config.toml` 的 `[params.home]` |
| 增删首页精选产品 | `Orz/data/products.yaml` |
| 增删产品全览内容 | `Orz/data/showcase.yaml` |
| 同步 GitHub 产品候选 | `python3 scripts/sync_github_products.py` |
| 修改顶部菜单 / 社交链接 | `Orz/config.toml` 的 `[menu.main]`、`[params.socialIcons]` |
| 修改整体视觉与组件 | `Orz/assets/css/extended/custom.css` |
| 修改域名 | GitHub **Settings → Pages → Custom domain**；构建时自动读取，无需改代码 |
| 临时覆盖域名 | `SITE_URL=https://example.com/ ./scripts/build_site.sh` |
| 修改页脚 / 备案信息 | `Orz/layouts/_partials/extend_footer.html` 与 `Orz/config.toml` 的 `[params.legal]` |

## 技术说明

- 主题通过 Git submodule 引入；自定义样式和模板都放在项目目录中，升级主题不会丢失。
- 首页与产品全览页均为数据驱动，内容维护在 `Orz/data/` 与 `Orz/content/`。
- 站点使用系统字体栈，不依赖 Google Fonts，国内访问更稳定。
- 深浅色主题由 PaperMod 提供，自定义组件使用 CSS 变量自动适配。
- 站点构建无需 Node.js，产物为纯静态文件。

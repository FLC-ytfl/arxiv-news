# 变更提案：生成产物从 main 分支剥离并发布到 GitHub Pages

## 需求背景
当前自动化流程每天会执行 `python main.py` 并把 `README.md`、`history/`、`docs/`（尤其是 `docs/data/snapshots/*.json`）提交到 `main` 分支。随着每日快照累积，仓库体积会持续增长，进而导致 clone/pull 变慢，并且 `main` 分支被“生成物提交”噪声淹没，不利于日常开发与审阅。

本提案的目标是：保留 GitHub Pages 的可用性与历史切换能力，同时让 `main` 分支只承载源码与站点源码（非每日生成的数据），避免每日自动提交对 `main` 造成干扰与膨胀。

## 变更内容（方案 2: gh-pages 分支）
1. **初始化 gh-pages 孤儿分支**：创建与 main 完全独立的 gh-pages 分支，专门存放生成物与历史归档。
2. **调整 GitHub Actions**：日更流程在 main 运行生成，仅提交源数据到 main（`data/`），将生成的 README.md 和 docs/ 推送到 gh-pages 分支。
3. **main 分支清理**：将 README.md、`docs/data/**`、`history/**` 从 main 的 Git 追踪中移除，并加入 `.gitignore`，保证 main 分支绝对干净。
4. **GitHub Pages 配置**：将部署源从 main 的 docs/ 切换到 gh-pages 分支的根目录。
5. **生成脚本可选增强**：为 `main.py` 增加"输出目录/README 输出开关"能力，便于 CI 直接生成到临时目录（可选项，后续优化）。
6. **更新知识库（SSOT）**：同步更新 `helloagents/project.md` 与相关模块文档，记录新的双分支约定。

## 影响范围（方案 2）
- **模块**：generator（`main.py`）、自动化（`.github/workflows/*`）、站点（`docs/`）、知识库（`helloagents/*`）、Git 分支结构
- **新增分支**：`gh-pages`（孤儿分支，专门存放生成物）
- **主要文件（预期）**：
  - `.github/workflows/daily_update.yml`（新增 gh-pages 推送步骤）
  - `main.py`（可选增强，后续优化）
  - `.gitignore`（忽略 README.md、docs/data、history）
  - main 分支：移除 `README.md`、`docs/data/**`、`history/**` 的追踪
  - gh-pages 分支：包含 `README.md`、`docs/`（完整站点）、历史归档
  - `docs/index.html`（保留在 main，作为站点源码）
  - `helloagents/project.md`（更新分支约定）
  - `helloagents/wiki/modules/generator.md`（补充发布流程说明）

## 核心场景
### Requirement: `main` 分支不再每日增长
**Module:** automation
日更任务执行后，`main` 分支没有新的自动提交（或仅在变更源码/站点源码时人工提交）。

#### Scenario: 定时更新与发布
按日运行后：
- GitHub Pages 站点可访问
- 数据文件可更新（manifest + 当日快照）
- `main` 分支不产生由生成物导致的提交

### Requirement: 站点仍支持历史日期切换
**Module:** docs-site
前端仍可通过 `manifest.json` 的日期列表加载历史快照文件。

#### Scenario: 历史日期浏览
用户在站点选择某日期：
- 前端能请求到该日期对应的快照 JSON
- 分类/搜索/筛选等功能正常

### Requirement: 仓库体积增长受控
**Module:** repository
生成数据不再进入 `main` 的 Git 历史，日常开发 clone/pull 不被快照体积拖慢。

#### Scenario: 新开发者拉取仓库
默认 clone 或单分支 clone 主要获取源码与站点源码，而不是多年快照数据。

## 风险评估（方案 2）
- **风险：gh-pages 分支初始化失败或推送冲突**
  - **缓解**：先手动创建并验证孤儿分支；工作流添加 `concurrency` 配置避免并发推送；push 前先 pull 或 fetch。
- **风险：main 分支清理时误删源码文件**
  - **缓解**：仅删除生成物（README.md、docs/data、history）；保留 docs/index.html 等站点源码；先在本地测试，确认 `git status` 后再推送。
- **风险：GitHub Pages 部署源切换导致短时不可用**
  - **缓解**：先确保 gh-pages 分支有完整内容，再切换 Pages Source；手动触发一次工作流验证 gh-pages 部署成功后再切换。
- **风险：历史数据丢失**
  - **缓解**：在清理 main 前，确保 gh-pages 已包含所有历史归档；可先备份现有 history/ 目录。
- **风险：工作流权限不足导致推送失败**
  - **缓解**：在工作流配置中显式添加 `permissions: contents: write`；使用 `GITHUB_TOKEN` 自动授权。


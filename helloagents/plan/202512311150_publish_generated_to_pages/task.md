# 任务清单：生成产物从 main 分支剥离并发布到 GitHub Pages（方案 2: gh-pages 分支）

Directory: `helloagents/plan/202512311150_publish_generated_to_pages/`

---

## 实施方案说明

采用 **gh-pages 孤儿分支方案**：
- **main 分支**：只保留源码、配置、工作流，保持干净
- **gh-pages 分支**：专门存放生成的 README.md、data.json 及历史记录
- 日更工作流在 main 运行，生成物推送到 gh-pages
- GitHub Pages 从 gh-pages 部署

**效果**：
✅ `git clone` 默认只拉 main，看不到历史数据
✅ main 分支日常操作非常干净
✅ GitHub Pages 正常部署，保留完整历史
⚠️ 仓库 .git 目录会随 gh-pages 提交增长（用户明确不在意）

---

## 1. 初始化 gh-pages 孤儿分支
- [ ] 1.1 创建 gh-pages 孤儿分支（无父提交，与 main 完全独立）
  - 执行命令：`git checkout --orphan gh-pages`
  - 清空工作区：`git rm -rf .`
  - 添加占位文件：`echo "# ArXiv Daily News Archive" > README.md`
  - 提交：`git add README.md && git commit -m "Initialize gh-pages branch"`
  - 推送：`git push origin gh-pages`
  - 切回 main：`git checkout main`
  - 验证：`git branch -a` 应看到 `remotes/origin/gh-pages`

## 2. 改造工作流 - 双分支推送策略
- [ ] 2.1 修改 `.github/workflows/daily_update.yml`：保留 main 的 data/ 提交，新增 gh-pages 部署步骤
  - main 分支提交步骤：仅提交 `data/` 目录（保留源数据）
  - gh-pages 部署步骤：
    - 使用 `actions/checkout@v4` 的多分支模式 checkout gh-pages 到子目录
    - 复制生成物：`README.md`、`docs/` 整个目录到 gh-pages 工作目录
    - 提交到 gh-pages：`git add . && git commit -m "Update pages: $(date)"`
    - 推送到 gh-pages：`git push origin gh-pages`
  - 验证：why.md#requirement-main-分支不再每日增长

- [ ] 2.2 添加 `permissions` 配置：确保工作流有写权限
  ```yaml
  permissions:
    contents: write
  ```

- [ ] 2.3 添加 `concurrency` 配置：避免并发部署冲突
  ```yaml
  concurrency:
    group: pages-deployment
    cancel-in-progress: false
  ```

- [ ] 2.4 增加 smoke 验证步骤（可选）：检查生成物完整性
  - 验证 `docs/data/manifest.json` 存在
  - 验证 `README.md` 存在且非空
  - 验证：why.md#requirement-站点仍支持历史日期切换

## 3. main 分支清理
- [ ] 3.1 更新 `.gitignore`：忽略本地生成物
  - 添加：`README.md`（仅本地生成，不提交到 main）
  - 添加：`docs/data/**`（前端数据，仅在 gh-pages）
  - 添加：`history/**`（历史归档，迁移到 gh-pages）
  - 保留：`docs/index.html`（站点源码，应保留在 main）
  - 验证：why.md#requirement-仓库体积增长受控

- [ ] 3.2 从 main 分支移除已追踪的生成物
  - 删除 README.md：`git rm README.md`
  - 删除 docs/data/：`git rm -r docs/data`
  - 删除 history/：`git rm -r history`
  - 提交：`git commit -m "Move generated files to gh-pages branch"`
  - 推送：`git push origin main`
  - 验证：`git status` 应显示 clean，`git log --oneline -5` 不应再有日更提交噪声

- [ ] 3.3 确认 docs/index.html 保留在 main
  - 验证 `git ls-files docs/index.html` 有输出
  - 验证站点源码文件仍在追踪中

## 4. 配置 GitHub Pages 部署源
- [ ] 4.1 进入仓库 Settings → Pages
  - Source: Deploy from a branch
  - Branch: `gh-pages` / `/ (root)`
  - 保存设置
  - 验证：访问 `https://<username>.github.io/arxiv-news/` 应能看到站点

- [ ] 4.2 等待 Pages 部署完成（约 1-2 分钟）
  - 查看 Actions 标签页：应有 `pages-build-deployment` 工作流
  - 验证：why.md#requirement-站点仍支持历史日期切换

## 5. 知识库同步（SSOT）
- [ ] 5.1 更新 `helloagents/project.md`
  - 修改"展示"部分：`GitHub Pages（由 Actions 推送到 gh-pages 分支发布）`
  - 修改"目录约定"：说明 main 不再包含 README/docs/data/history
  - 添加"分支约定"：
    - `main`: 源码、配置、工作流
    - `gh-pages`: 生成的站点产物与历史归档

- [ ] 5.2 更新 `helloagents/wiki/modules/generator.md`
  - 补充："产物不再提交到 main"的约束
  - 补充：CI 发布流程说明（main 运行生成，推送到 gh-pages）

## 6. 安全检查
- [ ] 6.1 执行安全检查（G9）
  - 确认无明文 token/密钥写入仓库
  - 确认 Actions 权限最小化（仅 `contents: write`）
  - 确认无危险破坏性命令（例如 `git push --force` 到 main）
  - 确认 gh-pages 分支权限隔离（不影响 main 分支代码审查流程）

## 7. 验收与回归测试
- [ ] 7.1 本地验收：运行 `python main.py`
  - 确认生成 `README.md`（在工作区，不提交到 main）
  - 确认生成 `docs/data/manifest.json`
  - 确认生成 `docs/data/snapshots/<date>.json`
  - 前端 index.html 能加载 manifest 和快照数据（用本地服务器测试）

- [ ] 7.2 CI 手动触发验收：通过 `workflow_dispatch` 触发
  - 验证 main 分支只有 data/ 提交（如有新数据）
  - 验证 gh-pages 分支有新的 README.md + docs/ 提交
  - 访问 GitHub Pages URL：站点可访问
  - 前端日期切换功能正常（历史快照可加载）
  - 验证：why.md#requirement-站点仍支持历史日期切换

- [ ] 7.3 定时任务验收：等待下一次自动触发（UTC 0:00）
  - 验证自动运行成功
  - 验证 main 分支干净（无 README/docs/data 提交）
  - 验证 gh-pages 分支有新提交
  - 验证站点更新

## 8. 后续优化（可选，不阻塞上线）
- [ ] 8.1 为 main.py 增加输出目录参数（`--out-dir`）
  - 使 CI 可直接生成到临时目录，避免污染工作区
  - 本地开发时可指定输出路径

- [ ] 8.2 为 main.py 增加 README 输出开关（`--no-readme`）
  - 使 main 分支的 README.md 可独立维护（项目介绍）
  - 生成的论文列表 README 仅在 gh-pages

- [ ] 8.3 添加 gh-pages 历史保留策略（控制分支体积）
  - 仅保留最近 N 天快照（例如 90 天）
  - 或保留月度归档 + 最近 30 天

---

## 验收标准总览

| 需求项 | 验证方法 | 通过标准 |
|--------|----------|----------|
| main 分支不再日增长 | `git log --oneline main` | 无每日自动提交（除 data/ 源数据） |
| 站点历史切换可用 | 访问站点，切换日期 | 历史快照可加载 |
| 仓库体积受控 | `git clone` main | 不包含 docs/data、history |
| Pages 部署成功 | 访问 Pages URL | 站点可访问 |
| 安全无风险 | 代码审查 | 无密钥泄露、权限最小化 |

---

## 执行顺序建议

1. **初始化 gh-pages**（步骤 1）
2. **清理 main 分支**（步骤 3）- 使 main 干净
3. **改造工作流**（步骤 2）- 实现双分支推送
4. **配置 Pages**（步骤 4）- 切换部署源
5. **知识库同步**（步骤 5）- 更新文档
6. **安全检查**（步骤 6）- 验证无风险
7. **验收测试**（步骤 7）- 确认可用
8. **可选优化**（步骤 8）- 后续迭代

---

**备注**：
- 方案 2 的核心优势是 main 分支绝对干净，日常开发体验最佳
- 用户明确不在意仓库整体体积，因此 gh-pages 增长不是问题
- 如未来需要控制 gh-pages 体积，可在步骤 8.3 实施保留策略

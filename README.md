# ArXiv Daily News

[![Daily Update](https://github.com/FLC-ytfl/arxiv-news/actions/workflows/daily_update.yml/badge.svg)](https://github.com/FLC-ytfl/arxiv-news/actions/workflows/daily_update.yml)
[![GitHub Pages](https://img.shields.io/badge/GitHub-Pages-brightgreen)](https://flc-ytfl.github.io/arxiv-news/)

📚 自动追踪 arXiv 最新论文，每日更新，支持历史浏览。

## 🌟 特性

- **自动化抓取**：每天 UTC 0:00（北京时间 8:00）自动抓取指定分类的最新 arXiv 论文
- **智能标注**：自动识别顶会论文（CVPR、ICCV、NeurIPS 等 30+ 会议）
- **历史浏览**：支持按日期切换查看历史论文快照
- **前端界面**：提供友好的 Web 界面，支持分类筛选和关键词搜索
- **双分支架构**：main 分支保持干净，生成物自动推送到 gh-pages



## 📖 在线访问

🔗 **GitHub Pages**：[https://flc-ytfl.github.io/arxiv-news/](https://flc-ytfl.github.io/arxiv-news/)

在线站点每日自动更新，无需本地部署。

## 🏗️ 项目结构

```
arxiv-news/
├── main.py                  # 论文抓取与生成脚本
├── requirements.txt         # Python 依赖
├── docs/
│   └── index.html          # 前端单页应用（站点源码）
├── .github/
│   └── workflows/
│       └── daily_update.yml # 自动化工作流
└── helloagents/            # 项目文档与知识库
```

### 分支说明

- **main** - 源码、配置、工作流（保持干净）
- **gh-pages** - 生成的站点产物与历史归档（自动推送）

## 🔧 配置说明

### 修改抓取分类

编辑 `main.py`，找到抓取分类配置：

```python
# 示例：修改为其他分类
categories = ["cs.CV", "cs.AI", "cs.LG"]
```

支持的分类参考：[arXiv Category Taxonomy](https://arxiv.org/category_taxonomy)

### 修改抓取数量

```python
# 默认每个分类抓取 100 篇
max_results = 100
```

### 自定义顶会列表

编辑 `main.py` 中的 `CONFERENCE_ABBREVS` 列表：

```python
CONFERENCE_ABBREVS = [
    "CVPR", "ICCV", "ECCV",  # 计算机视觉
    "NeurIPS", "ICML", "ICLR",  # 机器学习
    "ACL", "EMNLP", "NAACL",  # 自然语言处理
    # ... 添加更多会议
]
```

## 🤖 自动化工作流

项目使用 GitHub Actions 实现每日自动更新：

1. **触发时间**：每天 UTC 0:00（可在 `.github/workflows/daily_update.yml` 修改）
2. **执行流程**：
   - 在 main 分支运行 `python main.py` 生成数据
   - 将 README.md + docs/ + history/ 推送到 gh-pages 分支
   - GitHub Pages 自动部署更新
3. **手动触发**：在 Actions 页面点击 "Run workflow" 立即执行

## 📊 数据格式

### Manifest (docs/data/manifest.json)

```json
{
  "dates": ["2025-12-31", "2025-12-30", "..."],
  "generated_at": "2025-12-31T00:00:00Z"
}
```

### Snapshot (docs/data/snapshots/YYYY-MM-DD.json)

```json
{
  "date": "2025-12-31",
  "papers": [
    {
      "arxiv_id": "2312.12345",
      "title": "论文标题",
      "authors": ["作者1", "作者2"],
      "categories": ["cs.CV", "cs.AI"],
      "abstract": "摘要内容...",
      "published": "2025-12-30T10:00:00Z",
      "updated": "2025-12-30T10:00:00Z",
      "pdf_url": "https://arxiv.org/pdf/2312.12345",
      "abs_url": "https://arxiv.org/abs/2312.12345",
      "has_conference": true,
      "matched_conferences": ["CVPR"]
    }
  ]
}
```

## 🎨 自定义界面

前端界面源码位于 `docs/index.html`。

**修改步骤**：
1. 编辑 `docs/index.html`（在 main 分支）
2. 提交并推送到 main
3. 等待下次工作流运行（或手动触发）
4. 工作流会自动将更新的 index.html 同步到 gh-pages

**注意**：不要直接修改 gh-pages 分支的文件，下次工作流运行时会被覆盖。

## 🛠️ 开发指南

### 本地开发流程

1. **修改源码**（main.py 或 docs/index.html）
2. **本地测试**：
   ```bash
   python main.py  # 测试数据生成
   cd docs && python -m http.server 8000  # 测试前端
   ```
3. **提交到 main 分支**：
   ```bash
   git add .
   git commit -m "描述你的修改"
   git push origin main
   ```
4. **验证部署**：工作流运行后访问 GitHub Pages 查看效果

## 📝 更新日志

### 2025-12-31
- ✅ 实施方案 2：gh-pages 分支架构
- ✅ main 分支保持干净（仅源码、配置）
- ✅ 自动化工作流支持双分支推送
- ✅ 历史归档迁移到 gh-pages

### 历史版本
查看 [gh-pages 分支](https://github.com/FLC-ytfl/arxiv-news/tree/gh-pages) 的 `history/` 目录。

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

### 提交 PR 前请确保：
- ✅ 代码风格符合项目规范
- ✅ 本地测试通过
- ✅ 提交信息清晰描述改动内容
- ✅ 修改了源码文件（main 分支），而非生成物


## 📄 许可证

MIT License


---

**⭐ 如果这个项目对你有帮助，欢迎 Star！**

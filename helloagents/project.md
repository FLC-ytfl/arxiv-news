# 项目技术约定

## 技术栈
- **语言**: Python 3.9+
- **依赖**: `arxiv`（用于抓取论文元数据）
- **自动化**: GitHub Actions（定时执行 `main.py` 并推送产物到 gh-pages 分支）
- **展示**: GitHub Pages（由 Actions 推送到 gh-pages 分支发布）

## 分支约定
- **main**: 源码、配置、工作流（保持干净，无生成物）
- **gh-pages**: 生成的站点产物与历史归档（由 Actions 自动推送）

## 目录约定

### main 分支
- `main.py`: 抓取与产物生成入口（README + GitHub Pages 所需数据）
- `docs/`: GitHub Pages 静态站点源码目录
- `docs/index.html`: 前端应用入口（静态源码，保留在 main）
- `.github/workflows/`: 自动化工作流
- `helloagents/`: HelloAGENTS 知识库（SSOT）、方案包与变更历史归档

### gh-pages 分支（生成物）
- `README.md`: 每日生成的论文列表
- `docs/`: 完整的前端站点（包含 index.html + data/）
- `docs/data/`: 前端消费的数据目录（`manifest.json` + `snapshots/*.json`）
- `history/`: 历史 README 归档（按 `history/YYYY/MM/YYYY.MM.DD.md` 组织）

### 本地忽略（.gitignore）
- `README.md`: 本地生成，不提交到 main
- `docs/data/`: 本地生成，不提交到 main
- `history/`: 本地生成，不提交到 main

## 开发约定
- **编码**: UTF-8
- **命名**: Python 使用 `snake_case`；JSON 字段使用 `snake_case`
- **可重复生成**: `main.py` 应可在本地重复执行，不依赖交互输入

## 测试与验收
- 本项目以"生成产物可用"为主要验收方式：
  - `python main.py` 成功执行
  - 生成/更新 `README.md`（本地生成，不提交到 main）
  - 生成/更新 `docs/data/` 下的前端所需数据文件（本地生成，不提交到 main）
  - GitHub Actions 自动推送生成物到 gh-pages 分支
  - GitHub Pages 站点可访问且历史日期切换功能正常

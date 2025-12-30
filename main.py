# 本脚本用于抓取指定 arXiv 分类的最新论文，并生成：
# 1) README.md（简洁标题列表）
# 2) docs/data/manifest.json 与 docs/data/snapshots/YYYY-MM-DD.json（供 GitHub Pages 前端加载）

import datetime
import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple

import arxiv

CONFERENCE_ABBREVS = [
    "CVPR",
    "ICCV",
    "ECCV",
    "NeurIPS",
    "ICML",
    "ICLR",
    "ACL",
    "EMNLP",
    "NAACL",
    "EACL",
    "COLING",
    "AAAI",
    "IJCAI",
    "KDD",
    "WWW",
    "SIGGRAPH",
    "WACV",
    "ICRA",
    "IROS",
    "CoRL",
    "RSS",
    "AISTATS",
    "UAI",
]


def utc_now_iso() -> str:
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def normalize_text(text: str) -> str:
    return re.sub(r"\\s+", " ", (text or "").replace("\n", " ")).strip()


def extract_arxiv_id(entry_id: str) -> str:
    match = re.search(r"/abs/([^?#]+)", entry_id or "")
    return match.group(1) if match else (entry_id or "")


def extract_venue(result: Any) -> str:
    journal_ref = normalize_text(getattr(result, "journal_ref", "") or "")
    if journal_ref:
        return journal_ref

    comment = normalize_text(getattr(result, "comment", "") or "")
    if not comment:
        return ""

    for abbrev in CONFERENCE_ABBREVS:
        pattern = rf"\\b{re.escape(abbrev)}\\b(?:\\s*(20\\d{{2}}))?"
        match = re.search(pattern, comment, flags=re.IGNORECASE)
        if match:
            year = match.group(1)
            return f"{abbrev} {year}" if year else abbrev

    return ""


def result_to_paper(result: Any) -> Dict[str, Any]:
    entry_id = getattr(result, "entry_id", "") or ""
    paper_id = extract_arxiv_id(entry_id)
    authors = [a.name for a in (getattr(result, "authors", []) or []) if getattr(a, "name", None)]

    return {
        "id": paper_id,
        "title": normalize_text(getattr(result, "title", "") or ""),
        "url": entry_id,
        "published": getattr(getattr(result, "published", None), "date", lambda: None)().isoformat()
        if getattr(result, "published", None)
        else "",
        "authors": authors,
        "summary": normalize_text(getattr(result, "summary", "") or ""),
        "primary_category": getattr(result, "primary_category", "") or "",
        "categories": list(getattr(result, "categories", []) or []),
        "venue": extract_venue(result),
    }


def fetch_results(client: arxiv.Client, category: str, max_results: int = 500) -> List[Any]:
    search = arxiv.Search(
        query=f"cat:{category}",
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending,
    )
    return list(client.results(search))


def get_latest_date(results: List[Any]) -> Optional[datetime.date]:
    if not results:
        return None
    return results[0].published.date()


def collect_results_for_date(results: List[Any], target_date: datetime.date) -> List[Any]:
    collected: List[Any] = []
    for result in results:
        published_date = result.published.date()
        if published_date > target_date:
            continue
        if published_date < target_date:
            break
        collected.append(result)
    return collected


def build_readme_section(category: str, category_name: str, results: List[Any]) -> str:
    if not results:
        return f"### {category_name} ({category})\n未找到任何论文。\n\n---\n"

    latest_date = results[0].published.date()
    content = f"### {category_name} ({category})\n"
    content += f"**最近发布日期**: {latest_date}\n\n"

    count = 0
    for result in results:
        if result.published.date() != latest_date:
            break
        count += 1
        content += f"{count}. **[{normalize_text(result.title)}]({result.entry_id})**\n"

    content += f"\n{category}共找到 {count} 篇论文。\n\n---\n"
    return content


def ensure_dirs() -> Tuple[str, str]:
    data_dir = os.path.join("docs", "data")
    snapshots_dir = os.path.join(data_dir, "snapshots")
    os.makedirs(snapshots_dir, exist_ok=True)
    return data_dir, snapshots_dir


def list_snapshot_dates(snapshots_dir: str) -> List[str]:
    if not os.path.isdir(snapshots_dir):
        return []

    dates: List[str] = []
    for filename in os.listdir(snapshots_dir):
        if not filename.endswith(".json"):
            continue
        date_part = filename[: -len(".json")]
        try:
            datetime.date.fromisoformat(date_part)
        except ValueError:
            continue
        dates.append(date_part)

    return sorted(set(dates), reverse=True)


def write_json(path: str, payload: Dict[str, Any]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")


def generate_snapshot_and_manifest(
    categories: Dict[str, str],
    category_results: Dict[str, List[Any]],
    generated_at: Optional[str] = None,
) -> Tuple[str, str]:
    # 计算快照日期：取所有分类中的最大最新日期。
    latest_dates: List[datetime.date] = []
    for cat_code in categories.keys():
        latest = get_latest_date(category_results.get(cat_code, []))
        if latest:
            latest_dates.append(latest)

    if not latest_dates:
        raise RuntimeError("未获取到任何分类的论文结果，无法生成数据快照。")

    snapshot_date = max(latest_dates)
    generated_at = generated_at or utc_now_iso()

    data_dir, snapshots_dir = ensure_dirs()

    snapshot_payload: Dict[str, Any] = {
        "date": snapshot_date.isoformat(),
        "generated_at": generated_at,
        "categories": [],
    }

    for cat_code, cat_name in categories.items():
        results = category_results.get(cat_code, [])
        papers_for_day = collect_results_for_date(results, snapshot_date)
        snapshot_payload["categories"].append(
            {
                "code": cat_code,
                "name": cat_name,
                "papers": [result_to_paper(r) for r in papers_for_day],
            }
        )

    snapshot_path = os.path.join(snapshots_dir, f"{snapshot_date.isoformat()}.json")
    write_json(snapshot_path, snapshot_payload)

    manifest_payload: Dict[str, Any] = {
        "generated_at": generated_at,
        "dates": list_snapshot_dates(snapshots_dir),
        "categories": [{"code": code, "name": name} for code, name in categories.items()],
    }

    manifest_path = os.path.join(data_dir, "manifest.json")
    write_json(manifest_path, manifest_payload)

    return manifest_path, snapshot_path


if __name__ == "__main__":
    categories_map = {
        "cs.CV": "计算机视觉",
        "cs.AI": "人工智能",
        "cs.LG": "机器学习",
        "cs.CL": "计算语言学 (NLP)",
        "cs.RO": "机器人学",
    }

    generated_at = utc_now_iso()

    readme_full = "# ArXiv Daily News\n\n"
    readme_full += f"更新时间(UTC): {generated_at}\n\n"
    readme_full += "📄 完整信息请访问 [GitHub Pages](https://flc-ytfl.github.io/arxiv-news/)\n\n"

    client = arxiv.Client(page_size=100, delay_seconds=3, num_retries=3)
    category_results_map: Dict[str, List[Any]] = {}

    for cat_code, cat_name in categories_map.items():
        print(f"正在抓取 {cat_name}...")
        results = fetch_results(client, cat_code)
        category_results_map[cat_code] = results
        readme_full += build_readme_section(cat_code, cat_name, results)

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_full)
    print("README.md 已更新。")

    manifest_path, snapshot_path = generate_snapshot_and_manifest(
        categories_map, category_results_map, generated_at=generated_at
    )
    print(f"数据文件已更新: {manifest_path}, {snapshot_path}")

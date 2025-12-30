import arxiv
import datetime

def get_latest_papers(category="cs.CV", category_name="计算机视觉"):
    # 1. 初始化 Client
    client = arxiv.Client(
        page_size=100,
        delay_seconds=3,
        num_retries=3
    )

    # 2. 定义搜索
    search = arxiv.Search(
        query=f"cat:{category}",
        max_results=500, 
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending
    )

    # 3. 执行搜索
    results = list(client.results(search))
    
    if not results:
        return f"### {category_name} ({category})\n未找到任何论文。\n\n"

    # 4. 获取最新的一篇论文的日期
    latest_date = results[0].published.date()
    content = f"### {category_name} ({category})\n"
    content += f"**最近发布日期**: {latest_date}\n\n"
    
    count = 0
    for result in results:
        if result.published.date() == latest_date:
            count += 1
            authors = ', '.join(a.name for a in result.authors[:3])
            summary = result.summary[:200].replace('\n', ' ')
            content += f"{count}. **[{result.title}]({result.entry_id})**\n"
            content += f"   - **作者**: {authors}\n"
            content += f"   - **摘要**: {summary}...\n\n"
        else:
            break

    content += f"{category}共找到 {count} 篇论文。\n\n---\n"
    return content

if __name__ == "__main__":
    # 定义想要追踪的热门 CS 方向
    categories = {
        "cs.CV": "计算机视觉",
        "cs.AI": "人工智能",
        "cs.LG": "机器学习",
        "cs.CL": "计算语言学 (NLP)",
        "cs.RO": "机器人学"
    }

    full_content = f"# ArXiv Daily News\n\n更新时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    for cat_code, cat_name in categories.items():
        print(f"正在抓取 {cat_name}...")
        full_content += get_latest_papers(cat_code, cat_name)

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(full_content)
    print("README.md 已更新。")

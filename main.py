import arxiv
import datetime
import os

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
        return f"### {category_name} ({category})\n未找到任何论文。\n\n", ""

    # 4. 获取最新的一篇论文的日期
    latest_date = results[0].published.date()
    
    # README 简洁版（只有标题）
    readme_content = f"### {category_name} ({category})\n"
    readme_content += f"**最近发布日期**: {latest_date}\n\n"
    
    # GitHub Pages 完整版
    html_content = f'<h3>{category_name} ({category})</h3>\n'
    html_content += f'<p><strong>最近发布日期</strong>: {latest_date}</p>\n'
    html_content += '<div class="paper-list">\n'
    
    count = 0
    for result in results:
        if result.published.date() == latest_date:
            count += 1
            authors = ', '.join(a.name for a in result.authors[:3])
            if len(result.authors) > 3:
                authors += ' et al.'
            summary = result.summary.replace('\n', ' ')
            
            # README: 只有标题
            readme_content += f"{count}. **[{result.title}]({result.entry_id})**\n"
            
            # HTML: 完整信息
            html_content += f'''<div class="paper">
    <h4><a href="{result.entry_id}" target="_blank">{count}. {result.title}</a></h4>
    <p><strong>作者:</strong> {authors}</p>
    <p><strong>摘要:</strong> {summary}</p>
</div>
'''
        else:
            break

    readme_content += f"\n{category}共找到 {count} 篇论文。\n\n---\n"
    html_content += f'</div>\n<p>{category}共找到 {count} 篇论文。</p>\n<hr>\n'
    
    return readme_content, html_content

if __name__ == "__main__":
    # 定义想要追踪的热门 CS 方向
    categories = {
        "cs.CV": "计算机视觉",
        "cs.AI": "人工智能",
        "cs.LG": "机器学习",
        "cs.CL": "计算语言学 (NLP)",
        "cs.RO": "机器人学"
    }

    update_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # README 内容
    readme_full = f"# ArXiv Daily News\n\n更新时间: {update_time}\n\n"
    readme_full += "📄 完整信息请访问 [GitHub Pages](https://flc-ytfl.github.io/arxiv-news/)\n\n"
    
    # HTML 内容
    html_full = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ArXiv Daily News</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        h1 {{
            color: #333;
            border-bottom: 2px solid #007acc;
            padding-bottom: 10px;
        }}
        h3 {{
            color: #007acc;
            margin-top: 30px;
        }}
        .paper {{
            background: white;
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .paper h4 {{
            margin: 0 0 10px 0;
            color: #333;
        }}
        .paper h4 a {{
            color: #007acc;
            text-decoration: none;
        }}
        .paper h4 a:hover {{
            text-decoration: underline;
        }}
        .paper p {{
            margin: 5px 0;
            color: #555;
            line-height: 1.6;
        }}
        hr {{
            border: none;
            border-top: 1px solid #ddd;
            margin: 30px 0;
        }}
        .update-time {{
            color: #888;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <h1>📚 ArXiv Daily News</h1>
    <p class="update-time">更新时间: {update_time}</p>
'''
    
    for cat_code, cat_name in categories.items():
        print(f"正在抓取 {cat_name}...")
        readme_part, html_part = get_latest_papers(cat_code, cat_name)
        readme_full += readme_part
        html_full += html_part

    html_full += '''
</body>
</html>
'''

    # 创建 docs 目录用于 GitHub Pages
    os.makedirs("docs", exist_ok=True)

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_full)
    print("README.md 已更新。")
    
    with open("docs/index.html", "w", encoding="utf-8") as f:
        f.write(html_full)
    print("docs/index.html 已更新。")

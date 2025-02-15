import feedparser
import re
import json
from datetime import datetime
import pytz
from collections import defaultdict

def get_feed_category(feed_url, feed_list_content):
    # 查找feed_url所属的分类
    lines = feed_list_content.split('\n')
    current_category = None
    for line in lines:
        line = line.strip()
        if line.endswith(':'):
            current_category = line[:-1]  # 移除冒号
        elif line == feed_url:
            return current_category
    return 'Blog'  # 默认分类为 Blog

def fetch_feeds():
    with open('feed.list', 'r') as f:
        feed_list_content = f.read()
        feeds = [line.strip() for line in feed_list_content.splitlines() if line.strip() and not line.endswith(':')]
    
    articles_by_category = defaultdict(list)
    
    for feed_url in feeds:
        try:
            feed = feedparser.parse(feed_url)
            category = get_feed_category(feed_url, feed_list_content)
            
            for entry in feed.entries:
                published = entry.get('published_parsed', entry.get('updated_parsed'))
                if published:
                    dt = datetime(*published[:6])
                    dt = pytz.UTC.localize(dt)
                    beijing_tz = pytz.timezone('Asia/Shanghai')
                    dt = dt.astimezone(beijing_tz)
                    published_str = dt.strftime('%Y-%m-%d %H:%M')
                else:
                    published_str = ''
                
                summary = ''
                if 'summary' in entry:
                    summary = re.sub(r'<[^>]+>', '', entry.summary)
                    summary = summary.strip()[:150] + ('...' if len(summary) > 150 else '')
                elif 'description' in entry:
                    summary = re.sub(r'<[^>]+>', '', entry.description)
                    summary = summary.strip()[:150] + ('...' if len(summary) > 150 else '')
                
                article = {
                    'title': entry.title,
                    'link': entry.link,
                    'date': published_str,
                    'author': feed.feed.title,
                    'timestamp': dt.timestamp() if published else 0,
                    'summary': summary or '无摘要',
                    'source_url': feed.feed.link or feed_url,
                    'category': category
                }
                articles_by_category[category].append(article)
        except Exception as e:
            print(f"Error fetching {feed_url}: {str(e)}")
            continue
    
    # 对每个分类的文章进行处理
    all_articles = []
    for category, articles in articles_by_category.items():
        # 按时间戳排序
        articles.sort(key=lambda x: x['timestamp'], reverse=True)
        # 论坛分类保留所有文章，其他分类取60篇
        if category == 'Forums':
            all_articles.extend(articles)  # 保留所有文章
        else:
            all_articles.extend(articles[:60])  # 其他分类取60篇
    
    # 最终按时间排序
    all_articles.sort(key=lambda x: x['timestamp'], reverse=True)
    
    # 保存为JSON文件
    data = {
        'update_time': datetime.now(pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d'),  # 只显示年月日
        'articles': all_articles
    }
    
    with open('feed.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    fetch_feeds() 
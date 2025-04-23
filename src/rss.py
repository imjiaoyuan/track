import feedparser
import logging
from datetime import datetime
import pytz
import os
import re
from config import RSS_FEEDS, MAX_ARTICLES

logger = logging.getLogger(__name__)

class RSSFetcher:
    def __init__(self):
        self.index_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'content/_index.md'
        )
        feedparser.USER_AGENT = "Mozilla/5.0 (compatible; Echo/1.0; +https://github.com/yourusername/echo)"

    def _parse_date(self, entry):
        """Parse date from entry with fallbacks"""
        for field in ['published_parsed', 'updated_parsed', 'created_parsed']:
            if hasattr(entry, field) and getattr(entry, field):
                try:
                    dt = datetime(*getattr(entry, field)[:6], tzinfo=pytz.UTC)
                    return dt.astimezone(pytz.timezone('Asia/Shanghai'))
                except Exception:
                    continue
        return datetime.now(pytz.timezone('Asia/Shanghai'))

    def fetch(self):
        entries_by_category = {}
        
        for category, feeds in RSS_FEEDS.items():
            entries = []
            for feed_url in feeds:
                try:
                    feed = feedparser.parse(feed_url)
                    if not feed.entries:
                        continue

                    feed_title = feed.feed.get('title', '')
                    for entry in feed.entries:
                        try:
                            entries.append({
                                'title': entry.title,
                                'link': entry.link,
                                'date': self._parse_date(entry),
                                'author': feed_title
                            })
                        except Exception as e:
                            logger.error(f"Error parsing entry from {feed_url}: {str(e)}")
                            
                except Exception as e:
                    logger.error(f"Error fetching {feed_url}: {str(e)}")
            
            # Sort by date and limit entries
            entries.sort(key=lambda x: x['date'], reverse=True)
            entries_by_category[category] = entries[:MAX_ARTICLES]
            
        return entries_by_category

    def update_content(self, entries_by_category):
        for category, entries in entries_by_category.items():
            content = []
            today = datetime.now(pytz.timezone('Asia/Shanghai')).date()
            
            today_entries = [e for e in entries if e['date'].date() == today]
            old_entries = [e for e in entries if e['date'].date() != today]
            
            if today_entries:
                content.append("**今日更新**")
                for entry in today_entries:
                    content.append(f"- [{entry['title']}]({entry['link']}) / {entry['date'].strftime('%H:%M')}")
                content.append("")
            
            if old_entries:
                content.append("**历史记录**")
                for entry in old_entries:
                    content.append(f"- [{entry['title']}]({entry['link']}) / {entry['date'].strftime('%m月%d日 %H:%M')}")
            
            self._update_section(category, '\n'.join(content))

    def _update_section(self, category, content):
        """Update specific category section in index.md"""
        with open(self.index_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
        
        file_content = re.sub(
            f'<!--rss-{category}:start-->.*<!--rss-{category}:end-->', 
            f'<!--rss-{category}:start-->\n{content}\n<!--rss-{category}:end-->', 
            file_content, 
            flags=re.DOTALL
        )
        
        with open(self.index_path, 'w', encoding='utf-8') as f:
            f.write(file_content)

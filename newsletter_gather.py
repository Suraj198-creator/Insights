import feedparser
import time
import pprint
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import requests
load_dotenv()

urls=["https://techcrunch.com/feed/","https://news.google.com/rss/search?q=when:24h+allinurl:bloomberg.com&hl=en-US&gl=US&ceid=US:en","https://data-ai.theodo.com/en/technical-blog/rss.xml","https://nyheter.aitool.se/feed/","blog.datumbox.com/feed","https://news.mit.edu/rss/topic/artificial-intelligence2","https://www.theverge.com/rss/index.xml","https://www.marktechpost.com/feed/", "https://www.wired.com/feed/rss", "https://hnrss.org/frontpage",  "research.google/blog/rss", "ai2people.com/feed", "metadevo.com/feed", "dailyai.com/feed"]
results = {}
news_key: str = os.getenv("NEWS_API")

# response = requests.get(f"https://newsapi.org/v2/everything?q=Artifical Intelligence (AI)&from=2025-07-08&sortBy=publishedAt&apiKey={news_key}")

# pprint.pp(response.json())
today = datetime.now()
two_days_ago = (datetime.now() - timedelta(days=1)).date()
print(two_days_ago)
for x in urls:
    feed = feedparser.parse(x)
    for entry in feed.entries:
        TITLE = entry.title.lower()
        LINK = entry.link

        if hasattr(entry, 'published_parsed') or hasattr(entry, "pubDate"):
            published_dt = datetime.fromtimestamp(time.mktime(entry.published_parsed))
            published_date = published_dt.date()  # Truncate time part

            if published_date >= two_days_ago:
                date_str = published_dt.strftime("%d/%m/%Y")
                TITLES = f"{TITLE} - {date_str}"
                results[TITLES] = LINK
            # print(TITLES)
            # print(LINK)
pprint.pp(results)
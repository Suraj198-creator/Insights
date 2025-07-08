import feedparser
import time

urls=["https://techcrunch.com/feed/","https://www.theverge.com/rss/index.xml", "https://www.wired.com/feed/rss", "https://hnrss.org/frontpage"]

for x in urls:
    feed = feedparser.parse(x)
    for entry in feed.entries:
        TITLE = entry.title.lower()
        LINK = entry.link
        date_str = time.strftime("%d/%m/%Y", entry.published_parsed)
        TITLES= (TITLE + " - " + date_str)
        print(TITLES)
        print(LINK)
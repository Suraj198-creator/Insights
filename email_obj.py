import feedparser
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import requests
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
import xml.etree.ElementTree as ET
load_dotenv()

import time

class Email:
    def __init__(self, email, token, slug):
        self.email = email
        self.token = token
        self.slug = slug

    def __str__(self):
        with open("templates/ai_news.html", "r", encoding="utf-8") as file:
            html = file.read()

        # Replace the placeholder with the actual unsubscribe link
        unsubscribe_link = f"https://yourdomain.com/unsubscribe/{self.slug}?token={self.token}"
        html = html.replace("{{ unsubscribe_link }}", unsubscribe_link)

        return html


class NewsScraper:
    def __init__(self, rss_urls=None, selenium_url=None, query=None):
        self.result = {}
        self.rss_urls = rss_urls or []
        self.selenium_url = selenium_url
        self.query = query
        self.news_api_key = os.getenv("NEWS_API")
        self.driver = None

    def init_driver(self):
        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True)
        self.driver = webdriver.Chrome(options=options)

    def fetch_selenium(self, css_selector=".top-stories li", accept_selector=".osano-cm-close"):
        if not self.selenium_url:
            return
        if not self.driver:
            self.init_driver()

        self.driver.get(self.selenium_url)
        time.sleep(2)
        try:
            accept = self.driver.find_element(By.CSS_SELECTOR, accept_selector)
            accept.click()
        except NoSuchElementException:
            pass

        elements = self.driver.find_elements(By.CSS_SELECTOR, css_selector)
        for elem in elements:
            try:
                a = elem.find_element(By.TAG_NAME, "a")
                title = a.text.strip()
                link = a.get_attribute("href")
                self.result[title] = link
            except Exception:
                continue

    def fetch_newsapi(self):
        if not self.query or not self.news_api_key:
            return
        today = datetime.now().date()
        from_date = today - timedelta(days=2)
        url = (
            f"https://newsapi.org/v2/everything?"
            f"q={self.query}&from={from_date}&sortBy=publishedAt&apiKey={self.news_api_key}"
        )

        try:
            response = requests.get(url)
            response.raise_for_status()
            articles = response.json().get("articles", [])
            for article in articles:
                self.result[article["title"]] = article["url"]
        except Exception as e:
            print(f"[NewsAPI Error] {e}")

    def fetch_rss(self):
        cutoff = datetime.now().date() - timedelta(days=1)
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

        for url in self.rss_urls:
            try:
                resp = requests.get(url, headers=headers, timeout=10)
                resp.raise_for_status()
                feed = feedparser.parse(resp.content)

                for entry in feed.entries:
                    title = entry.get('title', '').strip()
                    link = entry.get('link', '').strip()
                    date_struct = entry.get('published_parsed') or entry.get('updated_parsed')
                    if not date_struct:
                        continue

                    pub_date = datetime.fromtimestamp(time.mktime(date_struct)).date()
                    if pub_date < cutoff:
                        continue

                    date_str = pub_date.strftime("%d-%m-%Y")
                    key = f"{title} – {date_str}"
                    self.result[key] = link
            except Exception as e:
                print(f"[RSS Error] {e} on {url}")

    def fetch_xml(self, url, limit=5):
        try:
            response = requests.get(url)
            root = ET.fromstring(response.content)
            for item in root.findall(".//item")[:limit]:
                title = item.find("title").text
                link = item.find("link").text
                pubDate = item.find("pubDate").text
                parsed_date = datetime.strptime(pubDate, "%a, %d %b %Y %H:%M:%S %z")
                formatted_date = parsed_date.strftime("%d/%m/%Y")
                self.result[f"{title} - {formatted_date}"] = link
        except Exception as e:
            print(f"[XML Error] {e} on {url}")

    def scrape_all(self):
        self.fetch_selenium()
        # self.fetch_newsapi()
        self.fetch_rss()
        return self.result

class CryptoScraper(NewsScraper):
    def __init__(self):
        super().__init__(rss_urls=[
            "https://cryptopotato.com/feed/",
            "https://99bitcoins.com/feed/",
            "https://cryptobriefing.com/feed/",
            "https://crypto.news/feed/",
            "https://coinlabz.com/feed/",
            "https://www.newsbtc.com/feed/",
            "https://bitcoinist.com/feed/",
            "https://bitcointe.com/feed/",
            "https://zycrypto.com/feed/",
            "https://www.coolwallet.io/blogs/blog.atom",
            "https://thebitcoinnews.com/feed/",
            "https://www.tronweekly.com/feed/",
            "https://cryptogiggle.com/feed/"


        ], query="crypto")

    def scrape_all(self):
        super().scrape_all()
        # Add extra XML parsing just for HubSpot
        self.fetch_xml("https://cointelegraph.com/rss")
        self.fetch_xml("https://bitrss.com/rss.xml")
        self.fetch_xml("https://coinidol.com/rss2/")
        self.fetch_xml("https://www.coindesk.com/arc/outboundfeeds/rss")
        return self.result

class MarketingScraper(NewsScraper):
    def __init__(self):
        super().__init__(
            rss_urls=[
                "https://learn.g2.com/rss.xml",
                "https://moz.com/posts/rss/blog",
                "https://blog.hubspot.com/marketing/rss.xml",
                "https://ahrefs.com/blog/feed/",
                "https://www.socialmediaexaminer.com/feed/",
                "https://seths.blog/feed/atom/"
            ],
            selenium_url="https://www.marketingdive.com/",
            query="marketing"
        )

    def scrape_all(self):
        super().scrape_all()
        # Add extra XML parsing just for HubSpot
        self.fetch_xml("https://blog.hubspot.com/marketing/rss.xml")
        return self.result

class AIScraper(NewsScraper):
    def __init__(self):
        super().__init__(rss_urls=[
            "https://techcrunch.com/feed/",
            "https://news.google.com/rss/search?q=when:24h+allinurl:bloomberg.com&hl=en-US&gl=US&ceid=US:en",
            "https://data-ai.theodo.com/en/technical-blog/rss.xml",
            "https://nyheter.aitool.se/feed/",
            "http://blog.datumbox.com/feed",
            "https://news.mit.edu/rss/topic/artificial-intelligence2",
            "https://www.theverge.com/rss/index.xml",
            "https://www.marktechpost.com/feed/",
            "https://www.wired.com/feed/rss",
            "https://hnrss.org/frontpage",
            "https://research.google/blog/rss",
            "https://ai2people.com/feed",
            "https://metadevo.com/feed",
            "https://dailyai.com/feed"
        ], query="AI")



class SelfHelpScraper(NewsScraper):
    def __init__(self):
        super().__init__(rss_urls=[
            "https://feeds.feedburner.com/tinybuddha",
            "https://www.mindbodygreen.com/rss/featured.xml",
            "https://www.lifehack.org/feed"
        ], query= "Success stories")


class Fintech(NewsScraper):
    def __init__(self):
        super().__init__(rss_urls=[
            "https://thefintechtimes.com/feed/",
            "https://www.financemagnates.com/fintech/feed/",
            "https://fintechnews.sg/feed/",
            "https://australianfintech.com.au/blog/feed/",
            "https://www.etoro.com/news-and-analysis/feed/",
            "https://techcrunch.com/tag/fintech/feed/",
            "https://techbullion.com/feed/",
            "https://www.bobsguide.com/category/bankingtech/fintech/feed/",
            "https://finovate.com/feed/",
            "https://www.paymentscardsandmobile.com/category/fintech/feed/",
            "https://fintechnews.ch/feed/",
            "https://www.atmmarketplace.com/rss/",
            "https://www.lemnisk.co/blog/feed/",
            # "https://ncfacanada.org/feed/",
            "https://lendfoundry.com/feed/",
            "https://www.clarusft.com/feed/",
            "https://fintecbuzz.com/feed/",
            "https://regtechtimes.com/feed/",
            "https://www.fintechinshorts.com/fintech/feed/",
            "https://www.fintechtris.com/blog?format=rss",
            "https://fintechnews.hk/feed/"

        ], query= "fintech")


    def scrape_all(self):
        super().scrape_all()
        # Add extra XML parsing just for HubSpot
        self.fetch_xml("https://www.amount.com/blog/rss.xml")

        return self.result

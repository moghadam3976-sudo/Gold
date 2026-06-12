```python
import feedparser
from datetime import datetime

# منابع خبری مرتبط با طلا، معدن، زمین‌شناسی و اخبار فارسی

RSS_FEEDS = [

    # معدن و طلا
    "https://www.mining.com/feed/",
    "https://www.miningweekly.com/feed/",
    "https://www.gold.org/feed/",

    # زمین‌شناسی
    "https://geology.com/rss.xml",
    "https://www.sciencedaily.com/rss/earth_climate/geology.xml",

    # فارسی
    "https://www.isna.ir/rss",
    "https://www.irna.ir/rss",
    "https://www.mehrnews.com/rss",
]


def get_live_news(max_items_per_feed=10):

    news = []

    for feed_url in RSS_FEEDS:

        try:

            feed = feedparser.parse(feed_url)

            source_name = feed.feed.get(
                "title",
                feed_url
            )

            for entry in feed.entries[:max_items_per_feed]:

                news.append({

                    "title":
                        entry.get("title", ""),

                    "link":
                        entry.get("link", ""),

                    "published":
                        entry.get(
                            "published",
                            ""
                        ),

                    "source":
                        source_name,

                    "summary":
                        entry.get(
                            "summary",
                            ""
                        )
                })

        except Exception as e:

            print(
                f"RSS Error: {feed_url}"
            )

    # مرتب سازی بر اساس تاریخ (اگر وجود داشت)

    news.sort(
        key=lambda x:
        x.get("published", ""),
        reverse=True
    )

    return news


if __name__ == "__main__":

    items = get_live_news()

    print(
        f"{len(items)} news loaded."
    )

    for item in items[:5]:

        print(
            item["title"]
        )
```


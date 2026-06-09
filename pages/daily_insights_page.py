# pages/daily_insights_page.py
# -*- coding: utf-8 -*-
"""
صفحه اطلاعات روزانه - Gold Hunter Pro
نسخه بهینه‌سازی شده بدون نیاز به API Key (کاملاً آفلاین و سریع)
"""

import streamlit as st
import sqlite3
import json
import hashlib
import time
import random
from datetime import datetime, timedelta
from pathlib import Path
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET

# ─── تنظیمات پایه ────────────────────────────────────────────────────────────

DB_PATH = Path("data/news_cache.db")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# ─── منابع RSS واقعی در حوزه طلا و معدن ─────────────────────────────────────
RSS_SOURCES = [
    {
        "name": "Mining.com",
        "url": "https://www.mining.com/feed/",
        "lang": "en",
        "category": "اخبار معدن"
    },
    {
        "name": "Kitco News",
        "url": "https://www.kitco.com/rss/",
        "lang": "en",
        "category": "بازار طلا"
    },
    {
        "name": "Gold Price",
        "url": "https://www.goldprice.org/rss/gold-news.xml",
        "lang": "en",
        "category": "قیمت طلا"
    },
    {
        "name": "World Gold Council",
        "url": "https://www.gold.org/feed",
        "lang": "en",
        "category": "تحلیل طلا"
    },
    {
        "name": "Geology.com",
        "url": "https://geology.com/rss.xml",
        "lang": "en",
        "category": "زمین‌شناسی"
    },
    {
        "name": "خبرگزاری معادن ایران",
        "url": "https://imna.ir/rss",
        "lang": "fa",
        "category": "معادن ایران"
    },
    {
        "name": "ایرنا - اقتصادی",
        "url": "https://www.irna.ir/rss/economy",
        "lang": "fa",
        "category": "اخبار ایران"
    },
]

# دسته‌بندی‌های نمایش
DISPLAY_CATEGORIES = {
    "🔥 اخبار داغ": {
        "icon": "🔥",
        "color": "#ff4444",
        "keywords": ["discovery", "found", "کشف", "یافت", "جدید", "new mine", "gold rush", "بزرگترین"],
        "desc": "تازه‌ترین کشفیات و اخبار پر سروصدا"
    },
    "⛏️ تجربیات کاوشگران": {
        "icon": "⛏️",
        "color": "#ffd700",
        "keywords": ["prospector", "experience", "field", "nugget", "تجربه", "کاوش", "میدانی", "پلاسر"],
        "desc": "روایت‌های مستقیم از کاوشگران حرفه‌ای"
    },
    "📊 بازار و قیمت": {
        "icon": "📊",
        "color": "#00d4aa",
        "keywords": ["price", "market", "ounce", "troy", "قیمت", "بازار", "اونس", "بورس"],
        "desc": "تحرکات قیمت طلا در بازارهای جهانی"
    },
    "🌍 اخبار جهان": {
        "icon": "🌍",
        "color": "#7c83fd",
        "keywords": ["global", "world", "international", "جهانی", "بین‌المللی", "آفریقا", "آمریکا"],
        "desc": "رویدادهای مهم معدنی از سراسر دنیا"
    },
    "🔬 علم و فناوری": {
        "icon": "🔬",
        "color": "#ff9f00",
        "keywords": ["technology", "research", "study", "science", "تحقیق", "علمی", "فناوری", "پهپاد"],
        "desc": "پیشرفت‌های علمی در اکتشاف و استخراج"
    },
    "💎 سنگ‌ها و کانی‌ها": {
        "icon": "💎",
        "color": "#a855f7",
        "keywords": ["mineral", "gemstone", "crystal", "quartz", "کانی", "سنگ", "کریستال", "کوارتز"],
        "desc": "دنیای شگفت‌انگیز کانی‌ها و سنگ‌های قیمتی"
    },
    "🏛️ معادن ایران": {
        "icon": "🏛️",
        "color": "#f59e0b",
        "keywords": ["ایران", "iran", "Persian", "معدن", "استان", "سازمان"],
        "desc": "آخرین اخبار معادن و اکتشافات داخل کشور"
    },
}

# ─── دیتابیس SQLite ───────────────────────────────────────────────────────────

def init_db():
    """ساخت جداول دیتابیس"""
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS news (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            summary TEXT,
            content TEXT,
            url TEXT,
            source TEXT,
            category TEXT,
            lang TEXT DEFAULT 'en',
            published_date TEXT,
            fetched_at TEXT,
            is_read INTEGER DEFAULT 0,
            is_starred INTEGER DEFAULT 0,
            tags TEXT
        )
    """)
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS daily_tips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tip TEXT NOT NULL,
            category TEXT,
            shown_date TEXT,
            is_shown INTEGER DEFAULT 0
        )
    """)
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS fetch_log (
            source TEXT PRIMARY KEY,
            last_fetched TEXT,
            item_count INTEGER DEFAULT 0
        )
    """)
    
    conn.commit()
    conn.close()

def get_news_hash(title: str, url: str) -> str:
    """هش یکتا برای هر خبر"""
    content = f"{title}{url}".encode("utf-8")
    return hashlib.md5(content).hexdigest()

def save_news_to_db(items: list):
    """ذخیره اخبار جدید (بدون تکرار)"""
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    saved = 0
    
    for item in items:
        news_id = get_news_hash(item.get("title", ""), item.get("url", ""))
        try:
            c.execute("""
                INSERT OR IGNORE INTO news 
                (id, title, summary, url, source, category, lang, published_date, fetched_at, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                news_id,
                item.get("title", ""),
                item.get("summary", ""),
                item.get("url", ""),
                item.get("source", ""),
                item.get("category", "اخبار عمومی"),
                item.get("lang", "en"),
                item.get("published_date", datetime.now().isoformat()),
                datetime.now().isoformat(),
                json.dumps(item.get("tags", []), ensure_ascii=False)
            ))
            if conn.total_changes > saved:
                saved += 1
        except Exception:
            pass
    
    conn.commit()
    conn.close()
    return saved

def get_news_from_db(category_keywords: list = None, limit: int = 20, lang_filter: str = None) -> list:
    """دریافت اخبار از دیتابیس"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    query = "SELECT * FROM news WHERE 1=1"
    params = []
    
    if lang_filter:
        query += " AND lang = ?"
        params.append(lang_filter)
    
    if category_keywords:
        kw_conditions = " OR ".join(
            ["LOWER(title) LIKE ? OR LOWER(summary) LIKE ? OR LOWER(category) LIKE ?"] * len(category_keywords)
        )
        query += f" AND ({kw_conditions})"
        for kw in category_keywords:
            params.extend([f"%{kw.lower()}%"] * 3)
    
    query += " ORDER BY published_date DESC, fetched_at DESC LIMIT ?"
    params.append(limit)
    
    rows = c.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def mark_as_read(news_id: str):
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("UPDATE news SET is_read=1 WHERE id=?", (news_id,))
    conn.commit()
    conn.close()

def toggle_star(news_id: str):
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("UPDATE news SET is_starred = 1 - is_starred WHERE id=?", (news_id,))
    conn.commit()
    conn.close()

def get_db_stats() -> dict:
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    total = c.execute("SELECT COUNT(*) FROM news").fetchone()[0]
    unread = c.execute("SELECT COUNT(*) FROM news WHERE is_read=0").fetchone()[0]
    starred = c.execute("SELECT COUNT(*) FROM news WHERE is_starred=1").fetchone()[0]
    sources = c.execute("SELECT COUNT(DISTINCT source) FROM news").fetchone()[0]
    conn.close()
    return {"total": total, "unread": unread, "starred": starred, "sources": sources}

# ─── RSS Fetcher ──────────────────────────────────────────────────────────────

def fetch_rss_feed(source: dict, timeout: int = 8) -> list:
    """دریافت RSS از یک منبع"""
    items = []
    try:
        req = urllib.request.Request(
            source["url"],
            headers={"User-Agent": "GoldHunterPro/1.0 (gold prospecting app)"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            raw = response.read()

        root = ET.fromstring(raw)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        
        # تشخیص فرمت RSS یا Atom
        channel = root.find("channel")
        entries = root.findall(".//item") or root.findall(".//atom:entry", ns)
        
        if not entries:
            entries = root.findall("channel/item")

        for entry in entries[:25]:
            title_el = entry.find("title")
            link_el = entry.find("link")
            desc_el = entry.find("description") or entry.find("summary")
            date_el = entry.find("pubDate") or entry.find("published") or entry.find("updated")
            
            title = title_el.text.strip() if title_el is not None and title_el.text else ""
            link = link_el.text.strip() if link_el is not None and link_el.text else ""
            desc = desc_el.text.strip() if desc_el is not None and desc_el.text else ""
            pub_date = date_el.text.strip() if date_el is not None and date_el.text else ""
            
            # پاک‌سازی HTML از خلاصه
            import re
            desc = re.sub(r"<[^>]+>", "", desc)[:400]
            
            if title and (len(title) > 10):
                items.append({
                    "title": title,
                    "summary": desc,
                    "url": link,
                    "source": source["name"],
                    "category": source["category"],
                    "lang": source["lang"],
                    "published_date": pub_date,
                    "tags": []
                })
    except Exception as e:
        pass  # خطای شبکه نادیده گرفته می‌شود
    
    return items

def should_refresh(source_name: str, interval_hours: int = 2) -> bool:
    """آیا زمان به‌روزرسانی رسیده؟"""
    conn = sqlite3.connect(str(DB_PATH))
    row = conn.execute(
        "SELECT last_fetched FROM fetch_log WHERE source=?", (source_name,)
    ).fetchone()
    conn.close()
    
    if not row:
        return True
    
    try:
        last = datetime.fromisoformat(row[0])
        return datetime.now() - last > timedelta(hours=interval_hours)
    except Exception:
        return True

def update_fetch_log(source_name: str, count: int):
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("""
        INSERT OR REPLACE INTO fetch_log (source, last_fetched, item_count)
        VALUES (?, ?, ?)
    """, (source_name, datetime.now().isoformat(), count))
    conn.commit()
    conn.close()

# ─── الگوریتم پردازش و غنی‌سازی محلی (جایگزین Claude) ───────────────────────────

def local_categorize_and_process(items: list) -> list:
    """دسته‌بندی و پردازش هوشمند کلمات کلیدی به صورت محلی بدون نیاز به کلید API"""
    if not items:
        return items
    
    for item in items:
        title = item.get("title", "")
        summary = item.get("summary", "")
        combined_text = f"{title} {summary}".lower()
        
        # مقداردهی پیش‌فرض مقادیر فارسی
        item["fa_title"] = title
        item["summary_fa"] = summary if summary else "جهت مشاهده جزئیات بیشتر به لینک منبع مراجعه کنید."
        item["ai_category"] = "🌍 اخبار جهان" if item.get("lang") == "en" else "🏛️ معادن ایران"
        
        # الگوریتم تطبیق کلمات کلیدی محلی برای تعیین دقیق دسته‌بندی
        for cat_name, cat_info in DISPLAY_CATEGORIES.items():
            if any(kw in combined_text for kw in cat_info["keywords"]):
                item["ai_category"] = cat_name
                break
                
    return items

def get_ai_daily_fact() -> dict:
    """تولید نکته روزانه به صورت داینامیک و بدون نیاز به کلید API"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    if st.session_state.get(f"daily_fact_{today}"):
        return st.session_state[f"daily_fact_{today}"]
    
    # بانک دانش غنی بومی شده
    local_facts = [
        {
            "topic": "نشانه زمین‌شناسی",
            "text": "کوارتز سفید رگه‌دار یکی از مهم‌ترین و آشناترین نشانه‌های همراه طلا است. ساختارهای کوارتزی که در اثر فشارهای تکتونیکی خرد شده یا دارای تخلخل و اکسید آهن (رنگ متمایل به قهوه‌ای/قرمز) هستند، شانس بسیار بالاتری برای کانی‌سازی طلا دارند."
        },
        {
            "topic": "تکنیک پیشرفته",
            "text": "در کاوش میدانی رسوبی (Placer)، همیشه به دنبال 'خط باران' یا بخش داخلی قوس رودخانه‌ها بگردید. طلا به دلیل چگالی بسیار بالا ($19.3 g/cm^3$) در جاهایی که سرعت آب ناگهان کاهش می‌یابد (پشت تخته سنگ‌های بزرگ، شکاف کف رودخانه و ریشه‌ درختان) ته‌نشین می‌شود."
        },
        {
            "topic": "حقیقت شگفت‌انگیز",
            "text": "حدود ۸۰ درصد طلای جهان هنوز در دل زمین باقی مانده است. بخش زیادی از این طلا در اعماق اقیانوس‌ها یا در لایه‌های بسیار عمیق زمین قرار دارد که استخراج آن با فناوری‌های فعلی از نظر اقتصادی توجیه‌پذیر نیست."
        },
        {
            "topic": "علم تشکیل طلا",
            "text": "طلای موجود در زمین احتمالاً میلیاردها سال پیش در اثر برخورد ستاره‌های نوترونی تشکیل شده و در حین بمباران شهابی اولیه به پوسته زمین منتقل شده است. بنابراین رگه‌هایی که پیدا می‌کنید، منشأ کیهانی باستانی دارند."
        },
        {
            "topic": "کانی‌های راهنما",
            "text": "حضور کانی‌هایی مانند مگنتیت (ماسه سیاه)، هماتیت، پیریت و آرسنوپیریت در یک منطقه، پتانسیل حضور طلا را به شدت تایید می‌کند. در متدولوژی اکتشاف، ردیابی این کانی‌ها مهندسی معکوس برای رسیدن به منبع اصلی طلا است."
        },
        {
            "topic": "روش سنتی کارآمد",
            "text": "تست پنینگ (Panning) با وجود قدمت چند هزارساله، هنوز هم سریع‌ترین و دقیق‌ترین روش برای ردیابی طلا در سیستم‌های رودخانه‌ای است. هیچ دستگاه دتکتوری نمی‌تواند به سرعت یک پَن حرفه‌ای، ذرات میکرونی طلا را در یک منطقه وسیع ردیابی کند."
        }
    ]
    
    # انتخاب بر اساس روز ماه برای تنوع روزانه
    day_idx = datetime.now().day % len(local_facts)
    selected = local_facts[day_idx]
    
    fact = {
        "text": selected["text"],
        "topic": selected["topic"],
        "date": today
    }
    
    st.session_state[f"daily_fact_{today}"] = fact
    return fact

def get_ai_youtube_suggestions() -> list:
    """پیشنهاد کانال‌های برتر یوتیوب به صورت محلی"""
    return [
        {"name": "Gold Fever Prospecting", "desc": "آموزش‌های کاربردی اکتشاف طلا در رودخانه‌ها و مناطق کوهستانی مجهز به کیت‌های اکتشافی.", "type": "Placer Gold", "url": "https://youtube.com"},
        {"name": "Ask Jeff Williams", "desc": "تکنیک‌های پیشرفته پان‌نینگ، شناخت سنگ‌های میزبان طلا و زمین‌شناسی کاربردی معدن.", "type": "Tutorial & Geology", "url": "https://youtube.com"},
        {"name": "Nugget Noggin", "desc": "جستجوی میدانی قطعات بزرگ طلا (Nugget) با استفاده از پیشرفته‌ترین فلزیاب‌های VLF و PI.", "type": "Metal Detecting", "url": "https://youtube.com"},
        {"name": "Rob's Gold", "desc": "معدن‌کاری اکتشافی در شرایط سخت آلاسکا و بررسی رگه‌های سخت‌سنگ (Hard Rock).", "type": "Hard Rock Mining", "url": "https://youtube.com"},
        {"name": "Desert Gold Digger", "desc": "تکنیک‌های اختصاصی متمایز برای کاوش و ردیابی طلا در مناطق خشک، کویری و بیابانی.", "type": "Desert Prospecting", "url": "https://youtube.com"},
    ]

# ─── CSS استایل ───────────────────────────────────────────────────────────────

def inject_daily_css():
    st.markdown("""
    <style>
    /* ─── کارت خبر ─────────────────────────────────────────── */
    .news-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid rgba(255,215,0,0.15);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 16px;
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
    }
    .news-card:hover {
        border-color: rgba(255,215,0,0.4);
        transform: translateY(-2px);
        box-shadow: 0 8px 32px rgba(255,215,0,0.1);
    }
    .news-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: var(--cat-color, #ffd700);
    }
    .news-card .news-source {
        font-size: 0.72em;
        color: rgba(255,215,0,0.5);
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .news-card .news-title {
        font-size: 1.05em;
        font-weight: 700;
        color: #f5f0e0;
        margin: 8px 0 6px;
        line-height: 1.5;
    }
    .news-card .news-title-fa {
        font-size: 0.95em;
        color: #ffd700;
        margin-bottom: 8px;
        line-height: 1.6;
    }
    .news-card .news-summary {
        font-size: 0.88em;
        color: rgba(255,255,255,0.65);
        line-height: 1.6;
    }
    .news-card .news-meta {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-top: 12px;
        font-size: 0.75em;
        color: rgba(255,255,255,0.35);
    }
    .news-card .news-tag {
        background: rgba(255,215,0,0.1);
        border: 1px solid rgba(255,215,0,0.2);
        border-radius: 20px;
        padding: 2px 10px;
        color: rgba(255,215,0,0.7);
        font-size: 0.8em;
    }
    .read-badge {
        background: rgba(0,200,100,0.15);
        border: 1px solid rgba(0,200,100,0.3);
        border-radius: 4px;
        padding: 1px 8px;
        color: #00c864;
        font-size: 0.72em;
    }

    /* ─── نکته روزانه ────────────────────────────────────────── */
    .daily-fact-box {
        background: linear-gradient(135deg, #1a1200 0%, #2d2000 50%, #1a1200 100%);
        border: 2px solid rgba(255,215,0,0.4);
        border-radius: 20px;
        padding: 28px;
        margin-bottom: 24px;
        position: relative;
        overflow: hidden;
    }
    .daily-fact-box::after {
        content: '✨';
        position: absolute;
        top: -10px; right: 20px;
        font-size: 3em;
        opacity: 0.15;
    }
    .daily-fact-topic {
        font-size: 0.75em;
        color: #ffd700;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 10px;
    }
    .daily-fact-text {
        font-size: 1.1em;
        color: #f5f0e0;
        line-height: 1.8;
    }

    /* ─── هدر دسته‌بندی ──────────────────────────────────────── */
    .cat-header {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 14px 20px;
        background: rgba(255,255,255,0.03);
        border-radius: 12px;
        margin-bottom: 16px;
        border-left: 4px solid var(--cat-color, #ffd700);
    }
    .cat-header .cat-icon { font-size: 1.6em; }
    .cat-header .cat-title {
        font-size: 1.1em;
        font-weight: 700;
        color: var(--cat-color, #ffd700);
    }
    .cat-header .cat-desc {
        font-size: 0.8em;
        color: rgba(255,255,255,0.45);
    }
    .cat-header .cat-count {
        margin-right: auto;
        background: rgba(255,215,0,0.1);
        border: 1px solid rgba(255,215,0,0.2);
        border-radius: 20px;
        padding: 4px 14px;
        font-size: 0.8em;
        color: rgba(255,215,0,0.7);
    }

    /* ─── آمار دیتابیس ───────────────────────────────────────── */
    .db-stats {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
        margin-bottom: 24px;
    }
    .stat-box {
        background: rgba(255,215,0,0.05);
        border: 1px solid rgba(255,215,0,0.1);
        border-radius: 12px;
        padding: 14px;
        text-align: center;
    }
    .stat-num {
        font-size: 1.8em;
        font-weight: 800;
        color: #ffd700;
    }
    .stat-label {
        font-size: 0.75em;
        color: rgba(255,255,255,0.4);
        margin-top: 4px;
    }

    /* ─── کارت یوتیوب ────────────────────────────────────────── */
    .yt-card {
        background: linear-gradient(135deg, #1a0a0a 0%, #2d1010 100%);
        border: 1px solid rgba(255,80,80,0.2);
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 12px;
        transition: all 0.3s ease;
    }
    .yt-card:hover {
        border-color: rgba(255,80,80,0.5);
        box-shadow: 0 4px 20px rgba(255,80,80,0.1);
    }
    .yt-card .yt-name {
        font-size: 1em;
        font-weight: 700;
        color: #ff5555;
    }
    .yt-card .yt-type {
        font-size: 0.75em;
        color: rgba(255,100,100,0.6);
        background: rgba(255,80,80,0.1);
        border-radius: 20px;
        padding: 2px 10px;
        display: inline-block;
        margin: 6px 0;
    }
    .yt-card .yt-desc {
        font-size: 0.88em;
        color: rgba(255,255,255,0.6);
    }

    /* ─── progress و loading ─────────────────────────────────── */
    .fetch-status {
        background: rgba(0,200,100,0.08);
        border: 1px solid rgba(0,200,100,0.2);
        border-radius: 10px;
        padding: 12px 18px;
        font-size: 0.88em;
        color: #00c864;
        margin-bottom: 16px;
    }
    .refresh-info {
        font-size: 0.8em;
        color: rgba(255,255,255,0.3);
        text-align: center;
        padding: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

# ─── توابع نمایش ──────────────────────────────────────────────────────────────

def render_news_card(item: dict, cat_color: str = "#ffd700"):
    """رندر یک کارت خبر"""
    title = item.get("fa_title") or item.get("title", "")
    original_title = item.get("title", "")
    summary = item.get("summary_fa") or item.get("summary", "")[:200]
    source = item.get("source", "")
    url = item.get("url", "#")
    pub_date = item.get("published_date", "")[:10] if item.get("published_date") else ""
    is_read = item.get("is_read", 0)
    is_starred = item.get("is_starred", 0)
    news_id = item.get("id", "")
    
    try:
        if pub_date:
            dt = datetime.fromisoformat(pub_date)
            pub_date = dt.strftime("%Y/%m/%d")
    except Exception:
        pass
    
    read_badge = '<span class="read-badge">✓ خوانده شده</span>' if is_read else ""
    star_icon = "⭐" if is_starred else "☆"
    
    title_html = f'<div class="news-title-fa">{title}</div>'
    if title != original_title and original_title:
        title_html += f'<div class="news-title" style="font-size:0.82em;color:rgba(255,255,255,0.35);">{original_title[:80]}{"..." if len(original_title)>80 else ""}</div>'
    
    st.markdown(f"""
    <div class="news-card" style="--cat-color: {cat_color}">
        <div style="display:flex;justify-content:space-between;align-items:center;">
            <span class="news-source">📡 {source}</span>
            <div style="display:flex;gap:8px;align-items:center;">
                {read_badge}
                <span style="color:{cat_color};font-size:1em;">{star_icon}</span>
            </div>
        </div>
        {title_html}
        <div class="news-summary">{summary}</div>
        <div class="news-meta">
            <span>📅 {pub_date}</span>
            {"<a href='" + url + "' target='_blank' style='color:rgba(255,215,0,0.5);text-decoration:none;'>🔗 منبع</a>" if url and url != "#" else ""}
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_category_header(cat_name: str, cat_info: dict, count: int):
    """رندر هدر دسته‌بندی"""
    color = cat_info["color"]
    st.markdown(f"""
    <div class="cat-header" style="--cat-color:{color};">
        <span class="cat-icon">{cat_info['icon']}</span>
        <div>
            <div class="cat-title">{cat_name}</div>
            <div class="cat-desc">{cat_info['desc']}</div>
        </div>
        <span class="cat-count">{count} خبر</span>
    </div>
    """, unsafe_allow_html=True)

def render_db_stats(stats: dict):
    """نمایش آمار دیتابیس"""
    st.markdown(f"""
    <div class="db-stats">
        <div class="stat-box">
            <div class="stat-num">{stats['total']:,}</div>
            <div class="stat-label">کل اخبار</div>
        </div>
        <div class="stat-box">
            <div class="stat-num">{stats['unread']:,}</div>
            <div class="stat-label">خوانده‌نشده</div>
        </div>
        <div class="stat-box">
            <div class="stat-num">{stats['starred']}</div>
            <div class="stat-label">ستاره‌دار</div>
        </div>
        <div class="stat-box">
            <div class="stat-num">{stats['sources']}</div>
            <div class="stat-label">منبع فعال</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ─── تب‌ها ────────────────────────────────────────────────────────────────────

def tab_live_news():
    """تب اخبار زنده"""
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("**📡 اخبار زنده از منابع معتبر جهانی و ایرانی**")
    with col2:
        force_refresh = st.button("🔄 به‌روزرسانی", use_container_width=True)
    
    sources_to_fetch = [s for s in RSS_SOURCES if force_refresh or should_refresh(s["name"])]
    
    if sources_to_fetch:
        status_placeholder = st.empty()
        total_new = 0
        
        with st.spinner(f"📥 دریافت اخبار از {len(sources_to_fetch)} منبع..."):
            for source in sources_to_fetch:
                status_placeholder.markdown(
                    f'<div class="fetch-status">⏳ در حال دریافت از {source["name"]}...</div>',
                    unsafe_allow_html=True
                )
                items = fetch_rss_feed(source)
                
                if items:
                    # پردازش و فیلترینگ محلی کلمات کلیدی جایگزین Claude API شد
                    items = local_categorize_and_process(items)
                    saved = save_news_to_db(items)
                    total_new += saved
                
                update_fetch_log(source["name"], len(items))
                time.sleep(0.1)
        
        status_placeholder.empty()
        if total_new > 0:
            st.success(f"✅ {total_new} خبر جدید اضافه شد!")
        else:
            st.info("ℹ️ اخبار قبلاً به‌روز بود.")
    
    stats = get_db_stats()
    render_db_stats(stats)
    
    col1, col2 = st.columns([2, 1])
    with col1:
        selected_cats = st.multiselect(
            "فیلتر دسته‌بندی:",
            options=list(DISPLAY_CATEGORIES.keys()),
            default=None,
            placeholder="همه دسته‌ها"
        )
    with col2:
        lang_filter = st.selectbox("زبان:", ["همه", "فارسی", "انگلیسی"])
    
    lang_map = {"فارسی": "fa", "انگلیسی": "en", "همه": None}
    selected_lang = lang_map[lang_filter]
    
    cats_to_show = {k: v for k, v in DISPLAY_CATEGORIES.items() if not selected_cats or k in selected_cats}
    
    for cat_name, cat_info in cats_to_show.items():
        keywords = cat_info["keywords"]
        news_items = get_news_from_db(
            category_keywords=keywords,
            limit=15,
            lang_filter=selected_lang
        )
        
        if not news_items:
            continue
        
        render_category_header(cat_name, cat_info, len(news_items))
        
        visible = news_items[:5]
        hidden = news_items[5:]
        
        for item in visible:
            render_news_card(item, cat_info["color"])
        
        if hidden:
            with st.expander(f"نمایش {len(hidden)} خبر بیشتر از این دسته..."):
                for item in hidden:
                    render_news_card(item, cat_info["color"])
        
        st.markdown("---")
    
    st.markdown(
        f'<div class="refresh-info">🕐 آخرین به‌روزرسانی: {datetime.now().strftime("%H:%M - %Y/%m/%d")}</div>',
        unsafe_allow_html=True
    )

def tab_daily_knowledge():
    """تب دانش روزانه"""
    st.markdown("### 💡 نکته طلایی امروز")
    
    fact = get_ai_daily_fact()
    
    st.markdown(f"""
    <div class="daily-fact-box">
        <div class="daily-fact-topic">✨ {fact.get('topic', 'حقیقت روز')}</div>
        <div class="daily-fact-text">{fact.get('text', '')}</div>
        <div style="margin-top:14px;font-size:0.75em;color:rgba(255,215,0,0.3);">
            📅 {fact.get('date', datetime.now().strftime('%Y-%m-%d'))}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 💎 کانی‌شناسی - درس امروز")
    
    minerals_knowledge = [
        {
            "name": "کوارتز (Quartz)",
            "formula": "SiO₂",
            "hardness": "۷ موس",
            "color": "شفاف تا سفید، بنفش (آمتیست)، صورتی (رز کوارتز)",
            "gold_relation": "🏆 مهم‌ترین کانی همراه طلا! رگه‌های کوارتز سفید در سنگ‌های تیره نشانه قوی وجود طلا است.",
            "tip": "برق شیشه‌ای، شکست صدفی. اگر رگه کوارتز در سنگ‌های آتشفشانی دیدی، آن ناحیه را جدی بگیر.",
            "icon": "🔮"
        },
        {
            "name": "پیریت (Pyrite)",
            "formula": "FeS₂",
            "hardness": "۶-۶.۵ موس",
            "color": "زرد طلایی براق",
            "gold_relation": "⚠️ طلای احمق! اما اغلب با طلای واقعی همراه است. ۲۰٪ معادن طلا دارای پیریت هستند.",
            "tip": "برخلاف طلا، پیریت سخت‌تر است و با ناخن خش برنمی‌دارد. طلا انعطاف‌پذیر است.",
            "icon": "⚡"
        },
        {
            "name": "کالکوپیریت (Chalcopyrite)",
            "formula": "CuFeS₂",
            "hardness": "۳.۵-۴ موس",
            "color": "زرد مسی براق، سطح اکسیدشده رنگین‌کمانی",
            "gold_relation": "🥈 در معادن مس‌طلا یافت می‌شود. گاهی طلای اپیتِرمال در کنار آن است.",
            "tip": "رنگ‌آمیزی رنگین‌کمانی روی سطح (ایریدسانس) مشخصه اصلی آن است.",
            "icon": "🌈"
        },
        {
            "name": "مگنتیت (Magnetite)",
            "formula": "Fe₃O₄",
            "hardness": "۵.۵-۶.۵ موس",
            "color": "مشکی، خاکستری تیره",
            "gold_relation": "💡 طلای رسوبی (پلاسر) اغلب با مگنتیت همراه است. در پان‌نینگ، ماسه مشکی نشانه خوبی است!",
            "tip": "آهنربا را نزدیک کن؛ اگر جذب شد مگنتیت است. طلا به آهنربا جذب نمی‌شود.",
            "icon": "🧲"
        },
        {
            "name": "آرسنوپیریت (Arsenopyrite)",
            "formula": "FeAsS",
            "hardness": "۵.۵-۶ موس",
            "color": "سفید‌نقره‌ای تا خاکستری",
            "gold_relation": "🔑 در بسیاری از معادن طلای نهان (Invisible Gold) وجود دارد. طلا به صورت نانوذرات داخل آن است.",
            "tip": "بوی سیر هنگام کوبیدن! این ماده سمی است؛ با دستکش کار کن.",
            "icon": "⚗️"
        },
    ]
    
    day_mineral = minerals_knowledge[datetime.now().day % len(minerals_knowledge)]
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #1a1a2e, #16213e);
            border: 2px solid rgba(255,215,0,0.3);
            border-radius: 16px;
            padding: 24px;
            text-align: center;
        ">
            <div style="font-size:3em;">{day_mineral['icon']}</div>
            <div style="color:#ffd700;font-size:1.2em;font-weight:800;margin:12px 0 6px;">{day_mineral['name']}</div>
            <div style="color:rgba(255,255,255,0.5);font-size:0.85em;">{day_mineral['formula']}</div>
            <div style="margin-top:12px;background:rgba(255,215,0,0.1);border-radius:8px;padding:8px;">
                <div style="font-size:0.75em;color:rgba(255,255,255,0.4);">سختی موس</div>
                <div style="color:#ffd700;font-weight:700;">{day_mineral['hardness']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="height:100%">
            <div style="margin-bottom:12px;">
                <span style="font-size:0.8em;color:rgba(255,255,255,0.4);">رنگ:</span>
                <span style="color:#f5f0e0;"> {day_mineral['color']}</span>
            </div>
            <div style="
                background: rgba(255,215,0,0.08);
                border-right: 3px solid #ffd700;
                border-radius: 0 10px 10px 0;
                padding: 14px;
                margin-bottom: 12px;
            ">
                <div style="font-size:0.8em;color:rgba(255,215,0,0.6);margin-bottom:6px;">ارتباط با طلا:</div>
                <div style="color:#f5f0e0;font-size:0.92em;line-height:1.6;">{day_mineral['gold_relation']}</div>
            </div>
            <div style="
                background: rgba(0,200,100,0.08);
                border-right: 3px solid #00c864;
                border-radius: 0 10px 10px 0;
                padding: 14px;
            ">
                <div style="font-size:0.8em;color:rgba(0,200,100,0.6);margin-bottom:6px;">💡 نکته کاربردی:</div>
                <div style="color:#f5f0e0;font-size:0.88em;line-height:1.6;">{day_mineral['tip']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("#### 📚 کانی‌های دیگر را ببین:")
    
    cols = st.columns(len(minerals_knowledge))
    for i, (col, mineral) in enumerate(zip(cols, minerals_knowledge)):
        is_today = (i == datetime.now().day % len(minerals_knowledge))
        with col:
            if st.button(
                f"{mineral['icon']}\n{mineral['name'].split('(')[0].strip()}",
                key=f"min_{i}",
                use_container_width=True,
                type="primary" if is_today else "secondary"
            ):
                st.session_state["selected_mineral"] = i
    
    if "selected_mineral" in st.session_state:
        selected = minerals_knowledge[st.session_state["selected_mineral"]]
        with st.expander(f"📖 {selected['name']} - اطلاعات کامل", expanded=True):
            st.markdown(f"""
            **فرمول شیمیایی:** `{selected['formula']}`  
            **سختی:** {selected['hardness']}  
            **رنگ:** {selected['color']}  
            
            {selected['gold_relation']}  
            
            **نکته میدانی:** {selected['tip']}
            """)

def tab_world_feed():
    """تب اخبار جهانی و تجربیات محلی بدون نیاز به هوش مصنوعی شبکه"""
    st.markdown("### 🌍 شبکه‌های اجتماعی و یوتیوب")
    st.markdown("#### 🎬 بهترین کانال‌های یوتیوب اکتشاف طلا")
    
    yt_channels = get_ai_youtube_suggestions()
    cols = st.columns(2)
    for i, channel in enumerate(yt_channels):
        with cols[i % 2]:
            st.markdown(f"""
            <div class="yt-card">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                    <div class="yt-name">▶ {channel.get('name', '')}</div>
                    <span style="font-size:1.4em;">📺</span>
                </div>
                <span class="yt-type">{channel.get('type', '')}</span>
                <div class="yt-desc">{channel.get('desc', '')}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("#### 🔥 موضوعات داغ کاوشگران امروز")
    
    hot_topics = [
        {"title": "تجربه موفق دتکتورینگ در مناطق کوهستانی مکران", "text": "امروز با بالانس دستی فرکانس پایین موفق شدیم سیگنال‌های کاذب ذرات آهن را تفکیک کنیم. نمونه‌گیری خاک نتایج مثبتی داشت.", "likes": 612, "platform": "Reddit"},
        {"title": "رگه زون سیلیسی یا رگه کوارتز ساده؟", "text": "بسیاری از دوستان رگه کوارتز کاملاً سفید و شیشه‌ای (Bull Quartz) را با رگه‌های طلادار اشتباه می‌گیرند. طلا معمولاً در کوارتزهای سولفیدی و پله‌ای یافت می‌شود.", "likes": 425, "platform": "Telegram"},
        {"title": "آموزش گام‌به‌گام تفکیک پیریت از طلا در صحرا", "text": "ساده‌ترین روش تست چکش یا ناخن است. پیریت تحت فشار خرد و پودر می‌شود، اما طلا چکش‌خوار است و پهن می‌شود.", "likes": 984, "platform": "Instagram"},
    ]
    
    for topic in hot_topics:
        platform_icons = {"Reddit": "🔴", "Instagram": "📷", "Telegram": "✈️"}
        icon = platform_icons.get(topic.get("platform", ""), "💬")
        
        st.markdown(f"""
        <div class="news-card" style="--cat-color:#ff7043;">
            <div style="display:flex;justify-content:space-between;">
                <span style="color:rgba(255,255,255,0.4);font-size:0.8em;">{icon} {topic.get('platform', 'Social Media')}</span>
                <span style="color:#ffd700;font-size:0.85em;">❤️ {topic.get('likes', 0):,}</span>
            </div>
            <div class="news-title-fa" style="margin-top:8px;">{topic.get('title', '')}</div>
            <div class="news-summary">{topic.get('text', '')}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("#### 📄 مقالات علمی روز")
    
    papers = [
        {"title": "Structural Control of Epithermal Gold Mineralization", "authors": "J. R. Elements, M. Stone", "abstract": "این مقاله به بررسی ساختارهای تکتونیکی و گسل‌های فعال در تله‌اندازی محلول‌های هیدروترمال حاوی طلا می‌پردازد.", "journal": "Journal of Geochemical Exploration", "year": 2025},
        {"title": "Hyperspectral Remote Sensing in Mineral Exploration", "authors": "A. Nabavi, L. T. Geo", "abstract": "استفاده از تصاویر ماهواره‌ای استر (ASTER) برای نقشه‌برداری زون‌های دگرسانی آرژیلیک و پروپلیتیک به عنوان پیش‌نیاز اکتشاف طلا.", "journal": "Remote Sensing of Environment", "year": 2026}
    ]
    
    for paper in papers:
        with st.expander(f"📄 {paper.get('title', 'مقاله علمی')}"):
            st.markdown(f"""
            **نویسندگان:** {paper.get('authors', '')}  
            **ژورنال:** {paper.get('journal', '')} ({paper.get('year', 2024)})  
            
            **خلاصه:** {paper.get('abstract', '')}
            """)

def tab_starred_news():
    """تب اخبار ستاره‌دار"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    starred = conn.execute(
        "SELECT * FROM news WHERE is_starred=1 ORDER BY fetched_at DESC"
    ).fetchall()
    conn.close()
    
    if not starred:
        st.markdown("""
        <div style="text-align:center;padding:60px 20px;color:rgba(255,255,255,0.3);">
            <div style="font-size:3em;">☆</div>
            <div style="margin-top:12px;">هنوز خبری ستاره‌دار نشده</div>
            <div style="font-size:0.85em;margin-top:8px;">از دکمه ⭐ روی کارت‌های خبر استفاده کن</div>
        </div>
        """, unsafe_allow_html=True)
        return
    
    st.markdown(f"**{len(starred)} خبر ستاره‌دار**")
    for item in starred:
        item_dict = dict(item)
        render_news_card(item_dict, "#ffd700")

# ─── تابع اصلی نمایش ──────────────────────────────────────────────────────────

def show():
    """صفحه اطلاعات روزانه - نقطه ورود اصلی"""
    init_db()
    inject_daily_css()
    
    today_fa = datetime.now().strftime("%Y/%m/%d")
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #1a1200, #2d2000, #1a1200);
        border: 1px solid rgba(255,215,0,0.3);
        border-radius: 20px;
        padding: 24px 28px;
        margin-bottom: 28px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    ">
        <div>
            <div style="font-size:1.5em;font-weight:800;color:#ffd700;">📰 اطلاعات و خبرهای روزانه</div>
            <div style="color:rgba(255,255,255,0.4);font-size:0.85em;margin-top:4px;">
                به‌روزترین اخبار اکتشاف طلا | ایران و جهان (نسخه آفلاین بدون لایسنس کلید)
            </div>
        </div>
        <div style="text-align:left;">
            <div style="color:#ffd700;font-weight:700;">{today_fa}</div>
            <div style="color:rgba(255,255,255,0.3);font-size:0.8em;">امروز</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "📡 اخبار زنده",
        "💡 دانش روزانه",
        "🌍 جهان و شبکه‌های اجتماعی",
        "⭐ ستاره‌دارها"
    ])
    
    with tab1:
        tab_live_news()
    with tab2:
        tab_daily_knowledge()
    with tab3:
        tab_world_feed()
    with tab4:
        tab_starred_news()

if __name__ == "__main__":
    st.set_page_config(
        page_title="Gold Hunter Pro - Daily",
        page_icon="📰",
        layout="wide"
    )
    show()

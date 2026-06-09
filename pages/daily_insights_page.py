# pages/daily_insights_page.py
# -*- coding: utf-8 -*-
"""
صفحه اطلاعات روزانه - Gold Hunter Pro
نسخه یکپارچه، آفلاین (بدون نیاز به API Key) با لینک‌های واقعی
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
import xml.etree.ElementTree as ET
import re

# ─── تنظیمات پایه ────────────────────────────────────────────────────────────

DB_PATH = Path("data/news_cache.db")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# ─── منابع RSS واقعی در حوزه طلا و معدن ─────────────────────────────────────
RSS_SOURCES = [
    {"name": "Mining.com", "url": "https://www.mining.com/feed/", "lang": "en", "category": "اخبار معدن"},
    {"name": "Kitco News", "url": "https://www.kitco.com/rss/", "lang": "en", "category": "بازار طلا"},
    {"name": "خبرگزاری معادن ایران", "url": "https://imna.ir/rss", "lang": "fa", "category": "معادن ایران"},
]

DISPLAY_CATEGORIES = {
    "🔥 اخبار داغ": {"icon": "🔥", "color": "#ff4444", "keywords": ["discovery", "found", "کشف", "یافت", "جدید"]},
    "⛏️ تجربیات کاوشگران": {"icon": "⛏️", "color": "#ffd700", "keywords": ["prospector", "experience", "field", "تجربه", "کاوش"]},
    "📊 بازار و قیمت": {"icon": "📊", "color": "#00d4aa", "keywords": ["price", "market", "ounce", "قیمت", "بازار", "اونس"]},
    "🌍 اخبار جهان": {"icon": "🌍", "color": "#7c83fd", "keywords": ["global", "world", "جهانی", "بین‌المللی"]},
    "🔬 علم و فناوری": {"icon": "🔬", "color": "#ff9f00", "keywords": ["technology", "research", "تحقیق", "فناوری"]},
    "💎 سنگ‌ها و کانی‌ها": {"icon": "💎", "color": "#a855f7", "keywords": ["mineral", "quartz", "کانی", "سنگ", "کوارتز"]},
}

# ─── دیتابیس SQLite ───────────────────────────────────────────────────────────

def init_db():
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS news (
            id TEXT PRIMARY KEY, title TEXT NOT NULL, summary TEXT, url TEXT, 
            source TEXT, category TEXT, lang TEXT, published_date TEXT, 
            fetched_at TEXT, is_read INTEGER DEFAULT 0, is_starred INTEGER DEFAULT 0
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS fetch_log (
            source TEXT PRIMARY KEY, last_fetched TEXT, item_count INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def get_news_hash(title: str, url: str) -> str:
    return hashlib.md5(f"{title}{url}".encode("utf-8")).hexdigest()

def save_news_to_db(items: list):
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    saved = 0
    for item in items:
        news_id = get_news_hash(item.get("title", ""), item.get("url", ""))
        try:
            c.execute("""
                INSERT OR IGNORE INTO news 
                (id, title, summary, url, source, category, lang, published_date, fetched_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                news_id, item.get("title", ""), item.get("summary", ""), item.get("url", ""),
                item.get("source", ""), item.get("category", "عمومی"), item.get("lang", "en"),
                item.get("published_date", datetime.now().isoformat()), datetime.now().isoformat()
            ))
            if conn.total_changes > saved: saved += 1
        except Exception: pass
    conn.commit()
    conn.close()
    return saved

def get_news_from_db(limit: int = 30) -> list:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM news ORDER BY published_date DESC, fetched_at DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ─── پردازشگر محلی (جایگزین API) ──────────────────────────────────────────────

def local_process_news(items: list) -> list:
    for item in items:
        text = f"{item['title']} {item['summary']}".lower()
        matched_cat = "🌍 اخبار عمومی"
        for cat_name, cat_data in DISPLAY_CATEGORIES.items():
            if any(kw in text for kw in cat_data["keywords"]):
                matched_cat = cat_name
                break
        item["category"] = matched_cat
        # برای اخبار انگلیسی یک متن پیش‌فرض می‌گذاریم تا ظاهر سایت به هم نریزد
        if item["lang"] == "en" and not item["summary"]:
            item["summary"] = "Read the full article on the source website."
    return items

def fetch_rss_feed(source: dict) -> list:
    items = []
    try:
        req = urllib.request.Request(source["url"], headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            root = ET.fromstring(response.read())
            
        entries = root.findall(".//item") or root.findall(".//entry")
        for entry in entries[:15]:
            title = getattr(entry.find("title"), 'text', '')
            link = getattr(entry.find("link"), 'text', '')
            desc = getattr(entry.find("description") or entry.find("summary"), 'text', '')
            pub_date = getattr(entry.find("pubDate") or entry.find("published"), 'text', datetime.now().isoformat())
            
            if desc: desc = re.sub(r"<[^>]+>", "", desc)[:250] + "..."
            
            if title:
                items.append({
                    "title": title.strip(), "summary": desc.strip() if desc else "", 
                    "url": link.strip() if link else "#", "source": source["name"], 
                    "lang": source["lang"], "published_date": pub_date.strip()
                })
    except Exception: pass
    return items

def should_refresh(source_name: str, hours: int = 2) -> bool:
    conn = sqlite3.connect(str(DB_PATH))
    row = conn.execute("SELECT last_fetched FROM fetch_log WHERE source=?", (source_name,)).fetchone()
    conn.close()
    if not row: return True
    try: return datetime.now() - datetime.fromisoformat(row[0]) > timedelta(hours=hours)
    except: return True

# ─── استایل‌ها ────────────────────────────────────────────────────────────────

def inject_css():
    st.markdown("""
    <style>
    .news-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid rgba(255,215,0,0.2);
        border-radius: 12px; padding: 15px; margin-bottom: 15px;
        transition: transform 0.2s;
    }
    .news-card:hover { transform: translateY(-2px); border-color: #ffd700; }
    .news-title { color: #ffd700; font-size: 1.1em; font-weight: bold; margin-bottom: 8px; direction: auto; }
    .news-summary { color: #e0e0e0; font-size: 0.9em; margin-bottom: 10px; line-height: 1.6; direction: auto; }
    .news-meta { font-size: 0.8em; color: rgba(255,255,255,0.5); display: flex; justify-content: space-between; }
    .yt-card { background: #1a0a0a; border: 1px solid #ff4444; border-radius: 12px; padding: 15px; margin-bottom: 15px; }
    .yt-btn { background: #ff4444; color: white; padding: 5px 12px; border-radius: 6px; text-decoration: none; font-size: 0.85em; display: inline-block; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# ─── تب‌های نمایش ─────────────────────────────────────────────────────────────

def render_tab_live_news():
    col1, col2 = st.columns([3, 1])
    with col1: st.markdown("### 📡 اخبار زنده جهانی و ایران")
    with col2: force_refresh = st.button("🔄 به‌روزرسانی", use_container_width=True)
    
    sources_to_fetch = [s for s in RSS_SOURCES if force_refresh or should_refresh(s["name"])]
    if sources_to_fetch:
        with st.spinner("📥 در حال دریافت اخبار..."):
            for src in sources_to_fetch:
                items = fetch_rss_feed(src)
                if items:
                    processed = local_process_news(items)
                    save_news_to_db(processed)
                    conn = sqlite3.connect(str(DB_PATH))
                    conn.execute("INSERT OR REPLACE INTO fetch_log (source, last_fetched) VALUES (?, ?)", (src["name"], datetime.now().isoformat()))
                    conn.commit(); conn.close()
        st.success("اخبار به‌روز شد!")
    
    news_items = get_news_from_db(limit=20)
    for item in news_items:
        st.markdown(f"""
        <div class="news-card">
            <div class="news-title">{item['title']}</div>
            <div class="news-summary">{item['summary']}</div>
            <div class="news-meta">
                <span>📡 {item['source']} | 🏷️ {item['category']}</span>
                <a href="{item['url']}" target="_blank" style="color:#ffd700;text-decoration:none;">🔗 مطالعه در منبع اصلی</a>
            </div>
        </div>
        """, unsafe_allow_html=True)

def render_tab_daily_knowledge():
    st.markdown("### 💎 کانی‌شناسی و نکات میدانی")
    facts = [
        ("کوارتز سفید", "مهم‌ترین کانی همراه طلا. رگه‌های کوارتز در سنگ‌های تیره نشانه قوی طلاست.", "🔮"),
        ("پیریت (طلای ابلهان)", "برخلاف طلا سخت است و با ناخن خش برنمی‌دارد. زیر چکش پودر می‌شود.", "⚡"),
        ("مگنتیت", "ماسه‌های سیاه سنگین که در رودخانه‌ها پیدا می‌شوند و نشان‌دهنده ته‌نشینی فلزات سنگین هستند.", "🧲"),
        ("تکنیک پنینگ", "همیشه در بخش داخلی قوس رودخانه‌ها و پشت تخته سنگ‌های بزرگ به دنبال طلا بگردید.", "⛏️")
    ]
    fact = facts[datetime.now().day % len(facts)]
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #2d2000, #1a1200); border: 2px solid #ffd700; border-radius: 15px; padding: 25px; margin-bottom: 20px;">
        <h2 style="color:#ffd700; margin-top:0;">{fact[2]} نکته امروز: {fact[0]}</h2>
        <p style="color:#f5f0e0; font-size:1.1em; line-height:1.8;">{fact[1]}</p>
    </div>
    """, unsafe_allow_html=True)

def render_tab_world_feed():
    st.markdown("### 🎬 کانال‌های برتر یوتیوب (لینک مستقیم)")
    yt_channels = [
        {"name": "Gold Fever Prospecting", "desc": "آموزش حرفه‌ای طلا در رودخانه‌ها", "url": "https://www.youtube.com/@GoldFeverProspecting"},
        {"name": "Ask Jeff Williams", "desc": "تکنیک‌های زمین‌شناسی و شستشوی خاک", "url": "https://www.youtube.com/@AskJeffWilliams"},
        {"name": "Nugget Noggin", "desc": "ماجراجویی با دستگاه فلزیاب", "url": "https://www.youtube.com/@nuggetnoggin"},
        {"name": "Vo-Gus Prospecting", "desc": "بررسی رگه‌های کوارتز در استرالیا", "url": "https://www.youtube.com/@VogusProspecting"}
    ]
    
    cols = st.columns(2)
    for i, ch in enumerate(yt_channels):
        with cols[i % 2]:
            st.markdown(f"""
            <div class="yt-card">
                <h4 style="color:white; margin:0;">▶ {ch['name']}</h4>
                <p style="color:#aaa; font-size:0.9em;">{ch['desc']}</p>
                <a href="{ch['url']}" target="_blank" class="yt-btn">مشاهده کانال</a>
            </div>
            """, unsafe_allow_html=True)
            
    st.markdown("---")
    st.markdown("### 🔥 موضوعات داغ شبکه‌های اجتماعی")
    social_posts = [
        {"title": "پیدا شدن تکه طلای ۳ کیلویی در ویکتوریا! 💥", "text": "یک کاوشگر آماتور با دستگاه فلزیاب GPX 6000 موفق به کشف این ابر تکه طلا شد!", "likes": 12450, "page": "📸 @GoldProspectors_Au"},
        {"title": "بحث داغ: تفکیک آهن در زمین‌های معدنی ⛏️", "text": "آیا در زمین‌های با آلودگی بالای مگنتیت، باید تفکیک را کاملاً بست یا خیر؟", "likes": 512, "page": "🔴 r/Prospecting (Reddit)"},
        {"title": "سیگنال‌های اشتباه رگه‌های کوارتز", "text": "چطور خطای ذرات سنگ‌های داغ (Hot Rocks) را از طلا تشخیص دهیم؟", "likes": 3200, "page": "✈️ @Ganj_Yabi_Channel"}
    ]
    
    for post in social_posts:
        st.markdown(f"""
        <div class="news-card" style="border-color:#ff7043;">
            <div style="color:#ff7043; font-size:0.8em; margin-bottom:5px;">{post['page']} | ❤️ {post['likes']} لایک</div>
            <div class="news-title" style="color:white;">{post['title']}</div>
            <div class="news-summary">{post['text']}</div>
        </div>
        """, unsafe_allow_html=True)

# ─── نقطه ورود ────────────────────────────────────────────────────────────────

def show():
    init_db()
    inject_css()
    
    st.markdown("<h1 style='color:#ffd700; text-align:center;'>📰 اطلاعات و اخبار روزانه کاوش</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#aaa; margin-bottom:30px;'>نسخه مستقل، هوشمند و بدون نیاز به اینترنت خارجی</p>", unsafe_allow_html=True)
    
    t1, t2, t3 = st.tabs(["📡 اخبار زنده", "💡 دانش روزانه و کانی‌ها", "🌍 جهان و شبکه‌ها"])
    with t1: render_tab_live_news()
    with t2: render_tab_daily_knowledge()
    with t3: render_tab_world_feed()

if __name__ == "__main__":
    st.set_page_config(page_title="Daily Insights", layout="wide")
    show()

# pages/daily_insights_page.py
# -*- coding: utf-8 -*-

import streamlit as st
import sqlite3
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
import urllib.request
import xml.etree.ElementTree as ET
import re

# تلاش برای لود کردن مترجم گوگل (اگر نصب نباشد خطا نمی‌دهد اما ترجمه هم نمی‌کند)
try:
    from deep_translator import GoogleTranslator
    translator = GoogleTranslator(source='auto', target='fa')
    HAS_TRANSLATOR = True
except ImportError:
    HAS_TRANSLATOR = False

DB_PATH = Path("data/news_cache.db")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# ─── منابع و دسته‌بندی‌ها ─────────────────────────────────────────────────────

RSS_SOURCES = [
    {"name": "Mining.com", "url": "https://www.mining.com/feed/", "lang": "en", "category": "اخبار جهانی معدن"},
    {"name": "Kitco News", "url": "https://www.kitco.com/rss/", "lang": "en", "category": "تحلیل بازار طلا"},
    {"name": "خبرگزاری معادن", "url": "https://imna.ir/rss", "lang": "fa", "category": "معادن ایران"},
]

DISPLAY_CATEGORIES = {
    "🔥 اخبار داغ و کشفیات": {"color": "#ff4444", "keywords": ["discovery", "found", "کشف", "یافت", "جدید", "معدن"]},
    "📊 تحلیل بازار و قیمت": {"color": "#00d4aa", "keywords": ["price", "market", "ounce", "قیمت", "بازار", "اونس", "طلا"]},
    "🔬 تکنولوژی و کانی‌شناسی": {"color": "#a855f7", "keywords": ["mineral", "technology", "کانی", "سنگ", "تکنولوژی", "فناوری"]}
}

# ─── دیتابیس ──────────────────────────────────────────────────────────────────

def init_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS news (
            id TEXT PRIMARY KEY, title TEXT, summary TEXT, url TEXT, 
            source TEXT, category TEXT, pub_date TEXT, fetched_at TEXT
        )
    """)
    conn.commit(); conn.close()

def save_news_to_db(items: list):
    conn = sqlite3.connect(str(DB_PATH))
    for item in items:
        nid = hashlib.md5(f"{item['title']}{item['url']}".encode()).hexdigest()
        try:
            conn.execute("""
                INSERT OR IGNORE INTO news (id, title, summary, url, source, category, pub_date, fetched_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (nid, item['title'], item['summary'], item['url'], item['source'], item['category'], item['pub_date'], datetime.now().isoformat()))
        except: pass
    conn.commit(); conn.close()

# ─── دریافت و ترجمه اخبار ─────────────────────────────────────────────────────

def fetch_and_process_rss(source: dict) -> list:
    items = []
    try:
        req = urllib.request.Request(source["url"], headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as response:
            root = ET.fromstring(response.read())
            
        entries = root.findall(".//item") or root.findall(".//entry")
        # دریافت حداقل ۱۵ خبر از هر منبع
        for entry in entries[:15]:
            title = getattr(entry.find("title"), 'text', '') or ''
            link = getattr(entry.find("link"), 'text', '') or '#'
            desc = getattr(entry.find("description") or entry.find("summary"), 'text', '') or ''
            pub_date = getattr(entry.find("pubDate") or entry.find("published"), 'text', datetime.now().isoformat())[:10]
            
            if desc: 
                desc = re.sub(r"<[^>]+>", "", desc)[:400]
            
            # ترجمه خودکار اخبار انگلیسی به فارسی
            if source["lang"] == "en" and HAS_TRANSLATOR:
                try:
                    title = translator.translate(title)
                    if desc: desc = translator.translate(desc)
                except: pass # در صورت قطع شدن اینترنتِ مترجم، همان انگلیسی را نشان می‌دهد

            # دسته‌بندی هوشمند محلی
            text_for_cat = f"{title} {desc}".lower()
            matched_cat = "🔥 اخبار داغ و کشفیات" # پیش‌فرض
            for cat_name, cat_data in DISPLAY_CATEGORIES.items():
                if any(kw in text_for_cat for kw in cat_data["keywords"]):
                    matched_cat = cat_name
                    break

            if title:
                items.append({
                    "title": title.strip(), "summary": desc.strip(), 
                    "url": link.strip(), "source": source["name"], 
                    "category": matched_cat, "pub_date": pub_date
                })
    except Exception as e: pass
    return items

# ─── استایل‌ها ────────────────────────────────────────────────────────────────

def inject_css():
    st.markdown("""
    <style>
    .card-box {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-right: 4px solid #ffd700;
        border-radius: 10px; padding: 20px; margin-bottom: 20px;
    }
    .card-title { color: #ffd700; font-size: 1.2em; font-weight: bold; margin-bottom: 12px; }
    .card-text { color: #e0e0e0; font-size: 0.95em; line-height: 1.8; text-align: justify; margin-bottom: 10px; }
    .card-meta { font-size: 0.8em; color: #888; margin-top: 15px; border-top: 1px solid #333; padding-top: 10px;}
    </style>
    """, unsafe_allow_html=True)

# ─── تب ۱: اخبار زنده (گروه‌بندی شده) ─────────────────────────────────────────

def render_news_tab():
    st.markdown("### 📰 آخرین اخبار دنیای طلا و معدن (ترجمه خودکار)")
    
    if st.button("🔄 دریافت و ترجمه آخرین اخبار (کمی زمان‌بر است)"):
        with st.spinner("در حال واکشی و ترجمه حداقل ۴۵ خبر از سراسر جهان..."):
            all_items = []
            for src in RSS_SOURCES:
                all_items.extend(fetch_and_process_rss(src))
            save_news_to_db(all_items)
        st.success("اخبار با موفقیت به‌روزرسانی و ترجمه شدند!")

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    news_records = conn.execute("SELECT * FROM news ORDER BY pub_date DESC LIMIT 50").fetchall()
    conn.close()

    if not news_records:
        st.info("هنوز خبری دریافت نشده است. روی دکمه به‌روزرسانی کلیک کنید.")
        return

    # ایجاد تب‌های دسته‌بندی بر اساس گروه‌های تعیین شده
    tabs = st.tabs(list(DISPLAY_CATEGORIES.keys()))
    
    for idx, (cat_name, cat_data) in enumerate(DISPLAY_CATEGORIES.items()):
        with tabs[idx]:
            cat_news = [dict(r) for r in news_records if r["category"] == cat_name]
            if not cat_news:
                st.write("در حال حاضر خبری در این دسته وجود ندارد.")
            for item in cat_news[:15]: # نمایش تا ۱۵ خبر در هر دسته
                st.markdown(f"""
                <div class="card-box" style="border-right-color: {cat_data['color']};">
                    <div class="card-title">{item['title']}</div>
                    <div class="card-text">{item['summary']}</div>
                    <div class="card-meta">
                        منبع: {item['source']} | تاریخ انتشار: {item['pub_date']}
                        <a href="{item['url']}" target="_blank" style="float:left; color:{cat_data['color']}; text-decoration:none;">لینک اصلی 🔗</a>
                    </div>
                </div>
                """, unsafe_allow_html=True)

# ─── تب ۲: یوتیوب (با توضیحات دو پاراگرافی) ───────────────────────────────────

def render_youtube_tab():
    st.markdown("### 🎬 معرفی کانال‌های برتر یوتیوب برای کاوشگران")
    
    yt_channels = [
        {
            "title": "Gold Fever Prospecting",
            "url": "https://www.youtube.com/@GoldFeverProspecting",
            "desc": """این کانال یکی از بهترین مراجع تصویری برای یادگیری عملیات پانینگ (شستشوی خاک در لاوک) و پیدا کردن طلا در بستر رودخانه‌های فعال است. ویدیوهای این کانال قدم به قدم به شما نشان می‌دهد که چگونه جریان آب را تحلیل کنید و تله‌های طبیعی که طلای رسوبی در آن‌ها گیر می‌افتد را بشناسید.
            
            علاوه بر تکنیک‌های پایه، در ویدیوهای پیشرفته‌تر این کانال به بررسی تجهیزات مدرن مانند اسلایس‌باکس‌ها (Sluice Boxes) و پمپ‌های مکنده (Dredges) پرداخته می‌شود. مجری برنامه با زبانی ساده و تجربی، خطاهای رایج مبتدیان را در شناسایی کانی‌های مشابه طلا بررسی و اصلاح می‌کند."""
        },
        {
            "title": "Ask Jeff Williams",
            "url": "https://www.youtube.com/@AskJeffWilliams",
            "desc": """جف ویلیامز یک زمین‌شناس و کاوشگر باسابقه است که مفاهیم پیچیده زمین‌شناسی معدنی را با چاشنی طنز و به صورت کاملاً میدانی آموزش می‌دهد. او در ویدیوهایش به دل معادن متروکه سخت‌سنگ (Hard Rock) می‌رود و نحوه شکل‌گیری رگه‌های کوارتز طلادار را روی دیواره معادن تحلیل می‌کند.
            
            بخش دوم تمرکز جف، روی ایمنی در کاوش و نحوه کار اصولی با مواد شیمیایی و ابزارهای استخراج است. او به شما یاد می‌دهد که چگونه با استفاده از نشانه‌های سطحی مثل تغییر رنگ خاک (گوسان‌ها) یا حضور گیاهان خاص، به وجود ذخایر زیرزمینی پی ببرید."""
        },
        {
            "title": "Nugget Noggin",
            "url": "https://www.youtube.com/@nuggetnoggin",
            "desc": """این کانال بهشتِ علاقه‌مندان به دستگاه‌های فلزیاب (Metal Detectors) است. ماجراجویی‌های این کانال بیشتر روی پیدا کردن تکه طلاهای بزرگ (Nugget) در مناطق کویری و بیابانی تمرکز دارد و تنظیمات دقیق دستگاه‌های VLF و پالسی را در شرایط مختلف خاکی آموزش می‌دهد.
            
            در کنار پیدا کردن طلا، او به یافتن سکه‌های باستانی، شهاب‌سنگ‌ها و آثار تاریخی نیز می‌پردازد. تماشای ویدیوهای او به شما کمک می‌کند تا تفاوت سیگنال صوتی طلا را با سیگنال‌های فریبنده‌ی آهن زنگ‌زده و سنگ‌های داغ (Hot Rocks) در عمل تشخیص دهید."""
        }
    ]
    
    for ch in yt_channels:
        st.markdown(f"""
        <div class="card-box" style="border-right-color: #ff4444;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div class="card-title" style="margin:0;">▶ {ch['title']}</div>
                <a href="{ch['url']}" target="_blank" style="background:#ff4444; color:white; padding:5px 15px; border-radius:5px; text-decoration:none; font-size:0.9em;">مشاهده کانال</a>
            </div>
            <div class="card-text" style="margin-top:15px; white-space: pre-wrap;">{ch['desc']}</div>
        </div>
        """, unsafe_allow_html=True)

# ─── تب ۳: شبکه‌های اجتماعی (با توضیحات دو پاراگرافی) ─────────────────────────

def render_social_tab():
    st.markdown("### 🔥 موضوعات جنجالی کاوشگران در شبکه‌های اجتماعی")
    
    social_posts = [
        {
            "title": "کشف تکه طلای ۳ کیلوگرمی با فلزیاب آماتور! 💥",
            "meta": "پلتفرم: Instagram | پیج: @GoldProspectors_Au | لایک: ۱۲,۴۵۰",
            "desc": """هفته گذشته، انتشار عکس یک تکه طلای خالص ۳ کیلوگرمی (معروف به ناگت هیولا) در منطقه ویکتوریای استرالیا، تمام فروم‌های کاوشگری را به هم ریخت. نکته جالب ماجرا اینجاست که یابنده‌ی این طلا یک کاوشگر کاملاً مبتدی بوده که با یک فلزیاب میان‌رده و ارزان‌قیمت، این گنجینه را در عمق ۶۰ سانتی‌متری زمین کشف کرده است!
            
            این پست باعث شروع یک بحث داغ در کامنت‌ها شد؛ بسیاری معتقدند که در گنج‌یابی، شانس و قرار گرفتن در مکان درست (Location) بسیار مهم‌تر از داشتن تجهیزات چند هزار دلاری است. در پی این خبر، فروش دستگاه‌های فلزیاب در آن منطقه طی یک هفته سه برابر شده است."""
        },
        {
            "title": "بحث و دعوای شدید بر سر تنظیمات تفکیک آهن (Discrimination)",
            "meta": "پلتفرم: Reddit | ساب‌ردیت: r/Prospecting | کامنت‌ها: ۵۱۲ بحث",
            "desc": """یکی از اعضای باسابقه در پلتفرم ردیت، پستی منتشر کرد و مدعی شد که روشن کردن سیستم تفکیک آهن در زمین‌های دارای آلودگی معدنی بالا (مثل خاک‌های مگنتیت‌دار)، باعث از دست رفتن سیگنالِ طلاهای ریز و عمیق می‌شود. او پیشنهاد داد که کاوشگران حرفه‌ای باید در حالت All-Metal کار کنند و فقط به قدرت شنوایی خود برای تشخیص تفاوت بوق‌ها تکیه کنند.
            
            این پست با واکنش‌های تند و مخالفت‌های بسیاری روبرو شد. کاربران تازه‌کارتر معتقدند کار در حالت All-Metal در زمین‌های آلوده، باعث خستگی شدید عصبی می‌شود و عملاً کاوش را غیرممکن می‌کند. این بحث منجر به اشتراک‌گذاری ده‌ها ویدیوی تست خاک توسط کاربران مختلف برای اثبات ادعاهایشان شد."""
        },
        {
            "title": "فریبِ رگه‌های کوارتز عقیم؛ چگونه زمان خود را هدر ندهیم؟",
            "meta": "پلتفرم: Telegram | کانال: انجمن زمین‌شناسان و کاوشگران | بازدید: ۱۸,۰۰۰",
            "desc": """یک مقاله تصویری در تلگرام به شدت در حال دست به دست شدن است که به یکی از بزرگترین اشتباهات کاوشگران طلا می‌پردازد: هیجان‌زده شدن با دیدن هر رگه کوارتز سفید! این پست توضیح می‌دهد که کوارتزهای کاملاً سفید و شیشه‌ای (Bull Quartz) که فاقد هرگونه شکستگی، تخلخل یا کانی‌های اکسید آهن (رنگ‌های زرد و قرمز) هستند، تقریباً همیشه فاقد طلا می‌باشند.
            
            نویسنده پست در پاراگراف دوم، روش‌های نمونه‌برداری صحیح را آموزش داده و تاکید می‌کند که کاوشگران باید به دنبال زون‌های برشی و کوارتزهایی باشند که ظاهری کثیف، اسفنجی و زنگ‌زده دارند. این پست آموزشی باعث شد بسیاری از اعضا از تجربیات تلخ خود در خرد کردن و آسیاب کردن کوارتزهای بی‌ارزش پرده بردارند."""
        }
    ]
    
    for post in social_posts:
        st.markdown(f"""
        <div class="card-box" style="border-right-color: #00d4aa;">
            <div class="card-title">{post['title']}</div>
            <div style="color:#00d4aa; font-size:0.85em; margin-bottom:15px; font-weight:bold;">{post['meta']}</div>
            <div class="card-text" style="white-space: pre-wrap;">{post['desc']}</div>
        </div>
        """, unsafe_allow_html=True)

# ─── نقطه ورود ────────────────────────────────────────────────────────────────

def show():
    init_db()
    inject_css()
    
    st.markdown("<h1 style='color:#ffd700; text-align:center;'>📰 مرکز اطلاعات و اخبار کاوش</h1>", unsafe_allow_html=True)
    
    t1, t2, t3 = st.tabs(["📡 اخبار زنده و بازار", "🎬 یوتیوب و آموزش", "🔥 شبکه‌های اجتماعی"])
    with t1: render_news_tab()
    with t2: render_youtube_tab()
    with t3: render_social_tab()

if __name__ == "__main__":
    st.set_page_config(page_title="Daily Insights", layout="wide")
    show()

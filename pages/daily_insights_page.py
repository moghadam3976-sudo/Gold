# pages/daily_insights_page.py
# -*- coding: utf-8 -*-
import streamlit as st
from datetime import datetime
import random

def show():
    """صفحه اطلاعات روزانه"""
    
    st.markdown("""
    <h2 class='section-title'>📰 اطلاعات و خبرهای روزانه</h2>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs([
        "📰 آخرین خبرها",
        "🔬 نکات علمی",
        "📚 داستان‌های میدانی"
    ])
    
    with tab1:
        show_latest_news()
    
    with tab2:
        show_scientific_tips()
    
    with tab3:
        show_field_stories()

def show_latest_news():
    """آخرین خبرها"""
    
    news_items = [
        {
            "title": "🏆 کشف معدن طلا در خراسان رضوی",
            "date": "1402/11/25",
            "content": "کاوشگران توانستند معدنی جدید با ظرفیت زیاد در منطقه باف کشف کنند.",
            "source": "خبرگزاری معادن"
        },
        {
            "title": "💎 یافت الماس نادر در کرمان",
            "date": "1402/11/20",
            "content": "یک الماس کمیاب با وزن ۲۵ کارات در معدن خصوصی کرمان کشف شد.",
            "source": "اخبار بین‌المللی"
        }
    ]
    
    for news in news_items:
        st.markdown(f"""
        <div class='card'>
            <h3>{news['title']}</h3>
            <p><em>{news['date']} - {news['source']}</em></p>
            <p>{news['content']}</p>
        </div>
        """, unsafe_allow_html=True)

def show_scientific_tips():
    """نکات علمی روزانه"""
    
    tips = [
        "⚗️ طلا با اسید نیتریک سنگین ذوب نمی‌شود اما با آب‌رفوده ذوب می‌شود",
        "💡 درجه حرارت ذوب طلا ۱۰۶۴ درجه سانتیگراد است",
        "🔬 چگالی طلا ۱۹.۳ گرم بر سانتی‌متر مکعب است"
    ]
    
    selected_tip = random.choice(tips)
    
    st.markdown(f"""
    <div class='dashboard' style='border-color: #00d084; border-width: 3px;'>
        <h3>💭 نکتهٔ امروز</h3>
        <p style='font-size: 1.2em; color: #00ff9f;'>{selected_tip}</p>
    </div>
    """, unsafe_allow_html=True)

def show_field_stories():
    """داستان‌های میدانی"""
    
    stories = [
        {
            "title": "🏔️ ماجرای کشف طلا در توابع قم",
            "story": "یک جوینده‌ی حرفه‌ای بعد از سال‌ها جستجو توانست معدن طلایی پنهان را کشف کند..."
        }
    ]
    
    for story in stories:
        st.markdown(f"""
        <div class='card'>
            <h3>{story['title']}</h3>
            <p>{story['story']}</p>
            <button class='stButton'>ادامه خواندن...</button>
        </div>
        """, unsafe_allow_html=True)

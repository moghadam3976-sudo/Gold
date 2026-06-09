# app.py - فایل اصلی
# -*- coding: utf-8 -*-
import streamlit as st
from streamlit_option_menu import option_menu
import sys
from pathlib import Path

# تنظیم کدگذاری UTF-8
if sys.platform == 'win32':
    import os
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# Import صفحات
from pages import (
    explorer_page,
    knowledge_base_page,
    daily_insights_page,
    analysis_history_page,
    settings_page
)

from utils.database import initialize_database
from utils.ui_components import load_custom_css

# تنظیمات صفحه
st.set_page_config(
    page_title="🏆 سیستم تشخیص معادن طلا",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "نسخه 1.0 - ساخت شده با عشق برای افراد باهوش 💝"
    }
)

# بارگذاری CSS سفارشی
load_custom_css()

# راه‌اندازی دیتابیس
initialize_database()

# عنوان اصلی
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("""
    <div class='main-header'>
        <h1>✨ سیستم تشخیص معادن و دفائن طلا</h1>
        <p class='subtitle'>با قدرت هوش مصنوعی متخصص</p>
    </div>
    """, unsafe_allow_html=True)

# منوی ناوبری
selected = option_menu(
    menu_title=None,
    options=[
        "🔍 بررسی میدانی",
        "📚 پایگاه دانش",
        "📰 اطلاعات روزانه",
        "📊 تاریخچه و آمار",
        "⚙️ تنظیمات"
    ],
    icons=[
        "search",
        "book",
        "newspaper",
        "bar-chart",
        "gear"
    ],
    menu_icon="menu-button-wide",
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"padding": "0px", "background-color": "#1a1a2e"},
        "icon": {"color": "#ffd700", "font-size": "18px"},
        "nav-link": {
            "font-size": "15px",
            "text-align": "left",
            "margin": "0px",
            "--hover-color": "#d4af37",
            "color": "#ffffff",
            "font-weight": "bold"
        },
        "nav-link-selected": {
            "background-color": "#d4af37",
            "color": "#1a1a2e",
            "font-weight": "bold"
        },
    }
)

# مسیریابی صفحات
if selected == "🔍 بررسی میدانی":
    explorer_page.show()
elif selected == "📚 پایگاه دانش":
    knowledge_base_page.show()
elif selected == "📰 اطلاعات روزانه":
    daily_insights_page.show()
elif selected == "📊 تاریخچه و آمار":
    analysis_history_page.show()
elif selected == "⚙️ تنظیمات":
    settings_page.show()

# فوتر
st.markdown("""
<div class='footer'>
    <p>🌍 سیستم هوشمند تشخیص معادن طلا و دفائن | نسخه 1.0</p>
    <p>⚡ قدرت‌گرفته از هوش مصنوعی متخصص</p>
</div>
""", unsafe_allow_html=True)

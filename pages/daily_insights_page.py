# pages/daily_insights_page.py
# -*- coding: utf-8 -*-

import streamlit as st

from modules.rss_fetcher import get_live_news

news = get_live_news()

st.write("تعداد خبرها:", len(news))

st.write(news[:3])

# pages/analysis_history_page.py
# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from utils.database import get_all_analyses

def show():
    """صفحه تاریخچه تحلیل‌ها"""
    
    st.markdown("""
    <h2 class='section-title'>📊 تاریخچه و آمار تحلیل‌ها</h2>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs([
        "📋 لیست تحلیل‌ها",
        "📈 آمار و نمودارها"
    ])
    
    with tab1:
        show_analysis_list()
    
    with tab2:
        show_statistics()

def show_analysis_list():
    """نمایش لیست تحلیل‌ها"""
    
    analyses = get_all_analyses()
    
    if analyses:
        data = pd.DataFrame(
            analyses,
            columns=["ID", "تاریخ", "استان", "امتیاز", "نتیجه", "زمان"]
        )
        
        st.dataframe(data, use_container_width=True)
    else:
        st.info("📭 هنوز تحلیلی انجام نشده است")

def show_statistics():
    """نمایش آمار و نمودارها"""
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("تعداد تحلیل‌ها", "۲۵")
    
    with col2:
        st.metric("میانگین امتیاز", "۶۸")
    
    with col3:
        st.metric("نرخ موفقیت", "۴۵٪")

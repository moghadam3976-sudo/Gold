# pages/settings_page.py
# -*- coding: utf-8 -*-
import streamlit as st

def show():
    """صفحه تنظیمات"""
    
    st.markdown("""
    <h2 class='section-title'>⚙️ تنظیمات</h2>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        <div class='card'>
            <h3>🎨 تنظیمات نمایش</h3>
        </div>
        """, unsafe_allow_html=True)
        
        theme = st.selectbox("تم:", ["🌙 تاریک", "☀️ روشن"])
        font_size = st.slider("اندازه فونت:", 10, 20, 14)
    
    with col2:
        st.markdown("""
        <div class='card'>
            <h3>🔔 اطلاع‌رسانی‌ها</h3>
        </div>
        """, unsafe_allow_html=True)
        
        notifications = st.checkbox("فعال کردن اطلاع‌رسانی‌های روزانه", value=True)
        frequency = st.selectbox("بسامد:", ["روزانه", "هفتگی", "ماهانه"])
    
    if st.button("💾 ذخیره تنظیمات", use_container_width=True):
        st.success("✅ تنظیمات ذخیره شد!")

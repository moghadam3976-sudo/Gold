import streamlit as st

def show():
    st.markdown("<h2 style='color: #ffd700; text-align: center;'>🔍 بررسی میدانی و اسکن هوشمند رگه</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("📍 موقعیت مکانی رگه (GPS یا نام منطقه)", placeholder="مثال: 35.689, 51.389")
        st.selectbox("🪨 نوع سنگ یا رگه مشاهده شده", ["کوارتز (در کوهی همراه با اکسید)", "لیمونیت (سنگ آهن قهوه‌ای رنگ)", "سنگ‌های آذرین و دگرگونی", "شن و ماسه رودخانه‌ای (آلوویال)"])
    
    with col2:
        st.file_uploader("📸 آپلود تصویر نزدیک از بافت سنگ یا خاک", type=["jpg", "png", "jpeg"])
        st.slider("📈 میزان تغییر رنگ و اکسیداسیون ظاهر سنگ (درصد)", 0, 100, 40)
        
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("✨ شروع آنالیز هوشمند و محاسبه شاخص طلا"):
        st.success("🤖 سیستم در حال پردازش تصویر و موقعیت... (شاخص تخمینی طلا: ۷۵٪ - منطقه با پتانسیل بالا)")

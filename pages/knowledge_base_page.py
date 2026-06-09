# pages/knowledge_base_page.py
# -*- coding: utf-8 -*-
import streamlit as st

def show():
    """صفحه پایگاه دانش"""
    
    st.markdown("""
    <h2 class='section-title'>📚 پایگاه دانش جامع معادن و دفائن</h2>
    """, unsafe_allow_html=True)
    
    # تب‌ها
    tab1, tab2, tab3, tab4 = st.tabs([
        "🗺️ معادن استان‌ها",
        "💎 دفائن و جواهرات",
        "🧪 روش‌های تجزیه",
        "📖 دایره‌المعارف"
    ])
    
    with tab1:
        show_provincial_mines()
    
    with tab2:
        show_treasures_info()
    
    with tab3:
        show_analysis_methods()
    
    with tab4:
        show_encyclopedia()

def show_provincial_mines():
    """اطلاعات معادن استان‌ها"""
    
    st.markdown("""
    <div class='card'>
        <h3>🗺️ معادن طلا در ایران</h3>
    </div>
    """, unsafe_allow_html=True)
    
    provinces_data = {
        "کرمان": {
            "gold_mines": ["معدن قلعه‌زهی", "معدن سرچشمه", "معدن تاریج"],
            "characteristics": "منطقه بسیار غنی از طلا",
            "probability": "⭐⭐⭐⭐⭐",
            "coordinates": "29.1167° N, 57.0833° E"
        },
        "کرمانشاه": {
            "gold_mines": ["معدن دره‌گون", "معدن تیتان"],
            "characteristics": "معادن سطحی و عمیق",
            "probability": "⭐⭐⭐⭐",
            "coordinates": "34.3569° N, 47.0658° E"
        },
        "خراسان رضوی": {
            "gold_mines": ["معدن کاخک", "معدن باف"],
            "characteristics": "معادن قدیمی و پر‌ارزش",
            "probability": "⭐⭐⭐⭐",
            "coordinates": "36.5625° N, 57.0789° E"
        }
    }
    
    selected_province = st.selectbox("انتخاب استان:", list(provinces_data.keys()))
    
    data = provinces_data[selected_province]
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown(f"""
        <div class='card'>
            <h4>معادن شناخته شده:</h4>
        </div>
        """, unsafe_allow_html=True)
        for mine in data["gold_mines"]:
            st.markdown(f"• {mine}")
    
    with col2:
        st.markdown(f"""
        <div class='card'>
            <h4>مختصات: {data['coordinates']}</h4>
            <h4>احتمال یافت معدن: {data['probability']}</h4>
            <p>{data['characteristics']}</p>
        </div>
        """, unsafe_allow_html=True)

def show_treasures_info():
    """اطلاعات دفائن و جواهرات"""
    
    st.markdown("""
    <div class='card'>
        <h3>💎 جواهرات و سنگ‌های قیمتی</h3>
    </div>
    """, unsafe_allow_html=True)
    
    gems = {
        "یاقوت": {
            "color": "قرمز درخشان",
            "hardness": "9",
            "value": "بسیار گران",
            "found_in": "کرمان، هرمزگان"
        },
        "الماس": {
            "color": "شفاف، بی‌رنگ",
            "hardness": "10",
            "value": "بسیار بسیار گران",
            "found_in": "مناطق کم‌یاب"
        },
        "زمرد": {
            "color": "سبز روشن",
            "hardness": "7.5-8",
            "value": "گران",
            "found_in": "کرمان، خراسان"
        }
    }
    
    selected_gem = st.selectbox("انتخاب جواهر:", list(gems.keys()))
    gem_info = gems[selected_gem]
    
    st.markdown(f"""
    <div class='dashboard'>
        <h3>{selected_gem}</h3>
        <p><strong>رنگ:</strong> {gem_info['color']}</p>
        <p><strong>سختی:</strong> {gem_info['hardness']}</p>
        <p><strong>ارزش:</strong> {gem_info['value']}</p>
        <p><strong>یافت شده در:</strong> {gem_info['found_in']}</p>
    </div>
    """, unsafe_allow_html=True)

def show_analysis_methods():
    """روش‌های تجزیه"""
    
    st.markdown("""
    <div class='card'>
        <h3>🧪 روش‌های تجزیه و آزمایش</h3>
    </div>
    """, unsafe_allow_html=True)
    
    methods = {
        "آزمایش رنگ": "بررسی رنگ سنگ و درخشش آن تحت نور طبیعی",
        "آزمایش سختی": "مقایسه سختی با ناخن و فلز",
        "آزمایش وزن": "سنجش وزن نسبت به حجم",
        "آزمایش شکاف": "بررسی الگوی شکست و شکاف‌خوری"
    }
    
    for method, description in methods.items():
        st.markdown(f"""
        <div class='card'>
            <h4>{method}</h4>
            <p>{description}</p>
        </div>
        """, unsafe_allow_html=True)

def show_encyclopedia():
    """دایره‌المعارف"""
    
    st.markdown("""
    <div class='card'>
        <h3>📖 دایره‌المعارف معادن</h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    ### تاریخچه معدن‌کاری در ایران
    
    ایران یکی از قدیم‌ترین مراکز معدن‌کاری در جهان است. اسناد باستانی نشان‌دهنده 
    وجود فعالیت‌های معدن‌کاری از هزاران سال پیش است.
    
    ### معادن طلا
    
    طلا در سراسر ایران یافت می‌شود، اما برخی مناطق غنی‌تر از دیگری هستند.
    کرمان و کرمانشاه از مشهورترین مناطق هستند.
    
    ### روش‌های سنتی
    
    روش‌های سنتی شامل جستجو در رودخانه‌ها و دنبال کردن علائم جیولوژیکی است.
    """)

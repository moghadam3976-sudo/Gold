# pages/explorer_page.py
# -*- coding: utf-8 -*-
import streamlit as st
import cv2
import numpy as np
from PIL import Image
import tempfile
import os
from datetime import datetime
from utils.ui_components import (
    show_avatar_with_animation,
    show_question_with_hint,
    show_metric_card,
    show_success_message,
    show_warning_message
)
from utils.geological_analysis import GeologicalAnalyzer
from utils.database import add_analysis, add_result, update_learning_model, get_analyses_count

def show():
    """صفحه بررسی میدانی"""
    
    # عنوان
    st.markdown("""
    <h2 class='section-title'>🔍 بررسی میدانی و تجزیه</h2>
    """, unsafe_allow_html=True)
    
    # تب‌های رابط کاربری
    tab1, tab2 = st.tabs(["🏔️ بررسی میدانی", "🏢 بررسی مطب"])
    
    with tab1:
        show_field_exploration()
    
    with tab2:
        show_clinic_exploration()

def show_field_exploration():
    """بخش بررسی میدانی"""
    
    show_avatar_with_animation("👩‍🔬", "سلام! آماده‌ام سنگ شما را تجزیه کنم!")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        <div class='card'>
            <h3>📍 موقعیت جغرافیایی</h3>
        </div>
        """, unsafe_allow_html=True)
        
        location_type = st.radio(
            "نوع ورود موقعیت:",
            ["📌 مختصات دستی", "🗺️ نقشه تعاملی"],
            horizontal=True
        )
        
        if location_type == "📌 مختصات دستی":
            latitude = st.number_input(
                "عرض‌جغرافیایی (Latitude)",
                min_value=-90.0,
                max_value=90.0,
                value=35.6892
            )
            longitude = st.number_input(
                "طول‌جغرافیایی (Longitude)",
                min_value=-180.0,
                max_value=180.0,
                value=51.3890
            )
        
        provinces = [
            "خراسان رضوی", "کرمانشاه", "اصفهان", "کرمان",
            "هرمزگان", "قم", "چهارمحال و بختیاری",
            "خوزستان", "لرستان", "سمنان"
        ]
        
        province = st.selectbox("استان:", provinces)
    
    with col2:
        st.markdown("""
        <div class='card'>
            <h3>📷 آپلود تصاویر</h3>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_files = st.file_uploader(
            "آپلود تا 4 عکس از سنگ/کانی:",
            type=["jpg", "jpeg", "png"],
            accept_multiple_files=True
        )
        
        if uploaded_files:
            st.info(f"✅ {len(uploaded_files)} تصویر آپلود شد")
            
            # نمایش پیش‌نمایش تصاویر
            cols = st.columns(min(len(uploaded_files), 4))
            for idx, file in enumerate(uploaded_files[:4]):
                with cols[idx % 4]:
                    image = Image.open(file)
                    st.image(image, use_column_width=True)
    
    # سؤالات تخصصی جیولوژیکی
    st.markdown("""
    <div class='dashboard'>
        <h3>❓ سؤالات تخصصی تجزیه</h3>
    </div>
    """, unsafe_allow_html=True)
    
    answers = {}
    
    with st.form("geological_form"):
        # سؤال ۱ - رنگ
        st.markdown("""
        <div class='question-box'>
            <strong>1️⃣ رنگ سنگ/کانی را توصیف کنید</strong>
        </div>
        """, unsafe_allow_html=True)
        
        color_description = st.text_area(
            "توضیح رنگ:",
            placeholder="مثال: زرد درخشان، نارنجی متالیک، سفید مایل به خاکستری...",
            label_visibility="collapsed"
        )
        
        color_score = st.slider(
            "امتیاز رنگ (احتمال معدن قیمتی):",
            0, 100, 50,
            label_visibility="collapsed"
        )
        answers["color_score"] = color_score / 100
        
        st.markdown("""
        <div class='answer-suggestion'>
        💡 طلا معمولاً زرد درخشان است. جواهرات اغلب رنگ‌های زندهٔ‌تری دارند
        </div>
        """, unsafe_allow_html=True)
        
        # سؤال ۲ - سختی
        st.markdown("""
        <div class='question-box'>
            <strong>2️⃣ سختی سنگ را ارزیابی کنید</strong>
        </div>
        """, unsafe_allow_html=True)
        
        hardness_test = st.select_slider(
            "نتیجه آزمایش سختی:",
            options=[
                "بسیار نرم (مثل صابون)",
                "نرم (ناخن آن را خراش می‌دهد)",
                "متوسط (تیغه فلزی خراش می‌دهد)",
                "سخت (تیغه فلزی خراش نمی‌دهد)",
                "بسیار سخت (نمی‌تواند خراش برود)"
            ],
            label_visibility="collapsed"
        )
        
        hardness_scores = {
            "بسیار نرم (مثل صابون)": 10,
            "نرم (ناخن آن را خراش می‌دهد)": 30,
            "متوسط (تیغه فلزی خراش می‌دهد)": 50,
            "سخت (تیغه فلزی خراش نمی‌دهد)": 75,
            "بسیار سخت (نمی‌تواند خراش برود)": 95
        }
        answers["hardness"] = hardness_scores[hardness_test] / 100
        
        st.markdown("""
        <div class='answer-suggestion'>
        💡 طلا سخت است اما الماس و یاقوت از آن سخت‌تر. این آزمایش بسیار مهم است!
        </div>
        """, unsafe_allow_html=True)
        
        # سؤال ۳ - تابش/درخشش
        st.markdown("""
        <div class='question-box'>
            <strong>3️⃣ تابش و درخشش سنگ</strong>
        </div>
        """, unsafe_allow_html=True)
        
        luster_type = st.selectbox(
            "نوع درخشش:",
            ["متالیک (فلزی)", "شیشه‌ای", "الماسی", "مرواری", "خاک‌ریزی"],
            label_visibility="collapsed"
        )
        
        luster_scores = {
            "متالیک (فلزی)": 80,
            "شیشه‌ای": 70,
            "الماسی": 95,
            "مرواری": 60,
            "خاک‌ریزی": 30
        }
        answers["luster_score"] = luster_scores[luster_type] / 100
        
        st.markdown("""
        <div class='answer-suggestion'>
        💡 درخشش متالیک معمول برای طلا است. درخشش الماسی برای جواهرات قیمتی است
        </div>
        """, unsafe_allow_html=True)
        
        # سؤال ۴ - ساختار بلوری
        st.markdown("""
        <div class='question-box'>
            <strong>4️⃣ ساختار بلوری</strong>
        </div>
        """, unsafe_allow_html=True)
        
        crystal_form = st.multiselect(
            "فرم‌های بلوری دیده‌شده:",
            ["بلور شش‌گوش", "بلور مکعبی", "بلور مثلث‌شکل", "بدون ساختار واضح"],
            label_visibility="collapsed"
        )
        
        answers["crystal_structure"] = (len(crystal_form) / 4) * 100
        
        st.markdown("""
        <div class='answer-suggestion'>
        💡 وجود ساختار بلوری واضح نشانه‌ی یک معدن قیمتی است
        </div>
        """, unsafe_allow_html=True)
        
        # سؤال ۵ - وزن مخصوص
        st.markdown("""
        <div class='question-box'>
            <strong>5️⃣ وزن و چگالی</strong>
        </div>
        """, unsafe_allow_html=True)
        
        weight_test = st.select_slider(
            "آزمایش وزن:",
            options=[
                "بسیار سبک",
                "سبک",
                "متوسط",
                "سنگین",
                "بسیار سنگین"
            ],
            label_visibility="collapsed"
        )
        
        weight_scores = {
            "بسیار سبک": 20,
            "سبک": 40,
            "متوسط": 60,
            "سنگین": 80,
            "بسیار سنگین": 95
        }
        answers["gravity_score"] = weight_scores[weight_test] / 100
        
        st.markdown("""
        <div class='answer-suggestion'>
        💡 طلا بسیار سنگین است! اگر سنگ شما بسیار سنگین است، احتمال بالا برای طلا
        </div>
        """, unsafe_allow_html=True)
        
        # سؤال ۶ - ارتباط کانی‌ای
        st.markdown("""
        <div class='question-box'>
            <strong>6️⃣ آیا کوارتز سفید در اطراف دیده می‌شود؟</strong>
        </div>
        """, unsafe_allow_html=True)
        
        quartz = st.checkbox("✅ بله، کوارتز سفید دیده می‌شود", value=False)
        answers["quartz_association"] = 1 if quartz else 0
        
        st.markdown("""
        <div class='answer-suggestion'>
        💡 کوارتز اغلب با طلا همراه است! وجود آن بسیار خوب است
        </div>
        """, unsafe_allow_html=True)
        
        # سؤال ۷ - خطوط اکسیداسیون
        st.markdown("""
        <div class='question-box'>
            <strong>7️⃣ آثار اکسیداسیون و تغییر رنگ</strong>
        </div>
        """, unsafe_allow_html=True)
        
        oxidation_level = st.slider(
            "میزان اکسیداسیون (%):",
            0, 100, 50,
            label_visibility="collapsed"
        )
        answers["oxidation"] = oxidation_level / 100
        
        st.markdown("""
        <div class='answer-suggestion'>
        💡 اکسیداسیون شدید ممکن است نشانه‌ی سن زیاد معدن باشد
        </div>
        """, unsafe_allow_html=True)
        
        # سؤال ۸ - شکاف‌خوری
        st.markdown("""
        <div class='question-box'>
            <strong>8️⃣ شکاف‌خوری و الگوی شکست</strong>
        </div>
        """, unsafe_allow_html=True)
        
        cleavage_description = st.text_area(
            "توضیح شکاف‌خوری:",
            placeholder="آیا سنگ در خطوط مشخصی شکسته می‌شود؟ الگو چگونه است؟",
            label_visibility="collapsed"
        )
        
        cleavage_quality = st.slider(
            "کیفیت شکاف‌خوری:",
            0, 100, 50,
            label_visibility="collapsed"
        )
        answers["cleavage"] = cleavage_quality / 100
        
        # دکمه ارسال
        submitted = st.form_submit_button(
            "📊 تجزیه و تحلیل نتایج",
            use_container_width=True
        )
    
    if submitted and answers:
        # تجزیه جیولوژیکی
        analyzer = GeologicalAnalyzer()
        report = analyzer.generate_geological_report(answers, province)
        
        # ذخیره در دیتابیس
        analysis_id = add_analysis(
            date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            latitude=latitude,
            longitude=longitude,
            province=province,
            answers=answers,
            dashboard_score=report["score"],
            location_type="field"
        )
        
        # نمایش نتایج
        display_results(report, province, analysis_id)

def display_results(report: dict, province: str, analysis_id: int):
    """نمایش نتایج تحلیل"""
    
    st.markdown("""
    <div class='dashboard'>
        <h2>📊 نتایج تجزیه و تحلیل</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # امتیاز کلی
    col1, col2, col3 = st.columns(3)
    
    with col1:
        score_level = "🟢 عالی" if report["score"] > 75 else "🟡 متوسط" if report["score"] > 50 else "🔴 ضعیف"
        st.markdown(f"""
        <div class='metric-box' style='background: linear-gradient(135deg, #d4af37 0%, #ffd700 100%);'>
            <div>امتیاز کلی</div>
            <div style='font-size: 2.5em;'>{report["score"]:.1f}</div>
            <div>{score_level}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        gold_percent = report["gold_probability"] * 100
        st.markdown(f"""
        <div class='metric-box' style='background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);'>
            <div>احتمال طلا</div>
            <div style='font-size: 2.5em;'>{gold_percent:.0f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        gem_percent = report["gemstone_probability"] * 100
        st.markdown(f"""
        <div class='metric-box' style='background: linear-gradient(135deg, #FF1493 0%, #FF69B4 100%);'>
            <div>احتمال جواهر</div>
            <div style='font-size: 2.5em;'>{gem_percent:.0f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    # تجزیه ساختاری
    st.markdown("""
    <div class='card'>
        <h3>🏗️ تجزیه ساختار</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        **فرم بلوری:**
        {report['structure_analysis']['crystal_form']}
        
        **نوع شکست:**
        {report['structure_analysis']['fracture_type']}
        """)
    
    with col2:
        st.markdown(f"""
        **شکاف‌خوری:**
        {report['structure_analysis']['cleavage_pattern']}
        
        **اکسیداسیون:**
        {report['structure_analysis']['oxidation_state']}
        """)
    
    # پیشنهادات عملی
    st.markdown("""
    <div class='card'>
        <h3>💡 پیشنهادات عملی</h3>
    </div>
    """, unsafe_allow_html=True)
    
    for i, rec in enumerate(report["recommendations"], 1):
        st.markdown(f"**{i}.** {rec}")
    
    # مراحل بعدی
    st.markdown("""
    <div class='card'>
        <h3>📋 مراحل بعدی</h3>
    </div>
    """, unsafe_allow_html=True)
    
    for step in report["next_steps"]:
        st.markdown(f"• {step}")
    
    # بخش نتیجه بررسی
    st.markdown("""
    <div class='dashboard'>
        <h3>🎯 نتیجه بررسی نهایی</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        result = st.radio(
            "نتیجه بررسی شما چیست؟",
            [
                "⏳ فعلاً بررسی نکردم",
                "❌ ارزش بررسی ندارد",
                "✅ بررسی کردم - طلا/جواهر داشت",
                "⚠️ بررسی کردم - چیزی نداشت"
            ],
            label_visibility="collapsed"
        )
    
    with col2:
        if st.button("💾 ذخیره نتیجه", use_container_width=True):
            add_result(analysis_id, "field_analysis", result)
            show_success_message("✅ نتیجه با موفقیت ذخیره شد!")
            
            # به‌روزرسانی مدل یادگیری
            total_count = get_analyses_count()
            if total_count >= 1000:
                success = 1 if "طلا/جواهر داشت" in result else 0
                update_learning_model(total_count, success)

def show_clinic_exploration():
    """بخش بررسی مطب (سنگ‌های ذخیره شده)"""
    
    show_avatar_with_animation("💼", "بخش شناسایی سنگ‌های مطب!")
    
    st.info("🏢 این بخش برای تجزیه سنگ‌های ذخیره شدهٔ در مطب است")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        <div class='card'>
            <h3>💎 معلومات سنگ</h3>
        </div>
        """, unsafe_allow_html=True)
        
        stone_name = st.text_input("نام یا شناخت سنگ:")
        stone_type = st.selectbox(
            "نوع سنگ:",
            ["نامعلوم", "طلا", "جواهر", "سنگ معدنی", "دفینه"]
        )
    
    with col2:
        st.markdown("""
        <div class='card'>
            <h3>📸 تصویر</h3>
        </div>
        """, unsafe_allow_html=True)
        
        clinic_image = st.file_uploader(
            "آپلود تصویر سنگ:",
            type=["jpg", "jpeg", "png"],
            key="clinic_image"
        )
    
    # سؤالات ساده‌تر برای مطب
    with st.form("clinic_form"):
        st.markdown("""
        <div class='dashboard'>
            <h3>❓ سؤالات تجزیه</h3>
        </div>
        """, unsafe_allow_html=True)
        
        clinic_answers = {}
        
        clinic_color = st.slider("رنگ و درخشش:", 0, 100, 50)
        clinic_answers["color"] = clinic_color
        
        clinic_hardness = st.select_slider(
            "سختی:",
            options=["نرم", "متوسط", "سخت", "بسیار سخت"]
        )
        clinic_answers["hardness"] = clinic_hardness
        
        clinic_notes = st.text_area("یادداشت‌های اضافی:")
        
        clinic_submitted = st.form_submit_button(
            "📝 تجزیه برای مطب",
            use_container_width=True
        )
    
    if clinic_submitted:
        show_success_message("✅ اطلاعات سنگ ذخیره شد!")

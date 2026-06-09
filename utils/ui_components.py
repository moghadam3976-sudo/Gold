# utils/ui_components.py
# -*- coding: utf-8 -*-
import streamlit as st

def load_custom_css():
    """بارگذاری CSS سفارشی با تم طلایی لاکچری"""
    css = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;600;700;900&display=swap');
        
        * {
            font-family: 'Vazirmatn', sans-serif;
            direction: rtl;
        }
        
        body {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #ffffff;
        }
        
        .main-header {
            text-align: center;
            background: linear-gradient(135deg, #d4af37 0%, #ffd700 50%, #d4af37 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            padding: 20px;
            border-radius: 10px;
            border: 2px solid #d4af37;
            box-shadow: 0 0 20px rgba(212, 175, 55, 0.3);
        }
        
        .main-header h1 {
            font-size: 2.5em;
            font-weight: 900;
            margin: 0;
            text-shadow: 0 2px 10px rgba(212, 175, 55, 0.2);
        }
        
        .subtitle {
            font-size: 1.1em;
            color: #d4af37;
            margin-top: 10px;
        }
        
        .card {
            background: linear-gradient(135deg, #2d2d44 0%, #3a3a52 100%);
            border: 2px solid #d4af37;
            border-radius: 15px;
            padding: 20px;
            margin: 15px 0;
            box-shadow: 0 8px 25px rgba(212, 175, 55, 0.15);
            transition: all 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 35px rgba(212, 175, 55, 0.25);
            border-color: #ffd700;
        }
        
        .metric-box {
            background: linear-gradient(135deg, #d4af37 0%, #ffd700 100%);
            color: #1a1a2e;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            font-weight: bold;
            font-size: 1.2em;
            box-shadow: 0 5px 20px rgba(212, 175, 55, 0.3);
        }
        
        .indicator-good {
            background: linear-gradient(135deg, #00d084 0%, #00ff9f 100%);
            color: #1a1a2e;
        }
        
        .indicator-warning {
            background: linear-gradient(135deg, #ff9500 0%, #ffb700 100%);
            color: white;
        }
        
        .indicator-danger {
            background: linear-gradient(135deg, #ff4757 0%, #ff6b7a 100%);
            color: white;
        }
        
        .dashboard {
            background: linear-gradient(135deg, #2d2d44 0%, #3a3a52 100%);
            border: 2px solid #d4af37;
            border-radius: 15px;
            padding: 25px;
            margin: 20px 0;
            box-shadow: 0 10px 40px rgba(212, 175, 55, 0.2);
        }
        
        .section-title {
            color: #ffd700;
            font-size: 1.8em;
            font-weight: 900;
            border-bottom: 3px solid #d4af37;
            padding-bottom: 10px;
            margin: 30px 0 20px 0;
        }
        
        .question-box {
            background: linear-gradient(135deg, #2d2d44 0%, #3a3a52 100%);
            border-right: 4px solid #d4af37;
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
        }
        
        .answer-suggestion {
            background: rgba(212, 175, 55, 0.1);
            border-right: 4px solid #00d084;
            padding: 10px;
            margin: 8px 0;
            border-radius: 5px;
            color: #00ff9f;
            font-size: 0.9em;
        }
        
        .footer {
            text-align: center;
            color: #d4af37;
            padding: 20px;
            border-top: 2px solid #d4af37;
            margin-top: 40px;
        }
        
        .avatar-container {
            text-align: center;
            margin: 20px 0;
        }
        
        .avatar {
            font-size: 4em;
            animation: float 3s ease-in-out infinite;
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-20px); }
        }
        
        .premium-badge {
            background: linear-gradient(135deg, #d4af37 0%, #ffd700 100%);
            color: #1a1a2e;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            display: inline-block;
            margin: 0 5px;
        }
        
        .stButton>button {
            background: linear-gradient(135deg, #d4af37 0%, #ffd700 100%) !important;
            color: #1a1a2e !important;
            font-weight: bold !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 10px 30px !important;
            transition: all 0.3s ease !important;
        }
        
        .stButton>button:hover {
            transform: scale(1.05) !important;
            box-shadow: 0 5px 20px rgba(212, 175, 55, 0.4) !important;
        }
        
        .stSelectbox, .stTextInput {
            direction: rtl;
        }
        
        .success-message {
            background: linear-gradient(135deg, #00d084 0%, #00ff9f 100%);
            color: #1a1a2e;
            padding: 15px;
            border-radius: 8px;
            font-weight: bold;
            margin: 10px 0;
        }
        
        .warning-message {
            background: linear-gradient(135deg, #ff9500 0%, #ffb700 100%);
            color: white;
            padding: 15px;
            border-radius: 8px;
            font-weight: bold;
            margin: 10px 0;
        }
        
        .danger-message {
            background: linear-gradient(135deg, #ff4757 0%, #ff6b7a 100%);
            color: white;
            padding: 15px;
            border-radius: 8px;
            font-weight: bold;
            margin: 10px 0;
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def show_avatar_with_animation(emoji="👩‍🔬", message="خوش آمدید!"):
    """نمایش آواتار متحرک"""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <div class='avatar-container'>
            <div class='avatar'>{emoji}</div>
            <p style='color: #d4af37; font-weight: bold; font-size: 1.2em;'>{message}</p>
        </div>
        """, unsafe_allow_html=True)

def show_metric_card(label, value, indicator_type="good"):
    """نمایش کارت معیار"""
    indicator_class = f"indicator-{indicator_type}"
    st.markdown(f"""
    <div class='metric-box {indicator_class}'>
        <div style='font-size: 0.9em; opacity: 0.8;'>{label}</div>
        <div style='font-size: 2em; margin-top: 10px;'>{value}</div>
    </div>
    """, unsafe_allow_html=True)

def show_question_with_hint(question, hint):
    """نمایش سؤال با راهنمایی"""
    st.markdown(f"""
    <div class='question-box'>
        <strong>❓ {question}</strong>
        <div class='answer-suggestion'>
        💡 {hint}
        </div>
    </div>
    """, unsafe_allow_html=True)

def show_success_message(text):
    """نمایش پیام موفقیت"""
    st.markdown(f"""
    <div class='success-message'>✅ {text}</div>
    """, unsafe_allow_html=True)

def show_warning_message(text):
    """نمایش پیام اخطار"""
    st.markdown(f"""
    <div class='warning-message'>⚠️ {text}</div>
    """, unsafe_allow_html=True)

def show_danger_message(text):
    """نمایش پیام خطر"""
    st.markdown(f"""
    <div class='danger-message'>🚨 {text}</div>
    """, unsafe_allow_html=True)

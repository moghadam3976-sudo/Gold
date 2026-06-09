import streamlit as st

def load_custom_css():
    st.markdown("""
    <style>
    .main-header {text-align: center; color: #ffd700; background-color: #1a1a2e; padding: 20px; border-radius: 10px; margin-bottom: 20px; border: 1px solid #d4af37;}
    .subtitle {color: #ffffff; font-size: 16px;}
    .footer {text-align: center; color: #888888; padding: 20px; font-size: 12px; margin-top: 50px;}
    div.stButton > button {background-color: #d4af37 !important; color: #1a1a2e !important; font-weight: bold !important; width: 100%; border-radius: 8px;}
    </style>
    """, unsafe_allow_html=True)

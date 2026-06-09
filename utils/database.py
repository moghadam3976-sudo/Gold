import streamlit as st

def initialize_database():
    if 'history' not in st.session_state:
        st.session_state['history'] = []

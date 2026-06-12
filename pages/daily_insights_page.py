# pages/daily_insights_page.py
# -*- coding: utf-8 -*-

import streamlit as st
import sqlite3
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
import urllib.request
import xml.etree.ElementTree as ET
import re
from rss_fetcher import get_live_news

news = get_live_news()

        

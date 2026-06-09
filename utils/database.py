# utils/database.py
# -*- coding: utf-8 -*-
import sqlite3
import os
import json
from datetime import datetime
from pathlib import Path

DATABASE_PATH = "data/gold_explorer.db"

def initialize_database():
    """راه‌اندازی دیتابیس"""
    Path("data").mkdir(exist_ok=True)
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # جدول تحلیل‌ها
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS analyses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        latitude REAL,
        longitude REAL,
        province TEXT,
        images_data TEXT,
        answers TEXT,
        indicators TEXT,
        dashboard_score REAL,
        final_result TEXT,
        location_type TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # جدول نتایج بررسی
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        analysis_id INTEGER,
        result_type TEXT,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (analysis_id) REFERENCES analyses(id)
    )
    """)
    
    # جدول مدل یادگیری
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS learning_model (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        total_analyses INTEGER DEFAULT 0,
        success_cases INTEGER DEFAULT 0,
        accuracy_score REAL DEFAULT 0.0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # جدول مطب
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clinic_analyses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        stone_name TEXT,
        stone_type TEXT,
        visual_characteristics TEXT,
        answers TEXT,
        indicators TEXT,
        dashboard_score REAL,
        recommendation TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    conn.commit()
    conn.close()

def add_analysis(date, latitude=None, longitude=None, province=None, 
                 images=None, answers=None, indicators=None, 
                 dashboard_score=0.0, final_result=None, location_type="field"):
    """ذخیره تحلیل جدید"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
    INSERT INTO analyses (date, latitude, longitude, province, 
                         images_data, answers, indicators, 
                         dashboard_score, final_result, location_type)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (date, latitude, longitude, province, 
          json.dumps(images or []), json.dumps(answers or {}),
          json.dumps(indicators or {}), dashboard_score, 
          final_result, location_type))
    
    conn.commit()
    analysis_id = cursor.lastrowid
    conn.close()
    
    return analysis_id

def add_result(analysis_id, result_type, description):
    """اضافه کردن نتیجه بررسی"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
    INSERT INTO results (analysis_id, result_type, description)
    VALUES (?, ?, ?)
    """, (analysis_id, result_type, description))
    
    conn.commit()
    conn.close()

def get_analyses_count():
    """دریافت تعداد تحلیل‌ها"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM analyses")
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_all_analyses():
    """دریافت تمام تحلیل‌ها"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, date, province, dashboard_score, final_result, created_at 
    FROM analyses ORDER BY created_at DESC
    """)
    data = cursor.fetchall()
    conn.close()
    return data

def update_learning_model(total, success):
    """به‌روزرسانی مدل یادگیری"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    accuracy = (success / total * 100) if total > 0 else 0
    
    cursor.execute("""
    UPDATE learning_model 
    SET total_analyses = ?, success_cases = ?, accuracy_score = ?
    WHERE id = 1
    """, (total, success, accuracy))
    
    if cursor.rowcount == 0:
        cursor.execute("""
        INSERT INTO learning_model (total_analyses, success_cases, accuracy_score)
        VALUES (?, ?, ?)
        """, (total, success, accuracy))
    
    conn.commit()
    conn.close()

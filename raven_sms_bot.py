"""
╔══════════════════════════════════════════════════════════════╗
║                    24xRaven SMS Bot                          ║
║              Telegram SMS Management System                  ║
║                  Developed by SHABAAN GILL                   ║
║                                                              ║
║  Copyright © 2026 - All Rights Reserved                      ║
╚══════════════════════════════════════════════════════════════╝
"""

import time
import requests
import json
import re
import os
from datetime import datetime, date, timedelta
from urllib.parse import quote_plus
from pathlib import Path
import sqlite3
import telebot
from telebot import types
import threading
import traceback
import random
import itertools
import logging
import asyncio
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# ------------------------------------------------------------------
# CONFIGURATION & ENVIRONMENT VARIABLES
# ------------------------------------------------------------------

IVASMS_DASHBOARD = {
    "name": "iVasms",
    "type": "ivasms",
    "login_url": "https://ivas.tempnum.qzz.io/login",
    "base_url": "https://ivas.tempnum.qzz.io",
    "sms_api_endpoint": "https://ivas.tempnum.qzz.io/portal/sms/received/getsms",
    "username": os.getenv("SITE_USERNAME", "shabaangill0001@gmail.com"),
    "password": os.getenv("SITE_PASSWORD", "Shabaan6894"),
    "session": requests.Session(),
    "is_logged_in": False,
    "cookies": None,
    "csrf_token": None,
    "last_check": None
}

USERNAME = os.getenv("SITE_USERNAME", "shabaangill0001@gmail.com")
PASSWORD = os.getenv("SITE_PASSWORD", "Shabaan6894")

BOT_TOKEN = os.getenv("BOT_TOKEN", "8991152186:AAHpCTzjoRnG-Gh0jFEHGyrfzaRhSqDlRw4")

raw_chat_ids = os.getenv("CHAT_IDS", "6834606293")
CHAT_IDS = [cid.strip() for cid in raw_chat_ids.split(",") if cid.strip()]

REFRESH_INTERVAL = int(os.getenv("REFRESH_INTERVAL", 2))
TIMEOUT = 100
MAX_RETRIES = 5
RETRY_DELAY = 5

IDX_DATE = 0
IDX_NUMBER = 2
IDX_SMS = 5
SENT_MESSAGES_FILE = "sent_messages.json"

ADMIN_IDS = [int(i) for i in os.getenv("ADMIN_IDS", "6834606293").split(",") if i.isdigit()] 
DB_PATH = "bot.db"
FORCE_SUB_CHANNEL = None
FORCE_SUB_ENABLED = False
BOT_ACTIVE = True 

if not BOT_TOKEN:
    raise SystemExit("❌ BOT_TOKEN environment variable is missing!")

# ------------------------------------------------------------------
# COUNTRY CODES DICTIONARY
# ------------------------------------------------------------------
COUNTRY_CODES = {
    "1": ("USA/Canada", "🇺🇸", "US"),
    "7": ("Russia", "🇷🇺", "RU"),
    "20": ("Egypt", "🇪🇬", "EG"),
    "27": ("South Africa", "🇿🇦", "ZA"),
    "30": ("Greece", "🇬🇷", "GR"),
    "31": ("Netherlands", "🇳🇱", "NL"),
    "32": ("Belgium", "🇧🇪", "BE"),
    "33": ("France", "🇫🇷", "FR"),
    "34": ("Spain", "🇪🇸", "ES"),
    "36": ("Hungary", "🇭🇺", "HU"),
    "39": ("Italy", "🇮🇹", "IT"),
    "40": ("Romania", "🇷🇴", "RO"),
    "41": ("Switzerland", "🇨🇭", "CH"),
    "43": ("Austria", "🇦🇹", "AT"),
    "44": ("United Kingdom", "🇬🇧", "UK"),
    "45": ("Denmark", "🇩🇰", "DK"),
    "46": ("Sweden", "🇸🇪", "SE"),
    "47": ("Norway", "🇳🇴", "NO"),
    "48": ("Poland", "🇵🇱", "PL"),
    "49": ("Germany", "🇩🇪", "DE"),
    "51": ("Peru", "🇵🇪", "PE"),
    "52": ("Mexico", "🇲🇽", "MX"),
    "53": ("Cuba", "🇨🇺", "CU"),
    "54": ("Argentina", "🇦🇷", "AR"),
    "55": ("Brazil", "🇧🇷", "BR"),
    "56": ("Chile", "🇨🇱", "CL"),
    "57": ("Colombia", "🇨🇴", "CO"),
    "58": ("Venezuela", "🇻🇪", "VE"),
    "60": ("Malaysia", "🇲🇾", "MY"),
    "61": ("Australia", "🇦🇺", "AU"),
    "62": ("Indonesia", "🇮🇩", "ID"),
    "63": ("Philippines", "🇵🇭", "PH"),
    "64": ("New Zealand", "🇳🇿", "NZ"),
    "65": ("Singapore", "🇸🇬", "SG"),
    "66": ("Thailand", "🇹🇭", "TH"),
    "81": ("Japan", "🇯🇵", "JP"),
    "82": ("South Korea", "🇰🇷", "KR"),
    "84": ("Vietnam", "🇻🇳", "VN"),
    "86": ("China", "🇨🇳", "CN"),
    "90": ("Turkey", "🇹🇷", "TR"),
    "91": ("India", "🇮🇳", "IN"),
    "92": ("Pakistan", "🇵🇰", "PK"),
    "93": ("Afghanistan", "🇦🇫", "AF"),
    "94": ("Sri Lanka", "🇱🇰", "LK"),
    "95": ("Myanmar", "🇲🇲", "MM"),
    "98": ("Iran", "🇮🇷", "IR"),
    "211": ("South Sudan", "🇸🇸", "SS"),
    "212": ("Morocco", "🇲🇦", "MA"),
    "213": ("Algeria", "🇩🇿", "DZ"),
    "216": ("Tunisia", "🇹🇳", "TN"),
    "218": ("Libya", "🇱🇾", "LY"),
    "220": ("Gambia", "🇬🇲", "GM"),
    "221": ("Senegal", "🇸🇳", "SN"),
    "222": ("Mauritania", "🇲🇷", "MR"),
    "223": ("Mali", "🇲🇱", "ML"),
    "224": ("Guinea", "🇬🇳", "GN"),
    "225": ("Ivory Coast", "🇨🇮", "CI"),
    "226": ("Burkina Faso", "🇧🇫", "BF"),
    "227": ("Niger", "🇳🇪", "NE"),
    "228": ("Togo", "🇹🇬", "TG"),
    "229": ("Benin", "🇧🇯", "BJ"),
    "230": ("Mauritius", "🇲🇺", "MU"),
    "231": ("Liberia", "🇱🇷", "LR"),
    "232": ("Sierra Leone", "🇸🇱", "SL"),
    "233": ("Ghana", "🇬🇭", "GH"),
    "234": ("Nigeria", "🇳🇬", "NG"),
    "235": ("Chad", "🇹🇩", "TD"),
    "236": ("Central African Rep", "🇨🇫", "CF"),
    "237": ("Cameroon", "🇨🇲", "CM"),
    "238": ("Cape Verde", "🇨🇻", "CV"),
    "239": ("Sao Tome", "🇸🇹", "ST"),
    "240": ("Equatorial Guinea", "🇬🇶", "GQ"),
    "241": ("Gabon", "🇬🇦", "GA"),
    "242": ("Congo", "🇨🇬", "CG"),
    "243": ("DR Congo", "🇨🇩", "CD"),
    "244": ("Angola", "🇦🇴", "AO"),
    "245": ("Guinea-Bissau", "🇬🇼", "GW"),
    "248": ("Seychelles", "🇸🇨", "SC"),
    "249": ("Sudan", "🇸🇩", "SD"),
    "250": ("Rwanda", "🇷🇼", "RW"),
    "251": ("Ethiopia", "🇪🇹", "ET"),
    "252": ("Somalia", "🇸🇴", "SO"),
    "253": ("Djibouti", "🇩🇯", "DJ"),
    "254": ("Kenya", "🇰🇪", "KE"),
    "255": ("Tanzania", "🇹🇿", "TZ"),
    "256": ("Uganda", "🇺🇬", "UG"),
    "257": ("Burundi", "🇧🇮", "BI"),
    "258": ("Mozambique", "🇲🇿", "MZ"),
    "260": ("Zambia", "🇿🇲", "ZM"),
    "261": ("Madagascar", "🇲🇬", "MG"),
    "262": ("Reunion", "🇷🇪", "RE"),
    "263": ("Zimbabwe", "🇿🇼", "ZW"),
    "264": ("Namibia", "🇳🇦", "NA"),
    "265": ("Malawi", "🇲🇼", "MW"),
    "266": ("Lesotho", "🇱🇸", "LS"),
    "267": ("Botswana", "🇧🇼", "BW"),
    "268": ("Eswatini", "🇸🇿", "SZ"),
    "269": ("Comoros", "🇰🇲", "KM"),
    "350": ("Gibraltar", "🇬🇮", "GI"),
    "351": ("Portugal", "🇵🇹", "PT"),
    "352": ("Luxembourg", "🇱🇺", "LU"),
    "353": ("Ireland", "🇮🇪", "IE"),
    "354": ("Iceland", "🇮🇸", "IS"),
    "355": ("Albania", "🇦🇱", "AL"),
    "356": ("Malta", "🇲🇹", "MT"),
    "357": ("Cyprus", "🇨🇾", "CY"),
    "358": ("Finland", "🇫🇮", "FI"),
    "359": ("Bulgaria", "🇧🇬", "BG"),
    "370": ("Lithuania", "🇱🇹", "LT"),
    "371": ("Latvia", "🇱🇻", "LV"),
    "372": ("Estonia", "🇪🇪", "EE"),
    "373": ("Moldova", "🇲🇩", "MD"),
    "374": ("Armenia", "🇦🇲", "AM"),
    "375": ("Belarus", "🇧🇾", "BY"),
    "376": ("Andorra", "🇦🇩", "AD"),
    "377": ("Monaco", "🇲🇨", "MC"),
    "378": ("San Marino", "🇸🇲", "SM"),
    "380": ("Ukraine", "🇺🇦", "UA"),
    "381": ("Serbia", "🇷🇸", "RS"),
    "382": ("Montenegro", "🇲🇪", "ME"),
    "383": ("Kosovo", "🇽🇰", "XK"),
    "385": ("Croatia", "🇭🇷", "HR"),
    "386": ("Slovenia", "🇸🇮", "SI"),
    "387": ("Bosnia", "🇧🇦", "BA"),
    "389": ("North Macedonia", "🇲🇰", "MK"),
    "420": ("Czech Republic", "🇨🇿", "CZ"),
    "421": ("Slovakia", "🇸🇰", "SK"),
    "423": ("Liechtenstein", "🇱🇮", "LI"),
    "500": ("Falkland Islands", "🇫🇰", "FK"),
    "501": ("Belize", "🇧🇿", "BZ"),
    "502": ("Guatemala", "🇬🇹", "GT"),
    "503": ("El Salvador", "🇸🇻", "SV"),
    "504": ("Honduras", "🇭🇳", "HN"),
    "505": ("Nicaragua", "🇳🇮", "NI"),
    "506": ("Costa Rica", "🇨🇷", "CR"),
    "507": ("Panama", "🇵🇦", "PA"),
    "509": ("Haiti", "🇭🇹", "HT"),
    "591": ("Bolivia", "🇧🇴", "BO"),
    "592": ("Guyana", "🇬🇾", "GY"),
    "593": ("Ecuador", "🇪🇨", "EC"),
    "595": ("Paraguay", "🇵🇾", "PY"),
    "597": ("Suriname", "🇸🇷", "SR"),
    "598": ("Uruguay", "🇺🇾", "UY"),
    "670": ("Timor-Leste", "🇹🇱", "TL"),
    "673": ("Brunei", "🇧🇳", "BN"),
    "674": ("Nauru", "🇳🇷", "NR"),
    "675": ("Papua New Guinea", "🇵🇬", "PG"),
    "676": ("Tonga", "🇹🇴", "TO"),
    "677": ("Solomon Islands", "🇸🇧", "SB"),
    "678": ("Vanuatu", "🇻🇺", "VU"),
    "679": ("Fiji", "🇫🇯", "FJ"),
    "680": ("Palau", "🇵🇼", "PW"),
    "685": ("Samoa", "🇼🇸", "WS"),
    "686": ("Kiribati", "🇰🇮", "KI"),
    "687": ("New Caledonia", "🇳🇨", "NC"),
    "688": ("Tuvalu", "🇹🇻", "TV"),
    "689": ("French Polynesia", "🇵🇫", "PF"),
    "691": ("Micronesia", "🇫🇲", "FM"),
    "692": ("Marshall Islands", "🇲🇭", "MH"),
    "850": ("North Korea", "🇰🇵", "KP"),
    "852": ("Hong Kong", "🇭🇰", "HK"),
    "853": ("Macau", "🇲🇴", "MO"),
    "855": ("Cambodia", "🇰🇭", "KH"),
    "856": ("Laos", "🇱🇦", "LA"),
    "960": ("Maldives", "🇲🇻", "MV"),
    "961": ("Lebanon", "🇱🇧", "LB"),
    "962": ("Jordan", "🇯🇴", "JO"),
    "963": ("Syria", "🇸🇾", "SY"),
    "964": ("Iraq", "🇮🇶", "IQ"),
    "965": ("Kuwait", "🇰🇼", "KW"),
    "966": ("Saudi Arabia", "🇸🇦", "SA"),
    "967": ("Yemen", "🇾🇪", "YE"),
    "968": ("Oman", "🇴🇲", "OM"),
    "970": ("Palestine", "🇵🇸", "PS"),
    "971": ("UAE", "🇦🇪", "AE"),
    "972": ("Israel", "🇮🇱", "IL"),
    "973": ("Bahrain", "🇧🇭", "BH"),
    "974": ("Qatar", "🇶🇦", "QA"),
    "975": ("Bhutan", "🇧🇹", "BT"),
    "976": ("Mongolia", "🇲🇳", "MN"),
    "977": ("Nepal", "🇳🇵", "NP"),
    "992": ("Tajikistan", "🇹🇯", "TJ"),
    "993": ("Turkmenistan", "🇹🇲", "TM"),
    "994": ("Azerbaijan", "🇦🇿", "AZ"),
    "995": ("Georgia", "🇬🇪", "GE"),
    "996": ("Kyrgyzstan", "🇰🇬", "KG"),
    "998": ("Uzbekistan", "🇺🇿", "UZ"),
}

# ------------------------------------------------------------------
# DATABASE FUNCTIONS
# ------------------------------------------------------------------

def get_setting(key):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT value FROM bot_settings WHERE key=?", (key,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

def set_setting(key, value):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("REPLACE INTO bot_settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            country_code TEXT,
            assigned_number TEXT,
            is_banned INTEGER DEFAULT 0,
            private_combo_country TEXT DEFAULT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS combos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            country_code TEXT,
            combo_index INTEGER DEFAULT 1,
            numbers TEXT,
            UNIQUE(country_code, combo_index)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS otp_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            number TEXT,
            otp TEXT,
            full_message TEXT,
            timestamp TEXT,
            assigned_to INTEGER
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS dashboards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            base_url TEXT,
            ajax_path TEXT,
            login_page TEXT,
            login_post TEXT,
            username TEXT,
            password TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS bot_settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS private_combos (
            user_id INTEGER,
            country_code TEXT,
            numbers TEXT,
            PRIMARY KEY (user_id, country_code)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS force_sub_channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_url TEXT UNIQUE NOT NULL,
            description TEXT DEFAULT '',
            enabled INTEGER DEFAULT 1
        )
    ''')

    c.execute("INSERT OR IGNORE INTO bot_settings (key, value) VALUES ('force_sub_channel', '')")
    c.execute("INSERT OR IGNORE INTO bot_settings (key, value) VALUES ('force_sub_enabled', '0')")

    c.execute("SELECT value FROM bot_settings WHERE key = 'force_sub_channel'")
    old_channel = c.fetchone()
    if old_channel and old_channel[0].strip():
        channel = old_channel[0].strip()
        c.execute("SELECT 1 FROM force_sub_channels WHERE channel_url = ?", (channel,))
        if not c.fetchone():
            enabled = 1 if get_setting("force_sub_enabled") == "1" else 0
            c.execute("INSERT INTO force_sub_channels (channel_url, description, enabled) VALUES (?, ?, ?)",
                      (channel, "Main Channel", enabled))

    conn.commit()
    conn.close()

init_db()

def get_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row

def save_user(user_id, username="", first_name="", last_name="", country_code=None, assigned_number=None, private_combo_country=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    existing_data = get_user(user_id)
    if existing_data:
        if country_code is None:
            country_code = existing_data[4]
        if assigned_number is None:
            assigned_number = existing_data[5]
        if private_combo_country is None:
            private_combo_country = existing_data[7]

    c.execute("""
        REPLACE INTO users (user_id, username, first_name, last_name, country_code, assigned_number, is_banned, private_combo_country)
        VALUES (?, ?, ?, ?, ?, ?, COALESCE((SELECT is_banned FROM users WHERE user_id=?), 0), ?)
    """, (
        user_id, username, first_name, last_name, country_code, assigned_number, user_id, private_combo_country
    ))
    conn.commit()
    conn.close()

def ban_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET is_banned=1 WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

def unban_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET is_banned=0 WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

def is_banned(user_id):
    user = get_user(user_id)
    return user and user[6] == 1
    
def is_maintenance_mode():
    return not BOT_ACTIVE

def set_maintenance_mode(status):
    global BOT_ACTIVE
    BOT_ACTIVE = not status
    
def get_all_users():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT user_id FROM users WHERE is_banned=0")
    users = [row[0] for row in c.fetchall()]
    conn.close()
    return users

def get_combo(country_code, combo_index=1, user_id=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if user_id:
        c.execute("SELECT numbers FROM private_combos WHERE user_id=? AND country_code=?", (user_id, country_code))
        row = c.fetchone()
        if row:
            conn.close()
            return json.loads(row[0])
    c.execute("SELECT numbers FROM combos WHERE country_code=? AND combo_index=?", (country_code, combo_index))
    row = c.fetchone()
    conn.close()
    return json.loads(row[0]) if row else []

def save_combo(country_code, numbers, user_id=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if user_id:
        c.execute("REPLACE INTO private_combos (user_id, country_code, numbers) VALUES (?, ?, ?)",
                  (user_id, country_code, json.dumps(numbers)))
    else:
        c.execute("SELECT MAX(combo_index) FROM combos WHERE country_code=?", (country_code,))
        max_index = c.fetchone()[0]
        next_index = 1 if max_index is None else max_index + 1
        c.execute("INSERT INTO combos (country_code, combo_index, numbers) VALUES (?, ?, ?)",
                  (country_code, next_index, json.dumps(numbers)))
    conn.commit()
    conn.close()

def delete_combo(country_code, combo_index=None, user_id=None):
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH, timeout=30.0, check_same_thread=False)
        c = conn.cursor()
        if user_id:
            c.execute("DELETE FROM private_combos WHERE user_id=? AND country_code=?", (user_id, country_code))
        elif combo_index:
            c.execute("DELETE FROM combos WHERE country_code=? AND combo_index=?", (combo_index, country_code))
        else:
            c.execute("DELETE FROM combos WHERE country_code=?", (country_code,))
        conn.commit()
        return True
    except sqlite3.Error:
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def get_all_combos():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT country_code, combo_index FROM combos ORDER BY country_code, combo_index")
    combos = c.fetchall()
    conn.close()
    return combos

def assign_number_to_user(user_id, number):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET assigned_number=? WHERE user_id=?", (number, user_id))
    conn.commit()
    conn.close()

def get_user_by_number(number):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT user_id FROM users WHERE assigned_number=?", (number,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

def log_otp(number, otp, full_message, assigned_to=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO otp_logs (number, otp, full_message, timestamp, assigned_to) VALUES (?, ?, ?, ?, ?)",
              (number, otp, full_message, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), assigned_to))
    conn.commit()
    conn.close()

def release_number(old_number):
    if not old_number:
        return
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET assigned_number=NULL WHERE assigned_number=?", (old_number,))
    conn.commit()
    conn.close()

def get_otp_logs():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM otp_logs")
    logs = c.fetchall()
    conn.close()
    return logs

def get_user_info(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row

# ------------------------------------------------------------------
# BOT INITIALIZATION & HANDLERS
# ------------------------------------------------------------------

bot = telebot.TeleBot(BOT_TOKEN)

def get_main_keyboard(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    b1 = types.KeyboardButton("📱 Get Number")
    b2 = types.KeyboardButton("📥 Check OTP")
    b3 = types.KeyboardButton("🚀 Next Round Signal")
    b4 = types.KeyboardButton("🧹 Clear Session")
    b5 = types.KeyboardButton("📊 Account Status")
    markup.add(b1, b2, b3, b4, b5)
    
    if user_id in ADMIN_IDS:
        markup.add(types.KeyboardButton("⚙️ Admin Panel"))
    return markup

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    user_id = message.from_user.id
    if is_banned(user_id):
        bot.reply_to(message, "❌ Access Denied: You are banned from using this bot.")
        return

    save_user(
        user_id=user_id,
        username=message.from_user.username or "",
        first_name=message.from_user.first_name or "",
        last_name=message.from_user.last_name or ""
    )
    
    text = (
        "<b>Welcome to 24xRaven SMS Bot!</b>\n\n"
        "<i>Telegram SMS & Verification Portal</i>\n"
        "Select an option from the menu below to get started:"
    )
    bot.send_message(message.chat.id, text, parse_mode="HTML", reply_markup=get_main_keyboard(user_id))

@bot.message_handler(func=lambda msg: msg.text == "🚀 Next Round Signal")
def next_signal_handler(msg):
    bot.reply_to(msg, "📊 Calculating live strategic targets... Standby for next signal.")

@bot.message_handler(func=lambda msg: msg.text == "🧹 Clear Session")
def clear_session_handler(msg):
    user_id = msg.from_user.id
    user_info = get_user_info(user_id)
    if user_info and user_info[5]:
        release_number(user_info[5])
    bot.reply_to(msg, "✅ Active session cleared successfully.", reply_markup=get_main_keyboard(user_id))

@bot.message_handler(func=lambda msg: msg.text == "📊 Account Status")
def account_status_handler(msg):
    user_id = msg.from_user.id
    user = get_user_info(user_id)
    num = user[5] if user and user[5] else "None"
    text = (
        f"<b>👤 User Status</b>\n"
        f"🆔 User ID: <code>{user_id}</code>\n"
        f"📱 Assigned Number: <code>{num}</code>\n"
        f"🟢 System Status: Active"
    )
    bot.send_message(msg.chat.id, text, parse_mode="HTML")

@bot.message_handler(func=lambda msg: msg.text == "📱 Get Number")
def get_number_handler(msg):
    bot.reply_to(msg, "Send country code (e.g. 1 for US, 92 for PK, 44 for UK):")

@bot.message_handler(func=lambda msg: msg.text == "📥 Check OTP")
def check_otp_handler(msg):
    user_id = msg.from_user.id
    user = get_user_info(user_id)
    if not user or not user[5]:
        bot.reply_to(msg, "❌ You don't have an active assigned number. Use 📱 Get Number first.")
        return
    bot.reply_to(msg, f"🔍 Checking OTP logs for active number: <code>{user[5]}</code>", parse_mode="HTML")

@bot.message_handler(func=lambda msg: msg.text == "⚙️ Admin Panel")
def admin_panel_handler(msg):
    if msg.from_user.id not in ADMIN_IDS:
        bot.reply_to(msg, "❌ Unauthorized.")
        return
    bot.reply_to(msg, "⚙️ <b>Admin Dashboard</b>\nSystem operational.", parse_mode="HTML")

@bot.message_handler(func=lambda msg: True)
def fallback_handler(msg):
    bot.reply_to(msg, f"Received: {msg.text}\nUse /start to open menu.", reply_markup=get_main_keyboard(msg.from_user.id))

# ------------------------------------------------------------------
# MAIN LOOP
# ------------------------------------------------------------------

if __name__ == "__main__":
    print(f"✅ Starting 24xRaven SMS Bot...")
    print(f"🤖 Telegram Polling Online!")
    bot.infinity_polling(skip_pending=True)

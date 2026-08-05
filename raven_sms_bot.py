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
from datetime import datetime
import sqlite3
import telebot
from telebot import types
import threading
from bs4 import BeautifulSoup

# ------------------------------------------------------------------
# CONFIGURATION & ENVIRONMENT VARIABLES
# ------------------------------------------------------------------

IVASMS_DASHBOARD = {
    "name": "iVasms",
    "login_url": "https://ivasms.com/login",
    "base_url": "https://ivasms.com",
    "my_numbers_url": "https://ivasms.com/portal/numbers",
    "sms_api_endpoint": "https://ivasms.com/portal/sms/received/getsms",
    "username": os.getenv("SITE_USERNAME", "shabaangill0001@gmail.com"),
    "password": os.getenv("SITE_PASSWORD", "Shabaan@6894"),
    "session": requests.Session(),
    "is_logged_in": False
}

IVASMS_DASHBOARD["session"].headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "X-Requested-With": "XMLHttpRequest"
})

BOT_TOKEN = os.getenv("BOT_TOKEN", "8991152186:AAHpCTzjoRnG-Gh0jFEHGyrfzaRhSqDlRw4")

raw_chat_ids = os.getenv("CHAT_IDS", "6834606293")
CHAT_IDS = [cid.strip() for cid in raw_chat_ids.split(",") if cid.strip()]

REFRESH_INTERVAL = int(os.getenv("REFRESH_INTERVAL", 5)) 
ADMIN_IDS = [int(i) for i in os.getenv("ADMIN_IDS", "6834606293").split(",") if i.isdigit()] 
DB_PATH = "bot.db"

if not BOT_TOKEN:
    raise SystemExit("❌ BOT_TOKEN environment variable is missing!")

# ------------------------------------------------------------------
# COUNTRY CODES DICTIONARY
# ------------------------------------------------------------------
COUNTRY_CODES = {
    "1": ("USA/Canada", "🇺🇸"),
    "44": ("United Kingdom", "🇬🇧"),
    "92": ("Pakistan", "🇵🇰"),
    "93": ("Afghanistan", "🇦🇫"),
    "91": ("India", "🇮🇳"),
}

# ------------------------------------------------------------------
# DATABASE INITIALIZATION
# ------------------------------------------------------------------

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
            assigned_to INTEGER,
            UNIQUE(number, otp, full_message)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def save_user(user_id, username="", first_name="", last_name=""):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO users (user_id, username, first_name, last_name)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
        username=excluded.username, first_name=excluded.first_name, last_name=excluded.last_name
    """, (user_id, username, first_name, last_name))
    conn.commit()
    conn.close()

def save_combo(country_code, numbers):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT MAX(combo_index) FROM combos WHERE country_code=?", (country_code,))
    max_index = c.fetchone()[0]
    next_index = 1 if max_index is None else max_index + 1
    c.execute("INSERT INTO combos (country_code, combo_index, numbers) VALUES (?, ?, ?)",
              (country_code, next_index, json.dumps(numbers)))
    conn.commit()
    conn.close()

def get_combo(country_code):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT numbers FROM combos WHERE country_code=?", (country_code,))
    row = c.fetchone()
    conn.close()
    return json.loads(row[0]) if row else []

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

def is_otp_logged(number, otp, full_message):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT 1 FROM otp_logs WHERE number=? AND otp=? AND full_message=?", (number, otp, full_message))
    row = c.fetchone()
    conn.close()
    return row is not None

def log_otp(number, otp, full_message, assigned_to=None):
    if is_otp_logged(number, otp, full_message):
        return False
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO otp_logs (number, otp, full_message, timestamp, assigned_to) VALUES (?, ?, ?, ?, ?)",
            (number, otp, full_message, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), assigned_to)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_user_info(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row

def release_number(old_number):
    if not old_number:
        return
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET assigned_number=NULL WHERE assigned_number=?", (old_number,))
    conn.commit()
    conn.close()

# ------------------------------------------------------------------
# SESSION AUTHENTICATION & SCRAPER ENGINE
# ------------------------------------------------------------------

bot = telebot.TeleBot(BOT_TOKEN)

def ivasms_login():
    """Logs into ivasms.com and holds active user session."""
    session = IVASMS_DASHBOARD["session"]
    try:
        res = session.get(IVASMS_DASHBOARD["login_url"], timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        csrf_token = None
        token_elem = soup.find('input', {'name': '_token'}) or soup.find('input', {'name': 'csrf_token'})
        if token_elem:
            csrf_token = token_elem.get('value')

        login_payload = {
            "email": IVASMS_DASHBOARD["username"],
            "username": IVASMS_DASHBOARD["username"],
            "password": IVASMS_DASHBOARD["password"]
        }
        if csrf_token:
            login_payload["_token"] = csrf_token

        post_res = session.post(IVASMS_DASHBOARD["login_url"], data=login_payload, timeout=12)
        if post_res.status_code in [200, 302]:
            IVASMS_DASHBOARD["is_logged_in"] = True
            return True
    except Exception as e:
        print(f"❌ iVasms Session Login Error: {e}")
    return False

def fetch_live_ivasms_number(country_code):
    """Hits the DataTables AJAX endpoint and HTML web pages on ivasms.com to fetch live active numbers."""
    session = IVASMS_DASHBOARD["session"]
    
    if not IVASMS_DASHBOARD["is_logged_in"]:
        ivasms_login()

    # 1. Try DataTables AJAX Endpoints
    ajax_urls = [
        f"{IVASMS_DASHBOARD['base_url']}/portal/numbers/get_data",
        f"{IVASMS_DASHBOARD['base_url']}/portal/numbers/list",
        f"{IVASMS_DASHBOARD['base_url']}/portal/get_numbers"
    ]

    dt_payload = {
        "draw": "1",
        "start": "0",
        "length": "1000",
        "search[value]": str(country_code)
    }

    headers = {
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "application/json, text/javascript, */*; q=0.01"
    }

    for url in ajax_urls:
        try:
            resp = session.post(url, data=dt_payload, headers=headers, timeout=10)
            if resp.status_code == 200:
                text_data = resp.text
                matches = re.findall(rf'\b{country_code}?\d{{8,11}}\b', text_data)
                for num in matches:
                    full_num = num if num.startswith(country_code) else f"{country_code}{num}"
                    if len(full_num) >= 9:
                        return full_num
        except Exception as e:
            print(f"DataTables fetch error for {url}: {e}")

    # 2. Scrape Page Source & Table DOM Elements
    for page_url in [IVASMS_DASHBOARD["my_numbers_url"], f"{IVASMS_DASHBOARD['base_url']}/portal/numbers"]:
        try:
            resp = session.get(page_url, timeout=10)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                for td in soup.find_all(['td', 'span', 'div']):
                    text = td.get_text(strip=True)
                    if re.match(rf'^(?:\+{country_code}|00{country_code}|{country_code})?\d{{7,11}}$', text):
                        clean_num = re.sub(r'\D', '', text)
                        if not clean_num.startswith(country_code):
                            clean_num = f"{country_code}{clean_num}"
                        return clean_num
        except Exception as e:
            print(f"Page scrape error for {page_url}: {e}")

    return None

def auto_poll_ivasms():
    """Background engine fetching incoming OTPs from ivasms.com and forwarding to Telegram Group."""
    print("🚀 Automatic Live ivasms.com Group Broadcaster Active...")
    
    while True:
        try:
            session = IVASMS_DASHBOARD["session"]
            if not IVASMS_DASHBOARD["is_logged_in"]:
                ivasms_login()

            resp = session.get(IVASMS_DASHBOARD["sms_api_endpoint"], timeout=12)
            
            if resp.status_code == 200:
                try:
                    data = resp.json()
                    sms_list = data if isinstance(data, list) else data.get("messages", []) or data.get("sms", [])
                    
                    for item in sms_list:
                        number = str(item.get("number") or item.get("phone") or "Unknown")
                        full_msg = str(item.get("message") or item.get("full_message") or "")
                        otp = str(item.get("otp") or "")

                        if not otp:
                            match = re.search(r'\b\d{4,8}\b', full_msg)
                            otp = match.group(0) if match else "N/A"

                        assigned_user = get_user_by_number(number)

                        if log_otp(number, otp, full_msg, assigned_to=assigned_user):
                            broadcast_text = (
                                f"<b>📥 New Live OTP Received!</b>\n\n"
                                f"📱 <b>Number:</b> <code>{number}</code>\n"
                                f"🔑 <b>OTP Code:</b> <code>{otp}</code>\n"
                                f"💬 <b>Message:</b> {full_msg}\n"
                                f"🕒 <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                            )
                            if assigned_user:
                                broadcast_text += f"👤 <b>Assigned User ID:</b> <code>{assigned_user}</code>\n"

                            broadcast_text += "\n<i>Powered by 24xRaven SMS Engine</i>"

                            for chat_id in CHAT_IDS:
                                try:
                                    bot.send_message(chat_id, broadcast_text, parse_mode="HTML")
                                except Exception as err:
                                    print(f"❌ Group Broadcast Error for {chat_id}: {err}")

                except json.JSONDecodeError:
                    pass

        except Exception as e:
            print(f"⚠️ Polling Loop Notice: {e}")

        time.sleep(REFRESH_INTERVAL)

polling_thread = threading.Thread(target=auto_poll_ivasms, daemon=True)
polling_thread.start()

# ------------------------------------------------------------------
# TELEGRAM BOT HANDLERS
# ------------------------------------------------------------------

def get_main_keyboard(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    b1 = types.KeyboardButton("📱 Get Number")
    b2 = types.KeyboardButton("📥 Check OTP")
    b3 = types.KeyboardButton("🧹 Clear Session")
    b4 = types.KeyboardButton("📊 Account Status")
    markup.add(b1, b2, b3, b4)
    if user_id in ADMIN_IDS:
        markup.add(types.KeyboardButton("⚙️ Admin Panel"))
    return markup

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    user_id = message.from_user.id
    save_user(user_id, message.from_user.username or "", message.from_user.first_name or "")
    text = (
        "<b>Welcome to 24xRaven SMS Bot!</b>\n\n"
        "<i>All incoming OTPs generated on ivasms.com post live to our Telegram group automatically!</i>\n\n"
        "Tap <b>📱 Get Number</b> below and type <code>93</code> to grab an active Afghanistan number."
    )
    bot.send_message(message.chat.id, text, parse_mode="HTML", reply_markup=get_main_keyboard(user_id))

@bot.message_handler(func=lambda msg: msg.text == "📱 Get Number")
def get_number_handler(msg):
    sent_msg = bot.reply_to(msg, "Send country code (e.g. 93 for Afghanistan, 92 for PK, 44 for UK):")
    bot.register_next_step_handler(sent_msg, process_country_code)

def process_country_code(msg):
    user_id = msg.from_user.id
    code = msg.text.strip()
    
    if code.startswith("/") or code in ["📱 Get Number", "📥 Check OTP", "🧹 Clear Session", "📊 Account Status"]:
        bot.reply_to(msg, "Cancelled request.", reply_markup=get_main_keyboard(user_id))
        return

    bot.reply_to(msg, f"⏳ Connecting to ivasms.com for country +{code}...")

    # 1. Scrape live number from ivasms.com
    assigned_num = fetch_live_ivasms_number(code)

    # 2. Database Stock Fallback
    if not assigned_num:
        numbers = get_combo(code)
        if numbers:
            assigned_num = numbers[0]

    if not assigned_num:
        bot.reply_to(
            msg, 
            f"❌ No live numbers found for country code <code>+{code}</code> on ivasms.com.\n\n"
            f"<i>Admin can add backup stock anytime using:</i>\n<code>/addcombo {code} number1,number2</code>", 
            parse_mode="HTML", 
            reply_markup=get_main_keyboard(user_id)
        )
        return

    assign_number_to_user(user_id, assigned_num)
    country_info = COUNTRY_CODES.get(code, ("Unknown", "🌐"))

    response = (
        f"<b>{country_info[1]} Number Assigned!</b>\n\n"
        f"<b>Country:</b> {country_info[0]} (+{code})\n"
        f"<b>Number:</b> <code>{assigned_num}</code>\n\n"
        f"<i>Trigger your OTP now. All incoming messages for this number will automatically broadcast live in your Telegram group!</i>"
    )
    bot.send_message(msg.chat.id, response, parse_mode="HTML", reply_markup=get_main_keyboard(user_id))

@bot.message_handler(commands=['addcombo'])
def add_combo_handler(msg):
    if msg.from_user.id not in ADMIN_IDS:
        bot.reply_to(msg, "❌ Unauthorized.")
        return
    try:
        parts = msg.text.split(" ", 2)
        if len(parts) < 3:
            bot.reply_to(msg, "Usage: /addcombo country_code num1,num2")
            return
            
        code = parts[1].strip()
        num_list = [n.strip() for n in parts[2].split(",") if n.strip()]
        
        save_combo(code, num_list)
        bot.reply_to(msg, f"✅ Added {len(num_list)} numbers for country code +{code}!")
    except Exception as e:
        bot.reply_to(msg, f"❌ Error adding combo: {e}")

@bot.message_handler(func=lambda msg: msg.text == "📥 Check OTP")
def check_otp_handler(msg):
    user_id = msg.from_user.id
    user = get_user_info(user_id)
    if not user or not user[5]:
        bot.reply_to(msg, "❌ No active assigned number. Tap 📱 Get Number first.")
        return
    
    assigned_num = user[5]
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT otp, full_message, timestamp FROM otp_logs WHERE number=? ORDER BY id DESC LIMIT 5", (assigned_num,))
    logs = c.fetchall()
    conn.close()

    if not logs:
        bot.reply_to(msg, f"⏳ No SMS received yet for <code>{assigned_num}</code>.", parse_mode="HTML")
        return

    text = f"<b>📥 Latest SMS Logs for <code>{assigned_num}</code>:</b>\n\n"
    for log in logs:
        otp, full_msg, tstamp = log
        text += f"🔑 <b>OTP:</b> <code>{otp}</code>\n💬 <b>MSG:</b> {full_msg}\n🕒 <i>{tstamp}</i>\n-------------------\n"
    
    bot.send_message(msg.chat.id, text, parse_mode="HTML")

@bot.message_handler(func=lambda msg: msg.text == "🧹 Clear Session")
def clear_session_handler(msg):
    user_id = msg.from_user.id
    user_info = get_user_info(user_id)
    if user_info and user_info[5]:
        release_number(user_info[5])
    bot.reply_to(msg, "✅ Session cleared successfully.", reply_markup=get_main_keyboard(user_id))

@bot.message_handler(func=lambda msg: msg.text == "📊 Account Status")
def account_status_handler(msg):
    user_id = msg.from_user.id
    user = get_user_info(user_id)
    num = user[5] if user and user[5] else "None"
    bot.reply_to(msg, f"<b>👤 User Status</b>\n🆔 ID: <code>{user_id}</code>\n📱 Active Number: <code>{num}</code>\n🟢 Live Group Broadcaster: Active", parse_mode="HTML")

@bot.message_handler(func=lambda msg: True)
def fallback_handler(msg):
    bot.reply_to(msg, f"Received: {msg.text}\nUse /start to open menu.", reply_markup=get_main_keyboard(msg.from_user.id))

# ------------------------------------------------------------------
# MAIN ENTRY POINT
# ------------------------------------------------------------------

if __name__ == "__main__":
    print("✅ Starting 24xRaven SMS Bot...")
    bot.infinity_polling(skip_pending=True)

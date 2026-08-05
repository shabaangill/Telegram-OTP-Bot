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
import random
from datetime import datetime
import sqlite3
import telebot
from telebot import types
import threading
from bs4 import BeautifulSoup
import pandas as pd

# ------------------------------------------------------------------
# CONFIGURATION & ENVIRONMENT VARIABLES
# ------------------------------------------------------------------

OTP_GROUP_LINK = os.getenv("OTP_GROUP_LINK", "https://t.me/your_otp_group_link")

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

raw_chat_ids = os.getenv("CHAT_IDS", "-100XXXXXXXXXX")
CHAT_IDS = [cid.strip() for cid in raw_chat_ids.split(",") if cid.strip()]

REFRESH_INTERVAL = int(os.getenv("REFRESH_INTERVAL", 5)) 
ADMIN_IDS = [int(i) for i in os.getenv("ADMIN_IDS", "6834606293").split(",") if i.isdigit()] 
DB_PATH = "bot.db"

if not BOT_TOKEN:
    raise SystemExit("❌ BOT_TOKEN environment variable is missing!")

# ------------------------------------------------------------------
# PLATFORMS & COUNTRY CODES DICTIONARIES
# ------------------------------------------------------------------

PLATFORMS = {
    "wa": ("WhatsApp", "💬"),
    "tg": ("Telegram", "✈️"),
    "tt": ("TikTok", "🎵"),
    "fb": ("Facebook", "📘"),
    "ig": ("Instagram", "📸"),
    "go": ("Google / Gmail", "📧"),
    "nf": ("Netflix", "🎬"),
    "ai": ("OpenAI / ChatGPT", "🤖")
}

COUNTRY_CODES = {
    "93": ("Afghanistan", "🇦🇫"),
    "966": ("Saudi Arabia", "🇸🇦"),
    "225": ("Ivory Coast", "🇨🇮"),
    "243": ("Congo", "🇨🇩"),
    "92": ("Pakistan", "🇵🇰"),
    "1": ("USA/Canada", "🇺🇸"),
    "44": ("United Kingdom", "🇬🇧"),
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
# EXCEL READER & SCRAPER ENGINE
# ------------------------------------------------------------------

bot = telebot.TeleBot(BOT_TOKEN)

def get_random_number_from_excel(country_code):
    """Reads numbers from numbers.xlsx by matching country names or numerical prefixes."""
    excel_path = "numbers.xlsx"
    if os.path.exists(excel_path):
        try:
            df = pd.read_excel(excel_path, skiprows=2, dtype=str)
            df.iloc[:, 0] = df.iloc[:, 0].fillna("")  # Col A (Range/Country Name)
            df.iloc[:, 2] = df.iloc[:, 2].fillna("")  # Col C (Numbers)

            valid_numbers = []
            country_name = COUNTRY_CODES.get(str(country_code), ("", ""))[0].upper()
            
            for index, row in df.iterrows():
                col_a_text = str(row.iloc[0]).upper()
                col_c_text = str(row.iloc[2])

                num_match = re.search(r'\b\d{8,12}\b', col_c_text)
                if num_match:
                    clean_number = num_match.group(0)

                    code_match = str(country_code) in col_a_text or clean_number.startswith(str(country_code))
                    name_match = country_name and country_name in col_a_text

                    if country_code == "225" and ("IVORY" in col_a_text or "COTE" in col_a_text):
                        name_match = True

                    if code_match or name_match:
                        valid_numbers.append(clean_number)

            if valid_numbers:
                return random.choice(valid_numbers)

        except Exception as e:
            print(f"Error reading numbers.xlsx: {e}")
            
    return None

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
# TELEGRAM BOT HANDLERS & INLINE KEYBOARDS
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

def get_platform_selection_keyboard():
    """Generates an inline grid of social media platforms."""
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = []
    for code, (name, icon) in PLATFORMS.items():
        btn_text = f"{icon} {name}"
        buttons.append(types.InlineKeyboardButton(btn_text, callback_data=f"platform_{code}"))
    markup.add(*buttons)
    return markup

def get_country_selection_keyboard(platform_code):
    """Generates an inline grid of countries after platform is chosen."""
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = []
    for code, (name, flag) in COUNTRY_CODES.items():
        btn_text = f"{flag} {name} (+{code})"
        buttons.append(types.InlineKeyboardButton(btn_text, callback_data=f"getnum_{platform_code}_{code}"))
    markup.add(*buttons)
    return markup

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    user_id = message.from_user.id
    save_user(user_id, message.from_user.username or "", message.from_user.first_name or "")
    text = (
        "<b>Welcome to 24xRaven SMS Bot!</b>\n\n"
        "<i>All incoming OTPs generated on ivasms.com post live to our Telegram group automatically!</i>\n\n"
        "Tap <b>📱 Get Number</b> below to pick a service and get an active number."
    )
    bot.send_message(message.chat.id, text, parse_mode="HTML", reply_markup=get_main_keyboard(user_id))

@bot.message_handler(func=lambda msg: msg.text == "📱 Get Number")
def get_number_handler(msg):
    text = "<b>📱 Select a Social Media Platform:</b>"
    bot.send_message(msg.chat.id, text, parse_mode="HTML", reply_markup=get_platform_selection_keyboard())

@bot.callback_query_handler(func=lambda call: call.data.startswith("platform_"))
def process_platform_callback(call):
    platform_code = call.data.split("_")[1]
    platform_info = PLATFORMS.get(platform_code, ("Selected Service", "🌐"))
    
    bot.answer_callback_query(call.id, text=f"Selected {platform_info[0]}")
    
    text = f"<b>{platform_info[1]} Service: {platform_info[0]}</b>\n\n<b>🌍 Now select a country:</b>"
    bot.edit_message_text(
        text, 
        chat_id=call.message.chat.id, 
        message_id=call.message.message_id, 
        parse_mode="HTML", 
        reply_markup=get_country_selection_keyboard(platform_code)
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("getnum_"))
def process_country_callback(call):
    parts = call.data.split("_")
    platform_code = parts[1]
    code = parts[2]
    user_id = call.from_user.id

    bot.answer_callback_query(call.id, text="Fetching random number from numbers.xlsx...")

    # 1. Fetch random number from numbers.xlsx
    assigned_num = get_random_number_from_excel(code)

    # 2. Scrape live number from ivasms.com if not in excel
    if not assigned_num:
        assigned_num = fetch_live_ivasms_number(code)

    # 3. Local DB Fallback
    if not assigned_num:
        numbers = get_combo(code)
        if numbers:
            assigned_num = random.choice(numbers)

    if not assigned_num:
        bot.send_message(
            call.message.chat.id, 
            f"❌ No numbers found for country code <code>+{code}</code> right now.\n\n"
            f"<i>Please try another country or verify stock in numbers.xlsx.</i>", 
            parse_mode="HTML"
        )
        return

    assign_number_to_user(user_id, assigned_num)
    country_info = COUNTRY_CODES.get(code, ("Unknown", "🌐"))
    platform_info = PLATFORMS.get(platform_code, ("Selected Service", "📱"))

    redirect_markup = types.InlineKeyboardMarkup()
    redirect_btn = types.InlineKeyboardButton("📢 View Live OTP Group", url=OTP_GROUP_LINK)
    redirect_markup.add(redirect_btn)

    response = (
        f"<b>{country_info[1]} Number Assigned!</b>\n\n"
        f"<b>Service:</b> {platform_info[1]} {platform_info[0]}\n"
        f"<b>Country:</b> {country_info[0]} (+{code})\n"
        f"<b>Number:</b> <code>{assigned_num}</code>\n\n"
        f"<i>Trigger your OTP now. Click below to view the incoming code in our live group!</i>"
    )
    bot.send_message(call.message.chat.id, response, parse_mode="HTML", reply_markup=redirect_markup)

@bot.message_handler(func=lambda msg: msg.text == "📥 Check OTP")
def check_otp_handler(msg):
    user_id = msg.from_user.id
    user = get_user_info(user_id)
    if not user or not user[5]:
        bot.reply_to(msg, "❌ No active assigned number. Tap 📱 Get Number first.")
        return
    
    assigned_num = user[5]

    redirect_markup = types.InlineKeyboardMarkup()
    redirect_btn = types.InlineKeyboardButton("🚀 Go to OTP Info Group", url=OTP_GROUP_LINK)
    redirect_markup.add(redirect_btn)

    text = (
        f"<b>📱 Assigned Number:</b> <code>{assigned_num}</code>\n\n"
        f"<i>All incoming OTP codes for this number are automatically streamed directly to our official group! Click below to view:</i>"
    )
    bot.send_message(msg.chat.id, text, parse_mode="HTML", reply_markup=redirect_markup)

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

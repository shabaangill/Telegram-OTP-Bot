# Setup Guide | دليل الإعداد

## 24xRaven SMS Bot - Complete Setup Instructions

**Developed by ✘ 𝙍𝘼𝙑𝙀𝙉**

---

## Important Security Notice | تنبيه أمني مهم

**NEVER commit sensitive information to Git!**

**لا تقم أبداً برفع المعلومات الحساسة على Git!**

This includes:
- Bot tokens
- Passwords
- User IDs
- Database files
- Configuration files with secrets

---

## Step-by-Step Setup | الإعداد خطوة بخطوة

### Step 1: Get Your Bot Token | الخطوة 1: احصل على توكن البوت

1. Open Telegram and search for **@BotFather**
2. Send `/newbot` command
3. Choose a name for your bot
4. Choose a username (must end with 'bot')
5. Copy the token

**Example:**
```
Token: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz-EXAMPLE
```

---

### Step 2: Get Your User ID | الخطوة 2: احصل على ID الخاص بك

1. Open Telegram and search for **@userinfobot**
2. Start the bot
3. Copy your user ID

**Example:**
```
User ID: 1234567890
```

---

### Step 3: Get Chat ID | الخطوة 3: احصل على معرف المجموعة

For a group or channel:
1. Add your bot to the group/channel
2. Send a message in the group
3. Visit: `https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates`
4. Find the chat ID in the response

**Example:**
```
Chat ID: -1001234567890
```

---

### Step 4: iVasms Account | الخطوة 4: حساب iVasms

1. Register at [iVasms](https://ivas.tempnum.qzz.io/)
2. Verify your email
3. Note your login credentials

---

### Step 5: Configure the Bot | الخطوة 5: إعداد البوت

Open `raven_sms_bot.py` and find these lines:

```python
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
ADMIN_IDS = [0000000000]
CHAT_IDS = ["YOUR_CHAT_ID_HERE"]

IVASMS_DASHBOARD = {
    "username": "YOUR_EMAIL_HERE",
    "password": "YOUR_PASSWORD_HERE",
    # ...
}

USERNAME = "YOUR_USERNAME_HERE"
PASSWORD = "YOUR_SITE_PASSWORD_HERE"
```

Replace with your actual values:

```python
BOT_TOKEN = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz-EXAMPLE"
ADMIN_IDS = [1234567890]
CHAT_IDS = ["-1001234567890"]

IVASMS_DASHBOARD = {
    "username": "your_email@example.com",
    "password": "your_password",
    # ...
}

USERNAME = "your_username"
PASSWORD = "your_password"
```

---

### Step 6: Install Dependencies | الخطوة 6: تثبيت المكتبات

```bash
pip install -r requirements.txt
```

---

### Step 7: Run the Bot | الخطوة 7: تشغيل البوت

```bash
python raven_sms_bot.py
```

You should see:
```
[INFO] Bot started successfully
[INFO] Listening for messages...
```

---

## Testing | الاختبار

### Test 1: Basic Functionality

1. Open Telegram
2. Search for your bot
3. Send `/start`
4. You should see the welcome message

### Test 2: Number Assignment

1. Click on a country button
2. You should receive a number
3. Check if OTP messages arrive

### Test 3: Admin Panel

1. Click "Admin Panel" (only visible to admins)
2. Test adding/removing combos
3. Check user management features

---

## Troubleshooting | حل المشاكل

### Problem: "Unauthorized" Error

**Cause**: Wrong bot token

**Solution**:
1. Check your token from @BotFather
2. Make sure there are no extra spaces
3. Verify the token in your configuration

---

### Problem: Bot doesn't respond

**Possible causes**:
1. Bot is not running
2. Wrong bot username
3. Bot was blocked by user
4. Network issues

**Solution**:
1. Check if bot process is running
2. Verify bot username
3. Restart the bot
4. Check internet connection

---

### Problem: Database errors

**Cause**: Corrupted database or permission issues

**Solution**:
```bash
# Delete old database
rm bot.db

# Restart bot (will create new database)
python raven_sms_bot.py
```

---

### Problem: iVasms login fails

**Cause**: Wrong credentials or site is down

**Solution**:
1. Verify your credentials
2. Check if site is accessible
3. Try logging in manually on the website

---

## Security Checklist | قائمة التحقق الأمنية

Before running your bot, make sure:

- [ ] `.env` file is in `.gitignore`
- [ ] `bot.db` is in `.gitignore`
- [ ] No tokens in code (if using .env)
- [ ] File permissions are correct
- [ ] You're not sharing your tokens with anyone

---

## Need Help? | تحتاج مساعدة؟

If you're still having issues:

- Read the [README](README.md)
- Join our [Telegram Channel](https://t.me/Raven_xx24)
- Email: hsh34811@gmail.com

---

<div align="center">

**Setup Complete! 🎉**

**الإعداد مكتمل! 🎉**

Your bot is ready to use!

البوت جاهز للاستخدام!

---

Made with ❤️ by ✘ 𝙍𝘼𝙑𝙀𝙉

Copyright © 2026 - All Rights Reserved

</div>

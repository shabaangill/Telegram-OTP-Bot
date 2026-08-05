<div align="center">

<h1>
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=32&duration=2800&pause=2000&color=00D9FF&center=true&vCenter=true&width=600&lines=iVasms+Dashboard+Bot;%E2%9C%98+%F0%9D%99%8D%F0%9D%98%BC%F0%9D%99%91%F0%9D%99%80%F0%9D%99%89;Telegram+SMS+Manager;Welcome+to+the+Project!" alt="Typing SVG" />
</h1>

<p align="center">
  <img src="https://cdn.simpleicons.org/python/3776AB" alt="Python" width="60" height="60"/>
  <img src="https://cdn.simpleicons.org/telegram/26A5E4" alt="Telegram" width="60" height="60"/>
  <img src="https://cdn.simpleicons.org/sqlite/003B57" alt="SQLite" width="60" height="60"/>
</p>

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Telegram](https://img.shields.io/badge/Telegram-Bot-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/Raven_xx24)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)]()

**بوت تليجرام احترافي متصل بلوحة iVasms لإدارة أرقام SMS وتوزيعها تلقائياً**

[العربية](#arabic) • [English](#english)

</div>

---

<div id="arabic">

## المحتويات

- [نظرة عامة](#نظرة-عامة)
- [المميزات](#المميزات)
- [التثبيت](#التثبيت)
- [الإعداد](#الإعداد)
- [الاستخدام](#الاستخدام)
- [الأوامر](#الأوامر)
- [المتطلبات](#المتطلبات)
- [الترخيص](#الترخيص)
- [التواصل](#التواصل)

## نظرة عامة

iVasms Dashboard Bot هو بوت تليجرام متقدم متصل بلوحة iVasms لإدارة وتوزيع أرقام SMS بشكل تلقائي. يدعم البوت عدة دول ويوفر نظام إدارة متكامل للمستخدمين والأرقام.

<div align="center">

| الميزة | الوصف |
|--------|-------|
| إدارة الأرقام | توزيع تلقائي للأرقام على المستخدمين |
| دعم متعدد الدول | أكثر من 150 دولة مدعومة |
| نظام الكومبوهات | إمكانية إنشاء مجموعات أرقام مخصصة |
| لوحة تحكم | لوحة تحكم كاملة للإدارة |
| قاعدة بيانات | SQLite لحفظ البيانات |

</div>

## المميزات

### إدارة الأرقام
- توزيع تلقائي للأرقام على المستخدمين
- دعم الكومبوهات العامة والخاصة
- تتبع الأرقام المستخدمة
- سجل كامل لرسائل OTP

### نظام المستخدمين
- تسجيل تلقائي للمستخدمين الجدد
- نظام حظر وإلغاء حظر
- إحصائيات مفصلة
- دعم الاشتراك الإجباري

### لوحة التحكم
- إضافة وحذف الكومبوهات
- إدارة المستخدمين
- عرض السجلات
- وضع الصيانة
- إرسال رسائل جماعية

### الأمان
- نظام صلاحيات متقدم
- حماية من الاستخدام غير المصرح
- تشفير البيانات الحساسة
- سجل كامل للعمليات

## التثبيت

### المتطلبات الأساسية
- Python 3.8 أو أحدث
- حساب Telegram Bot (من [@BotFather](https://t.me/BotFather))
- حساب على موقع iVasms

### خطوات التثبيت

1. **استنساخ المشروع**
```bash
git clone https://github.com/hsh34811-hash/iVasms-Dashboard-Bot.git
cd iVasms-Dashboard-Bot
```

2. **تثبيت المكتبات**
```bash
pip install -r requirements.txt
```

3. **إعداد البوت**
- افتح ملف `raven_sms_bot.py`
- غير المتغيرات التالية:
  - `BOT_TOKEN`: توكن البوت من BotFather
  - `ADMIN_IDS`: معرف التليجرام الخاص بك
  - `CHAT_IDS`: معرف المجموعة أو القناة
  - `USERNAME` و `PASSWORD`: بيانات موقع iVasms

4. **تشغيل البوت**
```bash
python raven_sms_bot.py
```

## الإعداد

### الحصول على Bot Token

1. افتح [@BotFather](https://t.me/BotFather) على تليجرام
2. أرسل `/newbot`
3. اتبع التعليمات
4. انسخ التوكن

### الحصول على معرف التليجرام

1. افتح [@userinfobot](https://t.me/userinfobot)
2. ابدأ المحادثة
3. انسخ معرفك (User ID)

### إعداد الملف

```python
# في ملف raven_sms_bot.py

BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
ADMIN_IDS = [YOUR_TELEGRAM_ID]
CHAT_IDS = ["YOUR_CHAT_ID"]

# بيانات موقع iVasms
IVASMS_DASHBOARD = {
    "username": "your_email@example.com",
    "password": "your_password",
    # ...
}
```

## الاستخدام

### للمستخدمين

1. ابدأ المحادثة مع البوت `/start`
2. اختر الدولة المطلوبة
3. احصل على رقم تلقائياً
4. استقبل رسائل OTP

### للإدارة

استخدم لوحة التحكم للوصول إلى:
- إدارة الكومبوهات
- إدارة المستخدمين
- عرض الإحصائيات
- إعدادات البوت

## الأوامر

### أوامر المستخدمين

| الأمر | الوصف |
|------|------|
| `/start` | بدء البوت وعرض القائمة الرئيسية |

### أوامر الإدارة

| الأمر | الوصف |
|------|------|
| لوحة التحكم | الوصول إلى لوحة الإدارة |
| إضافة كومبو | إضافة مجموعة أرقام جديدة |
| حذف كومبو | حذف مجموعة أرقام |
| حظر مستخدم | منع مستخدم من استخدام البوت |
| إلغاء الحظر | السماح لمستخدم محظور |
| الإحصائيات | عرض إحصائيات البوت |

## المتطلبات

```txt
requests>=2.32.5
pyTelegramBotAPI>=4.31.0
beautifulsoup4>=4.14.3
httpx>=0.28.1
```

## الهيكل

```
iVasms-Dashboard-Bot/
├── raven_sms_bot.py      # الملف الرئيسي
├── requirements.txt       # المكتبات المطلوبة
├── bot.db                # قاعدة البيانات (يتم إنشاؤها تلقائياً)
├── sent_messages.json    # سجل الرسائل المرسلة
├── README.md             # التوثيق
├── LICENSE               # الترخيص
└── .gitignore           # ملفات Git المستبعدة
```

## الترخيص

هذا المشروع مرخص تحت رخصة MIT - انظر ملف [LICENSE](LICENSE) للتفاصيل.

```
Copyright © 2026 ✘ 𝙍𝘼𝙑𝙀𝙉 - All Rights Reserved
```

## التواصل

<div align="center">

<p align="center">
  <a href="https://github.com/hsh34811-hash">
    <img src="https://cdn.simpleicons.org/github/181717" alt="GitHub" width="50" height="50"/>
  </a>
  <a href="https://t.me/P_X_24">
    <img src="https://cdn.simpleicons.org/telegram/26A5E4" alt="Telegram" width="50" height="50"/>
  </a>
  <a href="mailto:hsh34811@gmail.com">
    <img src="https://cdn.simpleicons.org/gmail/EA4335" alt="Email" width="50" height="50"/>
  </a>
</p>

[![GitHub](https://img.shields.io/badge/GitHub-hsh34811--hash-181717?style=for-the-badge&logo=github)](https://github.com/hsh34811-hash)
[![Telegram](https://img.shields.io/badge/Telegram-@P__X__24-2CA5E0?style=for-the-badge&logo=telegram)](https://t.me/P_X_24)
[![Channel](https://img.shields.io/badge/Channel-Raven__xx24-2CA5E0?style=for-the-badge&logo=telegram)](https://t.me/Raven_xx24)
[![Email](https://img.shields.io/badge/Email-hsh34811@gmail.com-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:hsh34811@gmail.com)

</div>

---

</div>

<div id="english">

## Contents

- [Overview](#overview-en)
- [Features](#features-en)
- [Installation](#installation-en)
- [Configuration](#configuration-en)
- [Usage](#usage-en)
- [Commands](#commands-en)
- [Requirements](#requirements-en)
- [License](#license-en)
- [Contact](#contact-en)

## Overview {#overview-en}

iVasms Dashboard Bot is an advanced Telegram bot connected to iVasms dashboard to manage and distribute SMS numbers automatically. The bot supports multiple countries and provides a complete management system for users and numbers.

<div align="center">

| Feature | Description |
|---------|-------------|
| Number Management | Automatic distribution of numbers to users |
| Multi-Country Support | Over 150 supported countries |
| Combo System | Ability to create custom number groups |
| Control Panel | Complete admin dashboard |
| Database | SQLite for data persistence |

</div>

## Features {#features-en}

### Number Management
- Automatic number distribution to users
- Support for public and private combos
- Track used numbers
- Complete OTP message log

### User System
- Automatic registration of new users
- Ban and unban system
- Detailed statistics
- Force subscribe support

### Control Panel
- Add and delete combos
- User management
- View logs
- Maintenance mode
- Broadcast messages

### Security
- Advanced permission system
- Protection from unauthorized use
- Sensitive data encryption
- Complete operation log

## Installation {#installation-en}

### Prerequisites
- Python 3.8 or newer
- Telegram Bot account (from [@BotFather](https://t.me/BotFather))
- iVasms website account

### Installation Steps

1. **Clone the project**
```bash
git clone https://github.com/hsh34811-hash/iVasms-Dashboard-Bot.git
cd iVasms-Dashboard-Bot
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure the bot**
- Open `raven_sms_bot.py`
- Change the following variables:
  - `BOT_TOKEN`: Bot token from BotFather
  - `ADMIN_IDS`: Your Telegram ID
  - `CHAT_IDS`: Group or channel ID
  - `USERNAME` and `PASSWORD`: iVasms credentials

4. **Run the bot**
```bash
python raven_sms_bot.py
```

## Configuration {#configuration-en}

### Getting Bot Token

1. Open [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot`
3. Follow instructions
4. Copy the token

### Getting Telegram ID

1. Open [@userinfobot](https://t.me/userinfobot)
2. Start the conversation
3. Copy your ID (User ID)

### File Configuration

```python
# In raven_sms_bot.py file

BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
ADMIN_IDS = [YOUR_TELEGRAM_ID]
CHAT_IDS = ["YOUR_CHAT_ID"]

# iVasms credentials
IVASMS_DASHBOARD = {
    "username": "your_email@example.com",
    "password": "your_password",
    # ...
}
```

## Usage {#usage-en}

### For Users

1. Start conversation with bot `/start`
2. Choose desired country
3. Get number automatically
4. Receive OTP messages

### For Admins

Use control panel to access:
- Combo management
- User management
- View statistics
- Bot settings

## Commands {#commands-en}

### User Commands

| Command | Description |
|---------|-------------|
| `/start` | Start bot and show main menu |

### Admin Commands

| Command | Description |
|---------|-------------|
| Control Panel | Access admin dashboard |
| Add Combo | Add new number group |
| Delete Combo | Remove number group |
| Ban User | Prevent user from using bot |
| Unban User | Allow banned user |
| Statistics | View bot statistics |

## Requirements {#requirements-en}

```txt
requests>=2.32.5
pyTelegramBotAPI>=4.31.0
beautifulsoup4>=4.14.3
httpx>=0.28.1
```

## License {#license-en}

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
Copyright © 2026 ✘ 𝙍𝘼𝙑𝙀𝙉 - All Rights Reserved
```

## Contact {#contact-en}

<div align="center">

<p align="center">
  <a href="https://github.com/hsh34811-hash">
    <img src="https://cdn.simpleicons.org/github/181717" alt="GitHub" width="50" height="50"/>
  </a>
  <a href="https://t.me/P_X_24">
    <img src="https://cdn.simpleicons.org/telegram/26A5E4" alt="Telegram" width="50" height="50"/>
  </a>
  <a href="mailto:hsh34811@gmail.com">
    <img src="https://cdn.simpleicons.org/gmail/EA4335" alt="Email" width="50" height="50"/>
  </a>
</p>

[![GitHub](https://img.shields.io/badge/GitHub-hsh34811--hash-181717?style=for-the-badge&logo=github)](https://github.com/hsh34811-hash)
[![Telegram](https://img.shields.io/badge/Telegram-@P__X__24-2CA5E0?style=for-the-badge&logo=telegram)](https://t.me/P_X_24)
[![Channel](https://img.shields.io/badge/Channel-Raven__xx24-2CA5E0?style=for-the-badge&logo=telegram)](https://t.me/Raven_xx24)
[![Email](https://img.shields.io/badge/Email-hsh34811@gmail.com-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:hsh34811@gmail.com)

</div>

---

<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&pause=1000&color=00FFFF&center=true&vCenter=true&width=600&lines=Thanks+for+Visiting!;Made+with+%E2%9D%A4%EF%B8%8F+by+%E2%9C%98+%F0%9D%99%8D%F0%9D%98%BC%F0%9D%99%91%F0%9D%99%80%F0%9D%99%89;Let's+Build+Together!;Happy+Coding!" alt="Typing SVG" />

### إذا أعجبك المشروع، لا تنسى إضافة نجمة | If you like the project, don't forget to star it

**Developed by ✘ 𝙍𝘼𝙑𝙀𝙉**

**Copyright © 2026 - All Rights Reserved**

</div>

</div>

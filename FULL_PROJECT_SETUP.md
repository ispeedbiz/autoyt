# 🔧 Full Project Setup Guide: AutoYT - Automated YouTube Video Generation

This guide provides **step-by-step instructions** to set up the entire AutoYT project on your system (Mac or Windows) with Google Sheets, OpenAI, ElevenLabs, and YouTube API integration.

---

## 📁 Folder Structure

```
autoyt/
├── main.py                  # Main script to process and post videos
├── suggest_topics.py        # Suggests new topics and fills Google Sheet
├── utils.py                 # Helper utilities (env loading, sanitizing, etc.)
├── .env                     # Environment variables (you create this)
├── .gitignore
├── requirements.txt
├── README.md
├── videos/                  # Folder where each video folder is created
│   └── video_<date>_<title>/
│       ├── script.txt
│       ├── output.mp3
│       ├── thumbnail.jpg
│       ├── final_video.mp4
│       └── final_prompt.txt
```

## ⚙️ TECHNICAL CHECKLIST (Must-Haves)

✅ Area

What to Ensure

✅ requirements.txt

Installed via pip install -r requirements.txt

✅ .env file

Contains valid API keys (OpenAI, ElevenLabs, Telegram)

✅ service_account.json

Added to your Google Sheet with Editor access

✅ client_secret.json

Used for YouTube OAuth + token.pickle gets generated

✅ main.py

Checks publish datetime before processing any row

✅ suggest_topics.py

Auto-generates 10-day content plan in Hindi

✅ Thumbnail Generator

Uses image + fallback to clean text overlay

✅ Cronjob Setup

Automates posting based on system time

✅ Logs & Error Capture

Alerts via Telegram + logs saved if configured


---

## ⚙️ Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/ispeedbiz/autoyt.git
cd autoyt
```

### 2. Create a virtual environment and activate it

**Mac/Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

---

## 📦 Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔐 Environment Configuration (.env)

Create a `.env` file in the root with the following:

```
OPENAI_API_KEY=your_openai_key
ELEVENLABS_API_KEY=your_elevenlabs_key
TELEGRAM_BOT_TOKEN=optional_bot_token
TELEGRAM_CHAT_ID=optional_chat_id
```

---

## 🔗 Google Sheets Setup

1. Create a Google Sheet with predefined columns (as shown in README).
2. Share it with your Google service account (from JSON file).
3. Place the `service_account.json` in the project root.
4. Update `SHEET_NAME` and `WORKSHEET_INDEX` in `main.py`.

---

## ▶️ YouTube API Setup

1. Create OAuth credentials from Google Developer Console.
2. Download `client_secret.json` and place it in root.
3. First upload will prompt for OAuth via browser.

---

## 🔊 ElevenLabs API Setup

1. Create account on [https://www.elevenlabs.io/](https://www.elevenlabs.io/)
2. Get your API key.
3. Add it to your `.env` file.

---

## ⏰ Cron Job (for auto publishing)

Use `cron` or `Task Scheduler` to run `main.py` periodically:

**Mac/Linux:**

```bash
crontab -e
```

```
0 * * * * cd /path/to/project && /bin/bash -c 'source venv/bin/activate && python main.py'
```

**Windows (Task Scheduler):**
- Create Basic Task → Trigger Daily → Action → Start a Program → `python.exe main.py`

---

## ✨ Output Example (Per Video)

```
videos/
└── video_2025-06-27_Elon_Musk/
    ├── script.txt
    ├── output.mp3
    ├── thumbnail.jpg
    ├── final_video.mp4
    └── final_prompt.txt
```

---

## 🧠 Auto Topic Suggestion

Run this command manually or on schedule:

```bash
python suggest_topics.py
```

---

## ☑️ Google Sheet Columns (Editable)

- Book/Topic
- Language
- Custom Title (optional)
- Notes (optional)
- Publish Date
- Thumbnail Text
- Tone
- Highlights
- Audience
- CTA
- Duration
- Thumbnail Source

---

## 🔁 Google Sheet Columns (Auto Updated)

- Status
- YouTube Link
- Last Updated
- Error Message
- Processing Time

---

## API Connections

✅ Google Sheets API

Uses service_account.json

Add this service account as Editor to your Google Sheet

Required scopes:

https://www.googleapis.com/auth/spreadsheets

https://www.googleapis.com/auth/drive

✅ YouTube Data API

Uses client_secret.json

Triggers OAuth flow on first run of main.py

Saves a token.pickle file for reuse

✅ ElevenLabs (Voiceover)

Provide API key in .env

Uses default voice or your custom Hindi voice

✅ OpenAI (Script Generation)

Uses GPT-4o model

Prompts are carefully crafted for engaging, humanlike narration

## 🛡️ License

This project is licensed under the MIT License.

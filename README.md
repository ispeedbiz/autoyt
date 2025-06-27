## autoyt
100% Autonomous Hindi Audiobook &amp; Knowledge YouTube Channel Generator. AI creates, voices, thumbnails, renders, and uploads scheduled videos from a Google Sheet—fully automated, Mac/Windows friendly.

## AutoYT – Fully Autonomous Hindi YouTube Channel Generator

AI-powered pipeline to generate, voice, thumbnail, render, and upload high-quality scheduled Hindi knowledge videos for YouTube—directly from a Google Sheet!

## AutoYT: Fully Automated AI-Powered YouTube Video Generator

**AutoYT** is a powerful automation pipeline that creates, voices, and uploads Hindi YouTube audiobook summaries — inspired by channels like *Syllabus with Rohit*. This tool is designed for creators who want to run YouTube channels fully autonomously.

---

## 🔧 Project Features

- ✅ Suggests topics based on audience & trends
- ✅ Generates Hindi scripts (with smart use of English)
- ✅ Converts text to natural AI voice (ElevenLabs or alternatives)
- ✅ Auto-generates thumbnails (with book/person/AUTO support)
- ✅ Compiles voice + image into 720p video using FFmpeg
- ✅ Uploads to YouTube with correct metadata, tags, thumbnail
- ✅ Updates Google Sheets (status, URL, error, timestamps)
- ✅ Fully scheduled via cron (videos post at specified times)

---

## 🗂️ Folder Structure

```
AutoYT/
│
├── main.py                 # Main automation pipeline
├── suggest_topics.py       # Topic suggester via GPT
├── utils.py                # Helper functions
├── .env                    # Environment variables (see below)
├── requirements.txt        # Dependencies
│
├── videos/                 # All generated content by topic/date
│   └── [Topic]-[Date]/
│       ├── script.txt
│       ├── output.mp3
│       ├── thumbnail.jpg
│       └── final_video.mp4
│
├── service_account.json    # Google Sheet API key (for gspread)
├── client_secret.json      # YouTube OAuth file
└── README.md
```

---

## 🔐 Environment Setup

Create a `.env` file like this:

```
OPENAI_API_KEY=your-openai-api-key
ELEVENLABS_API_KEY=your-elevenlabs-api-key
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_CHAT_ID=your-chat-id
```

---

## 📗 Google Sheet Setup

- The script connects to a Google Sheet like:
  `Back to Zero – Input Sheet`
- Required columns:
  ```
  Book/Topic | Language | Custom Title | Notes | Publish Date | Status | YouTube Link | Last Updated At | Error | Processing Time | ... (more for thumbnail/tone/highlights)
  ```

> Use `service_account.json` to connect via [gspread](https://docs.gspread.org/en/latest/).

---

## 📹 YouTube API Setup

1. Create OAuth client on [Google Cloud Console](https://console.cloud.google.com)
2. Download `client_secret.json`
3. Script will generate `token.pickle` on first upload.
4. Make sure you have YouTube Data API v3 enabled.

---

## 🗣️ Voice Generation (ElevenLabs)

- Uses [ElevenLabs](https://www.elevenlabs.io) API
- Requires an API key
- You can switch to alternatives like Coqui, Bark, or TTSMaker

---

## 📸 Thumbnails

- Smart fallback to either:
  - **AUTO**: Text-based thumbnail
  - **BOOK**: Use book image (if downloaded)
  - **PERSON**: Use portrait image (e.g., Steve Jobs)
- All thumbnails are styled similarly to *Syllabus with Rohit*

---

## 🕒 Cron Job Setup (Linux/Mac)

To run `main.py` every 15 minutes:

```bash
crontab -e
*/15 * * * * /path/to/venv/bin/python /path/to/main.py
```

To suggest new topics daily:

```bash
0 6 * * * /path/to/venv/bin/python /path/to/suggest_topics.py
```

---

## 💰 Cost Breakdown (10-min video)

| Component        | Tool         | Cost Est. (INR) |
|------------------|--------------|-----------------|
| Script Gen       | GPT-4o Cached| ₹4–6            |
| Voice Gen        | ElevenLabs   | ₹10–15          |
| Image & Video    | Open-source  | ₹0              |
| Upload/Sheets    | Google API   | ₹0              |
| **Total**        |              | **₹15–20**      |

> Optional: Use free TTS tools to cut voice costs

## FULL PROJECT SETUP

📘 Full Setup Guide → [Click to view](./FULL_PROJECT_SETUP.md)


## 👨‍💻 Contributors
> Made with ❤️ for Indian creators. [Back to Zero YouTube](https://youtube.com/@backtozero9378)
> Connect Me at LinkedIn Jagdish Lade. [https://www.linkedin.com/in/jagdishlade/]
> Support and Follow my YT. [https://www.youtube.com/@JagdishLade]

## 📜 License

MIT — free to use, modify, and contribute.
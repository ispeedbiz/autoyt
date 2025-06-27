Back to Zero – Fully Autonomous Hindi Audiobook YouTube Channel

====================
DESCRIPTION
====================
This project auto-generates, voices, thumbnails, renders, and uploads engaging Hindi/Hinglish book summaries, biographies, and knowledge videos to YouTube – all from a Google Sheet!

You only enter topics and scheduling in the Google Sheet; AI does the rest.

====================
SETUP INSTRUCTIONS
====================

1. Clone/download this folder to your local computer (Mac/Linux recommended).
2. Create and activate a virtual environment:
   python3 -m venv venv
   source venv/bin/activate

3. Install requirements:
   pip install -r requirements.txt

4. Add your credentials and API keys:
   - Place your Google service_account.json here (with access to your Sheet).
   - Create a .env file in this folder with:
        OPENAI_API_KEY=sk-...
        ELEVENLABS_API_KEY=sk-...
        TELEGRAM_BOT_TOKEN=...
        TELEGRAM_CHAT_ID=...

5. Share your Google Sheet with your service account email (editor access).

====================
HOW TO RUN
====================

- To auto-generate 10 days of video ideas:
    python3 suggest_topics.py

- To run the main YouTube video posting pipeline (manually):
    python3 main.py

- To run automatically, set up a cron job:
    (every 10 min)
    */10 * * * * cd /Users/yourusername/backtozero_automation && /Users/yourusername/backtozero_automation/venv/bin/python3 main.py >> cronlog.txt 2>&1

====================
FILE STRUCTURE
====================
main.py               # Main pipeline
suggest_topics.py     # Topic suggestion/scheduling
utils.py              # Helper functions
service_account.json  # Google API credentials
.env                  # API keys
videos/               # All generated assets per video
cronlog.txt           # Automation logs

====================
GOOGLE SHEET STRUCTURE (KEY COLUMNS)
====================
Book/Topic | Language | Custom Title (optional) | Notes (optional) | Publish Date | Status | YouTube Link | Thumbnail Text | Style/Tone | Key Highlights | Target Audience | CTA | Duration | Thumbnail Source | Attribution Note

- Status codes: 🕓 Waiting | ⚙️ Processing | ✅ Posted | ❌ Error

====================
SUPPORT
====================
For help, contact: [your email/telegram]

====================
DISCLAIMER
====================
This channel uses AI-generated and public-domain content for educational use. Book summaries and visuals follow Indian copyright fair use policy (§52).

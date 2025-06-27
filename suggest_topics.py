from dotenv import load_dotenv
load_dotenv()

import os
import openai
import gspread
from openai import OpenAI
from datetime import datetime, timedelta
from google.oauth2.service_account import Credentials
from utils import load_env
env = load_env()


# CONFIG
SERVICE_ACCOUNT_FILE = "service_account.json"
SHEET_NAME = "Back to Zero – Input Sheet"
WORKSHEET_INDEX = 0
NUM_DAYS = 10
IDEAS_PER_DAY = 2
TOTAL_IDEAS = NUM_DAYS * IDEAS_PER_DAY
LANGUAGE = "Hindi"
MORNING_TIME = "09:00"
EVENING_TIME = "18:00"

# Load env
OPENAI_API_KEY = env.get("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# GPT-4o Enhanced Prompt for Top-Class Content Suggestions
prompt = f"""
You are an expert content strategist for a popular Hindi YouTube channel inspired by 'Syllabus with Rohit'.

📌 Objective:
Suggest 20 powerful and emotionally engaging video topics. Ensure each topic has mass appeal and strong potential to attract Hindi-speaking Indian audiences, especially young professionals, entrepreneurs, students, and lifelong learners.

📚 Content Mix:
Balance the topics across these themes:
- Inspiring Biographies (e.g., Steve Jobs, Elon Musk)
- Powerful Self-help Books (e.g., Atomic Habits, Rich Dad Poor Dad)
- Philosophy and Ancient Wisdom (e.g., Stoicism, Bhagavad Gita)
- Future-ready topics (e.g., AI, Technology, Finance, Productivity, Mindset)

💡 Instructions for each topic (write clearly in English):
Provide exactly:
1. Book/Topic (English title or person's name)
2. Custom Title in Hindi (catchy, emotional, curiosity-driven)
3. 2-line Summary in simple Hindi, sprinkle popular English words (mindset, success, growth, etc.) naturally.
4. 2–3 crisp Key Highlights (bullet points, each ≤10 words) clearly in Hindi-English mix.
5. Target Audience (e.g., Students, Professionals, Entrepreneurs, General)
6. Style/Tone (Motivational, Inspirational, Storytelling, Informative, Humorous)
7. Recommended Duration (Short: 1-min, Medium: 5-min, Long: 10-min)
8. Thumbnail Source Type (AUTO / BOOK / PERSON)

✅ Strict Output Formatting:
- Clearly separate each idea with ===
- Use this exact structure (English labels exactly as written):

Book/Topic: 
Custom Title: 
Summary: 
Key Highlights:
- Highlight 1
- Highlight 2
- Highlight 3 (optional)
Target Audience: 
Style/Tone: 
Duration: 
Thumbnail Source: 

✨ Example (for clarity):

Book/Topic: Atomic Habits
Custom Title: छोटी आदतें, बड़ा Impact
Summary: छोटे-छोटे habits से कैसे long-term success हासिल करें। Practical life tips.
Key Highlights:
- 1% daily improvement का नियम
- Habit-stacking technique
- Identity-based आदतें बनाएं
Target Audience: Students, Entrepreneurs
Style/Tone: Motivational
Duration: Medium
Thumbnail Source: BOOK

Remember:
- Use a natural blend of conversational Hindi and commonly-used English terms.
- Suggest only high-impact, audience-centric topics.
- Avoid repetition or overly common suggestions.

Begin now:
"""

resp = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a Hindi content expert for YouTube."},
        {"role": "user", "content": prompt}
    ],
    temperature=0.7,
    max_tokens=1800
)

raw = resp.choices[0].message.content.strip()
ideas = [i.strip() for i in raw.split("===") if i.strip()]
rows = []

for i, idea in enumerate(ideas):
    lines = idea.split("\n")
    d = { "Language": LANGUAGE }
    for line in lines:
        if ":" in line:
            key, val = line.split(":", 1)
            key = key.strip().lower()
            val = val.strip()
            if "book" in key: d["Book/Topic"] = val
            elif "title" in key: d["Custom Title (optional)"] = val
            elif "summary" in key: d["Notes (optional)"] = val
            elif "highlight" in key: d["Key Highlights"] = val
            elif "audience" in key: d["Target Audience"] = val
            elif "tone" in key or "style" in key: d["Style/Tone - E.g., Inspirational, Motivational, Storytelling, Informative, Humorous (used dynamically in prompts)"] = val
            elif "duration" in key: d["Duration - Desired length of video (Short: 1-min, Medium: 5-min, Long: 10-min)"] = val
            elif "thumbnail" in key: d["Thumbnail Source (AUTO / BOOK / PERSON / NONE)."] = val

    day_offset = i // IDEAS_PER_DAY
    publish_time = MORNING_TIME if i % 2 == 0 else EVENING_TIME
    publish_date = (datetime.now() + timedelta(days=day_offset)).strftime("%Y-%m-%d")
    d["Publish Date"] = f"{publish_date} {publish_time}"
    d["Status"] = "🕓 Waiting"
    d["Thumbnail Text Specific catchy text to display on thumbnail"] = d.get("Custom Title (optional)", d.get("Book/Topic", ""))
    d["CTA (Call-to-Action) - What you want viewers to do after watching (Subscribe, comment, share, visit website, etc.)"] = "Subscribe for more!"
    d["Attribution Note"] = ""
    rows.append(d)

# Connect to Google Sheet & Drive (needed to open by title)
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
creds = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=SCOPES
)
gc = gspread.authorize(creds)
ws = gc.open(SHEET_NAME).get_worksheet(WORKSHEET_INDEX)

header = ws.row_values(1)
for d in rows:
    row = [d.get(col, "") for col in header]
    ws.append_row(row, value_input_option="USER_ENTERED")

print(f"✅ {len(rows)} scheduled ideas added to Google Sheet.")
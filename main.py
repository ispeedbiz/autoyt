#!/usr/bin/env python3
# main.py — BackToZero fully-autonomous pipeline (scheduled publish)

import os, sys, time, subprocess, traceback, requests, io, textwrap, logging, pickle
from datetime import datetime
from pathlib import Path
import gspread
from openai import OpenAI
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from PIL import Image, ImageDraw, ImageFont
from utils import load_env, get_video_folder, save_text_to_file, log_to_file, sanitize_folder_name

# ───────────────────────────────────────────────────────── config ──
BASE_DIR            = Path(__file__).parent
VIDEOS_DIR          = BASE_DIR / "videos"
SERVICE_ACCOUNT_FILE = "service_account.json"
SHEET_NAME          = "Back to Zero – Input Sheet"
WORKSHEET_INDEX     = 0
CLIENT_SECRETS_FILE = BASE_DIR / "client_secret.json"
SUPPORTED_LANG      = {"Hindi"}
HINDI_VOICE_ID      = os.getenv("HINDI_VOICE_ID", "EXAVITQu4vr4xnSDxMaL")
FFMPEG_CMD          = "ffmpeg"
MAX_TTS_CHARS       = 5000  # ElevenLabs limit

def sheet_client():
    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES
    )
    return gspread.authorize(creds)

def sheet_ws():
    return sheet_client().open(SHEET_NAME).get_worksheet(WORKSHEET_INDEX)

def parse_publish_datetime(s):
    # Accepts both "YYYY-MM-DD" and "YYYY-MM-DD HH:MM"
    try:
        if len(s.strip()) == 10:
            s += " 00:00"
        return datetime.strptime(s, "%Y-%m-%d %H:%M")
    except:
        return None

def list_pending(ws):
    now = datetime.now()
    all_rows = ws.get_all_values()
    pending = []
    for idx, row in enumerate(all_rows[1:], start=2):
        status = (row[5] if len(row) > 5 else "").strip().lower()
        pub_dt = parse_publish_datetime(row[4] if len(row) > 4 else "")
        if status in ("", "🕓 waiting") and pub_dt and pub_dt <= now:
            pending.append((idx, row))
    return pending

# ───────────────────────────────────────────────────────── logging ─
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout),
              logging.FileHandler(BASE_DIR / "automation.log")]
)

# ──────────────────────────────────────────────── Sheet & scheduling ─
def parse_publish_datetime(s: str):
    s = s.strip()
    if not s:
        return None
    # allow "YYYY-MM-DD HH:MM" or "YYYY-MM-DD"
    if len(s) == 10:
        s += " 00:00"
    try:
        return datetime.strptime(s, "%Y-%m-%d %H:%M")
    except:
        return None

def list_pending(ws):
    all_rows = ws.get_all_values()
    pending = []
    now = datetime.now()
    for idx, row in enumerate(all_rows[1:], start=2):
        status = (row[5] if len(row) > 5 else "").strip().lower()
        pub_dt = parse_publish_datetime(row[4] if len(row) > 4 else "")
        if status in ("", "🕓 waiting") and pub_dt and pub_dt <= now:
            pending.append((idx, row))
    return pending

def batch_update(ws, row, status, link="", err="", proc_time=""):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ws.batch_update([{
        "range": f"F{row}:J{row}",
        "values": [[status, link, ts, err, proc_time]]
    }])

# ──────────────────────────────────────────────────── Data parsing ─
SUPPORTED_LANGUAGES = {"Hindi"}
def row_to_data(row):
    """Extract and validate all needed fields from a sheet row."""
    def g(i, default=""):
        return row[i].strip() if len(row) > i and row[i].strip() else default

    data = {
        "topic":      g(0),
        "lang":       g(1).capitalize(),
        "title":      g(2),
        "notes":      g(3),
        "pub_date":   g(4),
        "thumb_src":  g(16, "AUTO"),
        "thumb_txt":  g(10, g(2, g(0))),
        "tone":       g(11, "Informative"),
        "highlights": g(12, f"Top insights from “{g(0)}”"),
        "audience":   g(13, "General viewers"),
        "cta":        g(14, "Subscribe"),
        "duration":   g(15, "Medium (3–5 min)"),
        "attrib":     g(17, "")
    }
    if not data["topic"]:
        raise ValueError("Missing Book/Topic")
    if data["lang"] not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Unsupported language: {data['lang']}")
    if not data["title"]:
        data["title"] = data["topic"]
    return data

# ─────────────────────────────────────────────────── Prompt builder ─

def build_prompt(d):
    """
    Enhanced prompt for top-class, engaging YouTube narration in Hindi-English.
    """
    return textwrap.dedent(f"""
    तुम 'Syllabus with Rohit' जैसी engaging और impactful narration देने वाले narrator हो —
    लेकिन शैली तुम्हारी original होनी चाहिए: {d['tone']} और energetic.

    🔹 Primary language: हिंदी (पर English proper nouns और tech terms जैसे AI, Finance, Deep Work, Mindset use करो)  
    🔹 वीडियो की length: {d['duration']} (script ≤ 90 seconds)  
    🔹 Target audience: {d['audience']}  
    🔹 Topic: “{d['topic']}”

    —— INTERNAL SCRIPT STRUCTURE (NEVER mention these labels in narration) ——
    ① Hook: Bold question या striking statement से शुरू करो.  
    ② Context: 1-2 lines में बताओ कि यह topic आज क्यों जरूरी है.  
    ③ Takeaways: 3 strong insights (हर insight ≤ 20 words), इन highlights को naturally include करो: {d['highlights']}  
    ④ Story/Analogy: एक short, relatable example या Indian story (≤ 30 words).  
    ⑤ Reflective Question: एक insightful सवाल viewer से direct पूछो.  
    ⑥ CTA: Warm, natural Hindi-English mix में viewer को action लेने बोलो: “{d['cta']}”

    —— STYLE & DELIVERY RULES ——
    • Short sentences (max 15 words); हर 3-4 sentences बाद एक shorter punch-line.  
    • Viewer को direct address करो (“सोचिए”, “imagine कीजिए”, “आपके लिए”).  
    • Hindi conversational, पर common English words naturally रहने दो (“growth mindset”, “AI”, “Atomic Habits”).  
    • Active voice, vivid verbs और emotion-triggering words use करो.  
    • किसी भी type का fluff, clichés या uncertain fact बिल्कुल नहीं.  
    • Pause, tone variation और question-driven rhythm रखें ताकि script naturally human लगे.

    Extra Notes: {d['notes'] or "None"}

    🚫 Return सिर्फ final clean narration—plain text, बिना bullets, बिना labels, बिना quotes.
    """).strip()



# ──────────────────────────────────────────────── Script generation ─
def generate_script(prompt, env, folder):
    client = OpenAI(api_key=env["OPENAI_API_KEY"])
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role":"system","content":"You are a gifted Hindi storyteller like Syllabus with Rohit."},
            {"role":"user","content":prompt}
        ],
        max_tokens=600,
        temperature=0.55,
        user="backtozero_youtube"
    )
    text = resp.choices[0].message.content.strip()
    save_text_to_file(text, folder/"script.txt")
    return text

# ────────────────────────── Chunked TTS + stitch audio ─
def text_to_mp3(script, env, folder):
    voice_id = HINDI_VOICE_ID
    parts = [script[i:i+MAX_TTS_CHARS] for i in range(0, len(script), MAX_TTS_CHARS)]
    files = []
    for idx, part in enumerate(parts,1):
        r = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
            headers={"xi-api-key":env["ELEVENLABS_API_KEY"]}, json={"text":part, "voice_settings":{"stability":0.5,"similarity_boost":0.7}}
        )
        if r.status_code!=200:
            raise RuntimeError("TTS failed: "+r.text)
        p = folder/f"voice{idx}.mp3"
        p.write_bytes(r.content); files.append(p)
    if len(files)==1:
        out = folder/"output.mp3"; files[0].rename(out); return out
    # concat
    txt = folder/"concat.txt"
    txt.write_text("".join(f"file '{f.name}'\n" for f in files))
    out = folder/"output.mp3"
    subprocess.run([FFMPEG_CMD,"-y","-f","concat","-safe","0","-i",txt,"-c","copy",out], check=True)
    for f in files: f.unlink()
    txt.unlink()
    return out

# ─────────────────────────────────────────── Thumbnail with smart logic ─

def make_thumbnail(text, out_folder):
    width, height = 1280, 720
    bg_color = (20, 20, 20)
    text_color = (255, 153, 0)
    img = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype('/Library/Fonts/Arial.ttf', 80)
    except:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (width - text_width) / 2
    y = (height - text_height) / 2
    draw.text((x, y), text, font=font, fill=text_color)
    out_path = out_folder / "thumbnail.jpg"
    img.save(out_path)
    print(f"Thumbnail saved: {out_path}")
    return out_path


def smart_thumbnail(d, env, folder):
    # ... any advanced AI/logic you want ...
    # fallback:
    return make_thumbnail(d["thumb_txt"], folder)


# ───────────────────────────────────────── video creation ─
def make_video(thumbnail, audio, folder):
    out = folder/"final_video.mp4"
    cmd = [FFMPEG_CMD,"-y","-loop","1","-i",thumbnail,"-i",audio,
           "-c:v","libx264","-c:a","aac","-b:a","192k","-shortest",
           "-movflags","+faststart","-vf","scale=1280:720","-pix_fmt","yuv420p",out]
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return out

# ──────────────────────────────────────────── YouTube upload ─
def yt_upload(video, thumb, d):
    if not Path("token.pickle").exists():
        raise RuntimeError("token.pickle missing. Run once manually for OAuth.")
    creds = pickle.load(open("token.pickle","rb"))
    yt = build("youtube","v3",credentials=creds)
    # video
    desc = f"{d['topic']} का सारांश\n\nमुख्य बिंदु:\n- "+ "\n- ".join(textwrap.wrap(d['highlights'],40))
    if d.get("attrib"):
        desc += f"\n\nImage source: {d['attrib']}"
    body = {
        "snippet": {"title":d["title"], "description":desc, "tags":[sanitize_folder_name(d['topic']),d['lang'],d['tone']], "categoryId":"22"},
        "status" : {"privacyStatus":"public","selfDeclaredMadeForKids":False}
    }
    media = MediaFileUpload(str(video), resumable=True, mimetype="video/mp4")
    rq = yt.videos().insert(part=",".join(body.keys()), body=body, media_body=media)
    resp = None
    while not resp:
        status, resp = rq.next_chunk()
        if status: logging.info("Uploading %d%%",int(status.progress()*100))
    # thumbnail
    tm = MediaFileUpload(str(thumb), mimetype="image/jpeg")
    yt.thumbnails().set(videoId=resp["id"], media_body=tm).execute()
    return f"https://youtu.be/{resp['id']}"

# ────────────────────────────────────────────── Telegram alert ─
def telegram_alert(env, msg):
    if env.get("TELEGRAM_BOT_TOKEN") and env.get("TELEGRAM_CHAT_ID"):
        requests.get(f"https://api.telegram.org/bot{env['TELEGRAM_BOT_TOKEN']}/sendMessage",
                     params={"chat_id":env["TELEGRAM_CHAT_ID"],"text":msg})

# ───────────────────────────────────────────── process row ─
def process(idx, row, ws, env):
    start = time.time()
    try:
        data = row_to_data(row)
        # folder
        raw = get_video_folder(VIDEOS_DIR, data["topic"], data["pub_date"])
        folder = Path(raw); folder.mkdir(parents=True, exist_ok=True)
        # prompt → script
        prompt = build_prompt(data)
        save_text_to_file(prompt, folder/"final_prompt.txt")
        script = generate_script(prompt, env, folder)
        audio  = text_to_mp3(script, env, folder)
        thumb  = smart_thumbnail(data, env, folder)
        video  = make_video(thumb, audio, folder)
        link = yt_upload(video, thumb, data)
        proc_t = f"{int(time.time()-start)}s"
        # Only success if a valid link was returned
        if link and ("youtube.com/watch" in link or "youtu.be/" in link):
            batch_update(ws, idx, "✅ Posted", link, "", proc_t)
        else:
            batch_update(ws, idx, "❌ Error", "", "No valid YouTube link", proc_t)
    except Exception as e:
        proc_t = f"{int(time.time()-start)}s"
        batch_update(ws, idx, "❌ Error", "", str(e), proc_t)
        logging.error("Row %s failed:\n%s", idx, traceback.format_exc())


# ─────────────────────────────────────────────── main loop ─
if __name__ == "__main__":
    env = load_env()
    ws  = sheet_ws()  # you’ll need to define sheet_ws() exactly as before
    pending = list_pending(ws)
    logging.info("Found %d pending rows", len(pending))
    for idx, row in pending:
        batch_update(ws, idx, "⚙️ Processing")
        process(idx, row, ws, env)
    logging.info("✓ All pending rows processed.")

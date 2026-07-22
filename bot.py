"""
🎵 VIBE MUSIC BOT — Railway Ready Edition
GitHub → Railway Deploy | Environment Variables Support
"""

# ═══════════════════════════════════════════════════════════════
# 🔐 CONFIGURATION — Railway se variables lega ya default use karega
# ═══════════════════════════════════════════════════════════════

import os

# 👇 Railway pe Environment Variables se lega
# 👇 Local run karne ke liye default values daali hain
API_ID = int(os.getenv("API_ID", "39941105"))
API_HASH = os.getenv("API_HASH", "dda1c01cda8736941fb0718a748ec64c")
BOT_TOKEN = os.getenv("BOT_TOKEN", "8923356127:AAERWVP6hCWTBQZbdlGrzxTOCPX8GN5Yq3Q")

# ═══════════════════════════════════════════════════════════════
# 📦 IMPORTS
# ═══════════════════════════════════════════════════════════════

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped
from youtube_search import YoutubeSearch
import yt_dlp
import random
from datetime import timedelta

# ═══════════════════════════════════════════════════════════════
# 🎨 EMOJIS & STYLES
# ═══════════════════════════════════════════════════════════════

MUSIC_EMOJIS = ["🎵", "🎶", "🎼", "🎸", "🎹", "🎺", "🎻", "🥁", "🎤", "🎧"]

def e(category):
    emojis = {
        "play": ["▶️", "🚀", "💫"], "pause": ["⏸️", "😴"],
        "skip": ["⏭️", "🦘"], "stop": ["⏹️", "🛑"],
        "success": ["✅", "🎉", "✨"], "error": ["❌", "💔"],
        "loading": ["⏳", "🔄"], "cool": ["😎", "🔥", "💯"],
        "party": ["🎉", "🥳"], "info": ["ℹ️", "💡"],
    }
    return random.choice(emojis.get(category, ["✨"]))

def me():
    return random.choice(MUSIC_EMOJIS)

def banner(text):
    return f"{me()} **{text}** {me()}"

def divider():
    return "━━━━━━━━━━━━━━━━━━━━━━━"

def fmt_time(sec):
    return str(timedelta(seconds=sec))[2:7] if sec else "0:00"

# ═══════════════════════════════════════════════════════════════
# 🤖 BOT INIT
# ═══════════════════════════════════════════════════════════════

app = Client("vibe_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
call = PyTgCalls(app)

queues = {}
current = {}
loop_mode = {}

# ═══════════════════════════════════════════════════════════════
# 🎵 YOUTUBE FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def search_yt(query, max_results=5):
    try:
        return YoutubeSearch(query, max_results=max_results).to_dict()
    except:
        return []

def dl_audio(vid, title):
    try:
        url = f"https://youtube.com/watch?v={vid}"
        opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'downloads/{vid}.%(ext)s',
            'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
            'quiet': True, 'no_warnings': True,
        }
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            fn = ydl.prepare_filename(info)
            return {
                'file': fn.replace('.webm', '.mp3').replace('.m4a', '.mp3'),
                'title': info.get('title', title),
                'duration': info.get('duration', 0),
                'uploader': info.get('uploader', 'Unknown'),
                'views': info.get('view_count', 'N/A'),
                'url': url, 'vid': vid
            }
    except Exception as ex:
        print(f"DL Error: {ex}")
        return None

# ═══════════════════════════════════════════════════════════════
# 🎛️ KEYBOARDS
# ═══════════════════════════════════════════════════════════════

def controls():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⏸️ Pause", callback_data="pause"),
         InlineKeyboardButton("▶️ Resume", callback_data="resume"),
         InlineKeyboardButton("⏭️ Skip", callback_data="skip")],
        [InlineKeyboardButton("🔁 Loop", callback_data="loop"),
         InlineKeyboardButton("📋 Queue", callback_data="queue"),
         InlineKeyboardButton("⏹️ Stop", callback_data="stop")]
    ])

def search_kb(results):
    btns = []
    em = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]
    for i, r in enumerate(results[:5]):
        btns.append([InlineKeyboardButton(f"{em[i]} {r['title'][:35]}...", callback_data=f"pl_{r['id']}")])
    btns.append([InlineKeyboardButton("❌ Cancel", callback_data="cx")])
    return InlineKeyboardMarkup(btns)

# ═══════════════════════════════════════════════════════════════
# 🎬 PLAYBACK
# ═══════════════════════════════════════════════════════════════

async def play_next(cid, msg=None):
    if cid in queues and queues[cid]:
        song = queues[cid].pop(0)
        current[cid] = song
        try:
            await call.join_group_call(cid, AudioPiped(song['file']))
        except:
            await call.change_stream(cid, AudioPiped(song['file']))

        txt = f"""
{me()} {banner("NOW PLAYING")} {me()}

{divider()}
**{song['title']}**
{divider()}
⏱ `{fmt_time(song['duration'])}` | 👤 `{song['uploader']}`
👁 `{song['views']}` views
🔗 [YouTube]({song['url']})

{e("party")} Enjoy the vibes! {e("party")}
"""
        if msg:
            await msg.reply_text(txt, reply_markup=controls(), disable_web_page_preview=True)
        else:
            await app.send_message(cid, txt, reply_markup=controls(), disable_web_page_preview=True)
    else:
        current.pop(cid, None)
        await app.send_message(cid, f"{e('info')} **Queue finished!** Add more with `/play`")

# ═══════════════════════════════════════════════════════════════
# 📱 COMMANDS
# ═══════════════════════════════════════════════════════════════

@app.on_message(filters.command("start"))
async def start(client, msg):
    name = msg.from_user.first_name
    await msg.reply_text(f"""
{e("cool")} **Hey {name}!** {e("cool")}

{divider()}
🎵 **VIBE MUSIC BOT** 🎵
Your personal DJ for Voice Chats!
{divider()}

📌 **Commands:**
├ `/play <song>` — Play music
├ `/search <song>` — Search & pick
├ `/skip` — Next song
├ `/pause` — Pause
├ `/resume` — Resume
├ `/stop` — Stop & leave
├ `/queue` — View queue
├ `/loop` — Toggle loop
└ `/help` — Full help

{e("party")} **Let's party!** {e("party")}
""")

@app.on_message(filters.command("help"))
async def help_cmd(client, msg):
    await msg.reply_text(f"""
{e("info")} {banner("HELP")} {e("info")}

🎵 **Play:** `/play <song name>`
🔍 **Search:** `/search <song>` — Pick from 5 results
⏭️ **Skip:** `/skip`
⏸️ **Pause:** `/pause`
▶️ **Resume:** `/resume`
⏹️ **Stop:** `/stop`
📋 **Queue:** `/queue`
🔁 **Loop:** `/loop`

💡 Tip: Send YouTube link directly too!
""")

@app.on_message(filters.command("play"))
async def play_cmd(client, msg):
    cid = msg.chat.id
    if len(msg.command) < 2:
        return await msg.reply_text(f"{e('error')} **Usage:** `/play <song name>`")

    q = " ".join(msg.command[1:])
    sm = await msg.reply_text(f"{e('loading')} Searching `{q}`...")

    res = search_yt(q, 1)
    if not res:
        return await sm.edit_text(f"{e('error')} **Not found!**")

    r = res[0]
    await sm.edit_text(f"{e('loading')} **Found:** `{r['title'][:40]}`")
Downloading...")

    song = dl_audio(r['id'], r['title'])
    if not song:
        return await sm.edit_text(f"{e('error')} **Download failed!**")

    if cid not in queues:
        queues[cid] = []
    queues[cid].append(song)

    if cid not in current or not current.get(cid):
        await sm.delete()
        await play_next(cid, msg)
    else:
        await sm.edit_text(
            f"{e('success')} **Added!**

"
            f"{me()} `{song['title'][:50]}`
"
            f"📊 Position: `#{len(queues[cid])}`"
        )

@app.on_message(filters.command("search"))
async def search_cmd(client, msg):
    if len(msg.command) < 2:
        return await msg.reply_text(f"{e('error')} **Usage:** `/search <song>`")

    q = " ".join(msg.command[1:])
    sm = await msg.reply_text(f"{e('loading')} Searching...")

    res = search_yt(q, 5)
    if not res:
        return await sm.edit_text(f"{e('error')} **No results!**")

    txt = f"{e('search')} {banner('SEARCH RESULTS')} {e('search')}

"
    em = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]
    for i, r in enumerate(res):
        txt += f"{em[i]} **{r['title']}**
   ⏱ `{r.get('duration', '?')}`

"
    txt += f"{e('cool')} Click to play!"

    await sm.edit_text(txt, reply_markup=search_kb(res))

@app.on_message(filters.command("skip"))
async def skip_cmd(client, msg):
    cid = msg.chat.id
    if cid not in current or not current.get(cid):
        return await msg.reply_text(f"{e('error')} **Nothing playing!**")

    skipped = current[cid]['title']
    try:
        await call.change_stream(cid)
    except:
        pass
    await msg.reply_text(f"{e('skip')} **Skipped!**

⏭️ `{skipped[:50]}`")
    await play_next(cid)

@app.on_message(filters.command("pause"))
async def pause_cmd(client, msg):
    cid = msg.chat.id
    await call.pause(cid)
    await msg.reply_text(f"{e('pause')} **Paused!**

⏸️ `{current[cid]['title'][:50]}`")

@app.on_message(filters.command("resume"))
async def resume_cmd(client, msg):
    cid = msg.chat.id
    await call.resume(cid)
    await msg.reply_text(f"{e('play')} **Resumed!**

▶️ `{current[cid]['title'][:50]}`")

@app.on_message(filters.command("stop"))
async def stop_cmd(client, msg):
    cid = msg.chat.id
    queues[cid] = []
    current.pop(cid, None)
    try:
        await call.leave_group_call(cid)
    except:
        pass
    await msg.reply_text(f"{e('stop')} **Stopped!**

👋 See you! Use `/play` to start again.")

@app.on_message(filters.command("queue"))
async def queue_cmd(client, msg):
    cid = msg.chat.id
    if cid not in queues or not queues[cid]:
        return await msg.reply_text(f"{e('info')} **Queue empty!**")

    txt = f"{e('cool')} {banner('QUEUE')} {e('cool')}

"
    if cid in current and current.get(cid):
        txt += f"🎵 **Now:** `{current[cid]['title']}`

📋 **Next:**
"
    for i, s in enumerate(queues[cid][:10], 1):
        txt += f"`{i}.` {s['title'][:40]}
"
    await msg.reply_text(txt)

@app.on_message(filters.command("loop"))
async def loop_cmd(client, msg):
    cid = msg.chat.id
    loop_mode[cid] = not loop_mode.get(cid, False)
    st = "ON 🔁" if loop_mode[cid] else "OFF ❌"
    await msg.reply_text(f"{e('cool')} **Loop:** `{st}`")

# ═══════════════════════════════════════════════════════════════
# 🔘 CALLBACKS
# ═══════════════════════════════════════════════════════════════

@app.on_callback_query()
async def cb(client, cb):
    cid = cb.message.chat.id
    d = cb.data

    if d.startswith("pl_"):
        vid = d.replace("pl_", "")
        await cb.answer("🎵 Downloading...")
        song = dl_audio(vid, "Song")
        if not song:
            return await cb.answer("❌ Failed!", show_alert=True)

        if cid not in queues:
            queues[cid] = []
        queues[cid].append(song)

        if cid not in current or not current.get(cid):
            await play_next(cid)
        else:
            await cb.message.edit_text(
                f"{e('success')} **Added!** `{song['title'][:40]}`
Position: `#{len(queues[cid])}`"
            )
        return

    if d == "cx":
        await cb.message.edit_text(f"{e('info')} Cancelled!")
        return

    if d == "pause":
        await call.pause(cid)
        await cb.answer("⏸️ Paused!")
    elif d == "resume":
        await call.resume(cid)
        await cb.answer("▶️ Resumed!")
    elif d == "skip":
        try:
            await call.change_stream(cid)
        except:
            pass
        await cb.answer("⏭️ Skipped!")
        await play_next(cid)
    elif d == "stop":
        queues[cid] = []
        current.pop(cid, None)
        try:
            await call.leave_group_call(cid)
        except:
            pass
        await cb.answer("🛑 Stopped!")
        await cb.message.edit_text(f"{e('stop')} **Stopped!**")
    elif d == "loop":
        loop_mode[cid] = not loop_mode.get(cid, False)
        await cb.answer(f"Loop: {'ON' if loop_mode[cid] else 'OFF'}")
    elif d == "queue":
        if cid not in queues or not queues[cid]:
            await cb.answer("📭 Empty!", show_alert=True)
        else:
            txt = f"📋 Queue ({len(queues[cid])}):
"
            for i, s in enumerate(queues[cid][:5], 1):
                txt += f"{i}. {s['title'][:30]}
"
            await cb.answer(txt[:200], show_alert=True)

@call.on_stream_end()
async def on_end(client, upd):
    cid = upd.chat_id
    if loop_mode.get(cid, False) and cid in current:
        queues[cid].insert(0, current[cid])
    await play_next(cid)

# ═══════════════════════════════════════════════════════════════
# 🚀 RUN
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    os.makedirs("downloads", exist_ok=True)
    print("""
    ╔═══════════════════════════════════════╗
    ║     🎵 VIBE MUSIC BOT STARTING 🎵     ║
    ╚═══════════════════════════════════════╝
    """)
    app.run()

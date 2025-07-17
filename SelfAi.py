prompt = "" # Prompt (example: Your name is Natasha. You are the assistant of esfelurm. You are an expert in programming, hacking, and cybersecurity. esfelurm is your supervisor and rightful owner. Your answers must be highly accurate and delivered with a touch of humor.)
api_key = "" # Api Key Openai (https://openai.com)
session = "" # Name Session file (how make session file: https://github.com/Mr-Spect3r/TgAcc-Robber/blob/main/session.py)

from telethon import TelegramClient, events
from openai import OpenAI
import re, json, os
from datetime import datetime

client = TelegramClient(session, 123456, 'jbdfuivbniosjhiojwiohio123')
openai_client = OpenAI(api_key=api_key)

log_file_path = "ai_logs.txt"
keywords_file = "monitor_keywords.json"
ai_mode = "off"
me_user = None
blocked_users = set()
bold_enabled = False
monitor_keywords = []
del_msg_monitoring = False

def log(message: str):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(log_file_path, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} {message}\n")

async def save_to_saved_messages(text: str):
    try:
        await client.send_message("me", text)
    except Exception as e:
        log(f"❌ Failed to save to Saved Messages: {str(e)}")

def load_keywords():
    global monitor_keywords
    try:
        with open(keywords_file, "r", encoding="utf-8") as f:
            monitor_keywords = json.load(f)
    except:
        monitor_keywords = []

def save_keywords():
    try:
        with open(keywords_file, "w", encoding="utf-8") as f:
            json.dump(monitor_keywords, f)
    except Exception as e:
        log(f"Keyword save error: {str(e)}")

load_keywords()

@client.on(events.NewMessage(pattern=r'^/(\w+)( .+)?$'))
async def unified_command_handler(event):
    global ai_mode, bold_enabled, del_msg_monitoring

    full_text = event.raw_text.strip().lower()
    parts = full_text.split(maxsplit=1)
    cmd = parts[0]
    args = parts[1] if len(parts) > 1 else ""

    def reorder_command(cmd_text):
        if cmd_text.startswith('/ai') and ('on' in cmd_text or 'off' in cmd_text):
            core = cmd_text.replace('/ai', '').replace('on', '').replace('off', '')
            suffix = 'on' if 'on' in cmd_text else 'off'
            return f"/ai{core}{suffix}"
        elif cmd_text.startswith('/bold') or cmd_text.startswith('/delmg'):
            core = cmd_text.replace('on', '').replace('off', '')
            suffix = 'on' if 'on' in cmd_text else 'off'
            return f"{core}{suffix}"
        return cmd_text

    cmd = reorder_command(cmd)

    if cmd == "/aipvon":
        ai_mode = "pv"
        await safe_reply(event, "✅ AI mode: PV")
        log("AI mode set to PV")

    elif cmd == "/aigpon":
        ai_mode = "gp"
        await safe_reply(event, "✅ AI mode: Group Replies")
        log("AI mode set to Group")

    elif cmd == "/aitagon":
        ai_mode = "tag"
        await safe_reply(event, "✅ AI mode: Tag")
        log("AI mode set to Tag")

    elif cmd == "/aioff":
        ai_mode = "off"
        await safe_reply(event, "🛑 AI disabled")
        log("AI disabled")

    elif cmd == "/boldon":
        bold_enabled = True
        await safe_reply(event, "🔤 Bold mode is ON")

    elif cmd == "/boldoff":
        bold_enabled = False
        await safe_reply(event, "🔤 Bold mode is OFF")

    elif cmd == "/delmgon":
        del_msg_monitoring = True
        await safe_reply(event, "🗑️ Message delete monitoring ON")

    elif cmd == "/delmgoff":
        del_msg_monitoring = False
        await safe_reply(event, "🗑️ Message delete monitoring OFF")

    elif cmd == "/log":
        if os.path.exists(log_file_path):
            try:
                await client.send_file("me", log_file_path, caption="📄 AI Log File")
            except Exception as e:
                await safe_reply(event, "❌ Failed to send log file.")
                log(f"Log file send error: {str(e)}")
        else:
            await safe_reply(event, "⚠️ No log file found.")

    elif cmd.startswith("/block"):
        target = args.strip()
        if target.startswith("@"):
            username = target[1:]
            blocked_users.add(username.lower())
            await safe_reply(event, f"🚫 Blocked username: @{username}")
            log(f"Blocked username @{username}")
        else:
            try:
                user_id = int(target)
                blocked_users.add(user_id)
                await safe_reply(event, f"🚫 Blocked user ID: {user_id}")
                log(f"Blocked user ID {user_id}")
            except:
                await safe_reply(event, "⚠️ Usage: /block [@username or user_id]")

    elif cmd.startswith("/unblock"):
        target = args.strip()
        if target.startswith("@"):
            username = target[1:]
            if username.lower() in blocked_users:
                blocked_users.remove(username.lower())
                await safe_reply(event, f"✅ Unblocked username: @{username}")
                log(f"Unblocked username @{username}")
            else:
                await safe_reply(event, "ℹ️ Username not blocked.")
        else:
            try:
                user_id = int(target)
                if user_id in blocked_users:
                    blocked_users.remove(user_id)
                    await safe_reply(event, f"✅ Unblocked user ID: {user_id}")
                    log(f"Unblocked user ID {user_id}")
                else:
                    await safe_reply(event, "ℹ️ User ID not blocked.")
            except:
                await safe_reply(event, "⚠️ Usage: /unblock [@username or user_id]")

    elif cmd.startswith("/addmon"):
        keyword = args.strip().lower()
        if keyword and keyword not in monitor_keywords:
            monitor_keywords.append(keyword)
            save_keywords()
            await safe_reply(event, f"✅ Keyword added: {keyword}")
        else:
            await safe_reply(event, "⚠️ Invalid or duplicate keyword.")

    elif cmd.startswith("/remmon"):
        keyword = args.strip().lower()
        if keyword in monitor_keywords:
            monitor_keywords.remove(keyword)
            save_keywords()
            await safe_reply(event, f"🗑️ Keyword removed: {keyword}")
        else:
            await safe_reply(event, "⚠️ Keyword not found.")

    elif cmd == "/monlist":
        if monitor_keywords:
            await safe_reply(event, "🔍 Monitored keywords:\n" + "\n".join(monitor_keywords))
        else:
            await safe_reply(event, "📭 No monitored keywords.")

    elif cmd == "/help":
        help_text = """
🤖 **AI Self-Bot Help**

/AiPvOn - Enable AI in private chats  
/AiGpOn - Enable AI in groups (replies only)  
/AiTagOn - Enable AI when mentioned in groups  
/AiOff - Disable AI  
/BoldOn - Enable bold formatting  
/BoldOff - Disable bold formatting  
/DelMgOn - Enable delete message monitoring  
/DelMgOff - Disable it  
/Block [@username or ID] - Block a user  
/Unblock [@username or ID] - Unblock a user  
/AddMon [word] - Add monitored keyword  
/RemMon [word] - Remove keyword  
/MonList - Show monitored keywords  
/Log - Send log file  
/Help - Show this help  
"""
        await safe_reply(event, help_text)

@client.on(events.NewMessage())
async def handle_incoming(event):
    global me_user
    try:
        sender_id = event.sender_id
        sender = await event.get_sender()

        if getattr(sender, 'bot', False) or (sender.username and sender.username.lower().endswith("bot")):
            log(f"🤖 Ignored bot message from: @{getattr(sender, 'username', 'unknown')}")
            return

        if sender_id in blocked_users or (sender.username and sender.username.lower() in blocked_users):
            log(f"⛔ Blocked sender ignored: {sender_id} / @{getattr(sender, 'username', 'unknown')}")
            return

        if me_user is None:
            me_user = await client.get_me()

        if bold_enabled and event.out:
            try:
                await event.edit(f"**{event.text}**")
            except Exception as e:
                log(f"Bold edit error: {str(e)}")

        if ai_mode == "pv" and event.is_private and not event.out:
            await reply_with_ai(event, event.text)

        elif ai_mode == "gp" and event.is_group and event.is_reply:
            msg = await event.get_reply_message()
            if msg and msg.sender_id == me_user.id:
                await reply_with_ai(event, event.text)

        elif ai_mode == "tag" and event.is_group and not event.out:
            if me_user.username:
                pattern = re.compile(rf"@{me_user.username}(?:\s+|$)(.*)", re.IGNORECASE)
                match = pattern.match(event.raw_text.strip())
                if match:
                    query = match.group(1).strip()
                    await reply_with_ai(event, query if query else "👋 I'm here!")

        for word in monitor_keywords:
            if word.lower() in event.raw_text.lower():
                await save_to_saved_messages(f"🔔 Keyword triggered: '{word}'\nUser: {sender_id}\nText: {event.raw_text}")

    except Exception as e:
        log(f"Error in handle_incoming: {str(e)}")

@client.on(events.MessageDeleted())
async def deleted_msg_handler(event):
    if del_msg_monitoring:
        for msg_id in event.deleted_ids:
            log_msg = f"🗑️ A message was deleted in chat {event.chat_id}"
            await save_to_saved_messages(log_msg)

async def reply_with_ai(event, msg_text):
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "system",
                "content": f"{prompt}\nAnswer the question inside the parentheses only: ({msg_text})"
            }]
        )
        answer = response.choices[0].message.content
        log(f"AI Reply: {answer}")
        await safe_reply(event, answer)
    except Exception as e:
        log(f"OpenAI error: {str(e)}")
        await safe_reply(event, "⚠️ AI error occurred.")

async def safe_reply(event, text):
    try:
        await event.reply(text)
    except Exception as e:
        log(f"Reply error: {str(e)}")

print("AI Self-Bot is running...")
client.start()
client.run_until_disconnected()
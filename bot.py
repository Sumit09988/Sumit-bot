import requests
import time
import json

BOT_TOKEN = "8617423223:AAHUcMIDMWXVN0rpiWECM1v-3JucJzObiQs"
API_URL = "https://usersxinfo-adminn.vercel.app/get_data?key=demo&mobile="
CHANNEL = "@SUMITDARKOSINT"
ADMIN_ID = 7515864015

OFFSET = 0

# ---------------- STORAGE ----------------
try:
    with open("users.json") as f:
        users = set(json.load(f))
except:
    users = set()

try:
    with open("banned.json") as f:
        banned = set(json.load(f))
except:
    banned = set()

def save():
    json.dump(list(users), open("users.json", "w"))
    json.dump(list(banned), open("banned.json", "w"))

# ---------------- SEND ----------------
def send_message(chat_id, text, keyboard=None):
    footer = "\n━━━━━━━━━━━━━━\n👨‍💻 Developer: @T4HKR"

    data = {
        "chat_id": chat_id,
        "text": text + footer,
        "parse_mode": "Markdown",
        "reply_markup": json.dumps(keyboard) if keyboard else None
    }

    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data=data)

# ---------------- BUTTONS ----------------
def main_menu():
    return {
        "keyboard": [
            [{"text": "📱 Number Search"}],
            [{"text": "📊 Bot Stats"}, {"text": "👨‍💻 Developer"}],
            [{"text": "ℹ️ Help"}]
        ],
        "resize_keyboard": True
    }

# ---------------- JOIN CHECK ----------------
def check_join(user_id):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMember?chat_id={CHANNEL}&user_id={user_id}"
    res = requests.get(url).json()
    return res.get("result", {}).get("status") in ["member", "administrator", "creator"]

# ---------------- FETCH ----------------
def fetch(number):
    try:
        return json.dumps(requests.get(API_URL + number).json())
    except:
        return None

# ---------------- FORMAT RESULT ----------------
def format_result(data):
    try:
        d = json.loads(data)
        msg = "📱 RESULT FOUND ✅\n━━━━━━━━━━━━━━\n\n"

        for key, value in d.items():
            msg += f"🔹 {key.upper()}:\n`{value}`\n\n"

        return msg
    except:
        return "❌ Error formatting result"

# ---------------- LOOP ----------------
while True:
    res = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset={OFFSET}").json()

    if "result" in res:
        for upd in res["result"]:
            OFFSET = upd["update_id"] + 1

            if "message" not in upd:
                continue

            msg = upd["message"]
            chat_id = msg["chat"]["id"]
            user_id = msg["from"]["id"]
            text = msg.get("text", "")

            users.add(user_id)
            save()

            # banned check
            if user_id in banned:
                continue

            # force join
            if not check_join(user_id):
                send_message(chat_id, "⚠️ पहले channel join करो\n👉 @SUMITDARKOSINT")
                continue

            # ---------------- MENU ----------------
            if text == "/start":
                send_message(
                    chat_id,
                    "👋 Welcome to OSINT Bot 🔍\n\n🚀 Fast Number Lookup Service",
                    main_menu()
                )

            elif text == "📱 Number Search":
                send_message(chat_id, "📲 Send any mobile number (10 digits)")

            elif text == "📊 Bot Stats" and user_id == ADMIN_ID:
                send_message(chat_id, f"📊 Total Users: {len(users)}")

            elif text == "👨‍💻 Developer":
                send_message(chat_id, "👨‍💻 Developer: @T4HKR\n🚀 Premium Bot Service")

            elif text == "ℹ️ Help":
                send_message(
                    chat_id,
                    "ℹ️ HOW TO USE:\n\n"
                    "1️⃣ Click 📱 Number Search\n"
                    "2️⃣ Send 10 digit number\n"
                    "3️⃣ Get instant result ⚡"
                )

            # ---------------- ADMIN ----------------
            elif text.startswith("/ban") and user_id == ADMIN_ID:
                try:
                    uid = int(text.split()[1])
                    banned.add(uid)
                    save()
                    send_message(chat_id, f"🚫 Banned: {uid}")
                except:
                    send_message(chat_id, "❌ Usage: /ban user_id")

            elif text.startswith("/unban") and user_id == ADMIN_ID:
                try:
                    uid = int(text.split()[1])
                    banned.discard(uid)
                    save()
                    send_message(chat_id, f"✅ Unbanned: {uid}")
                except:
                    send_message(chat_id, "❌ Usage: /unban user_id")

            elif text.startswith("/broadcast") and user_id == ADMIN_ID:
                msg_text = text.replace("/broadcast ", "")
                for u in users:
                    try:
                        send_message(u, f"📢 {msg_text}")
                    except:
                        pass
                send_message(chat_id, "✅ Broadcast Sent")

            # ---------------- NUMBER ----------------
            elif text.isdigit() and len(text) == 10:
                send_message(chat_id, "🔍 Fetching Data... ⏳")

                raw = fetch(text)

                if raw:
                    formatted = format_result(raw)
                    send_message(chat_id, formatted)
                else:
                    send_message(chat_id, "❌ Data fetch failed")

            else:
                send_message(chat_id, "⚠️ Send valid number (10 digits)")

    time.sleep(2)

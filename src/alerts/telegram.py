import os
import urllib.parse
import urllib.request


def send_telegram_alert(message: str) -> dict:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("Telegram token/chat_id not configured. Skipping alert.")
        return {"ok": False, "reason": "missing_config"}

    data = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": message
    }).encode()

    url = "https" + "://" + "api.telegram.org/bot" + token + "/sendMessage"

    with urllib.request.urlopen(url, data=data, timeout=20) as response:
        body = response.read().decode()

    print(body)
    return {"ok": True, "response": body}

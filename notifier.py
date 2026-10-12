import os, requests

class TelegramNotifier:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
    def send_text(self, text):
        if not self.token or not self.chat_id:
            raise RuntimeError("Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env")
        r = requests.post(f"https://api.telegram.org/bot{self.token}/sendMessage",
                          json={"chat_id": self.chat_id, "text": text[:3900]},
                          timeout=30)
        r.raise_for_status()
        if not r.json().get("ok"):
            raise RuntimeError(f"Telegram API error: {r.text}")
    def send(self, item, config):
        prefix = config.get("telegram", {}).get("message_prefix", "🔔 Reddit Keyword Alert")
        self.send_text(f"{prefix}\n\n{item['subject']}\n{item['date']}\n\n{item['body'] or item['text']}")

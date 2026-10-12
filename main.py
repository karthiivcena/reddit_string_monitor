import argparse, logging, time
from dotenv import load_dotenv
from config_loader import load_config
from logger_setup import setup_logging
from email_reader import EmailAlertReader
from database import AlertDatabase
from notifier import TelegramNotifier
from filters import should_forward

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--config", default="config.json")
    p.add_argument("--once", action="store_true")
    p.add_argument("--test-telegram", action="store_true")
    args = p.parse_args()
    load_dotenv()
    cfg = load_config(args.config)
    setup_logging(cfg["application"].get("log_level", "INFO"), cfg["paths"]["log_file"])
    log = logging.getLogger("reddit_bridge")
    db = AlertDatabase(cfg["database"]["path"])
    tg = TelegramNotifier()
    if args.test_telegram:
        tg.send_text("Reddit Free Alert Bridge test: Telegram is configured.")
        print("Test message sent.")
        return
    reader = EmailAlertReader(cfg)
    interval = max(30, int(cfg["email_reader"]["poll_interval_seconds"]))
    while True:
        try:
            for item in reader.fetch_messages():
                if not should_forward(item, cfg):
                    reader.mark_seen(item["seq"])
                    continue
                if db.was_sent(item["message_key"]):
                    reader.mark_seen(item["seq"])
                    continue
                db.record_pending(item)
                try:
                    tg.send(item, cfg)
                    db.mark_sent(item["message_key"])
                    reader.mark_seen(item["seq"])
                    log.info("Forwarded alert: %s", item["subject"])
                except Exception:
                    log.exception("Telegram delivery failed; email will remain unread for retry.")
        except KeyboardInterrupt:
            break
        except Exception:
            log.exception("Email polling failed; retrying next cycle.")
        if args.once:
            break
        time.sleep(interval)

if __name__ == "__main__":
    main()

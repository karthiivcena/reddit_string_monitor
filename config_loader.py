import json
from pathlib import Path

def load_config(path="config.json"):
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"Config file not found: {p}")
    c = json.loads(p.read_text(encoding="utf-8"))
    for k in ("application", "paths", "email_reader", "filters", "telegram", "database"):
        if k not in c:
            raise ValueError(f"Missing config section: {k}")
    if int(c["email_reader"].get("poll_interval_seconds", 60)) < 30:
        raise ValueError("poll_interval_seconds must be at least 30")
    return c

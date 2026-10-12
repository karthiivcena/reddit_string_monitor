import logging
from pathlib import Path

def setup_logging(level="INFO", log_file="logs/bridge.log"):
    p = Path(log_file)
    p.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(level=getattr(logging, str(level).upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[logging.StreamHandler(), logging.FileHandler(p, encoding="utf-8")], force=True)

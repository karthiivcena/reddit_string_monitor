import email, imaplib, logging, os
from email.header import decode_header, make_header
from email.message import Message
from bs4 import BeautifulSoup

class EmailAlertReader:
    """Reads unread alert emails; does not connect to Reddit."""
    def __init__(self, config):
        self.config = config
        self.log = logging.getLogger("reddit_bridge.email")
        self.host = os.getenv("IMAP_HOST", "imap.gmail.com")
        self.port = int(os.getenv("IMAP_PORT", "993"))
        self.username = os.getenv("IMAP_USERNAME")
        self.password = os.getenv("IMAP_PASSWORD")
        self.mailbox = os.getenv("IMAP_MAILBOX", "INBOX")
        if not self.username or not self.password:
            raise RuntimeError("Set IMAP_USERNAME and IMAP_PASSWORD in .env")

    def fetch_messages(self):
        out = []
        sender = self.config["email_reader"].get("sender_contains", "f5bot.com")
        max_batch = int(self.config["email_reader"].get("max_emails_per_cycle", 50))
        with imaplib.IMAP4_SSL(self.host, self.port) as m:
            m.login(self.username, self.password)
            status, _ = m.select(self.mailbox)
            if status != "OK":
                raise RuntimeError(f"Could not open mailbox {self.mailbox}")
            status, data = m.search(None, "UNSEEN", "FROM", f'"{sender}"')
            if status != "OK":
                raise RuntimeError("IMAP search failed")
            for seq in data[0].split()[-max_batch:]:
                status, rows = m.fetch(seq, "(BODY.PEEK[])")
                if status != "OK" or not rows or not isinstance(rows[0], tuple):
                    continue
                msg = email.message_from_bytes(rows[0][1])
                subject = self._decode(msg.get("Subject", "Reddit alert"))
                from_ = self._decode(msg.get("From", ""))
                body = self._body(msg)
                seq_s = seq.decode()
                key = (msg.get("Message-ID") or f"{from_}|{subject}|{msg.get('Date','')}").strip()
                out.append({"seq": seq_s, "message_key": key, "subject": subject,
                            "sender": from_, "body": body, "date": msg.get("Date", ""),
                            "text": subject + "\n\n" + body})
        return out

    def mark_seen(self, seq):
        with imaplib.IMAP4_SSL(self.host, self.port) as m:
            m.login(self.username, self.password)
            m.select(self.mailbox)
            status, _ = m.store(seq.encode(), "+FLAGS", "\\Seen")
            if status != "OK":
                self.log.warning("Could not mark message as read: %s", seq)

    @staticmethod
    def _decode(value):
        try:
            return str(make_header(decode_header(value)))
        except Exception:
            return value or ""

    @staticmethod
    def _body(msg: Message):
        plain, html = [], []
        parts = msg.walk() if msg.is_multipart() else [msg]
        for part in parts:
            if part.get_content_maintype() == "multipart":
                continue
            payload = part.get_payload(decode=True)
            if payload is None:
                continue
            charset = part.get_content_charset() or "utf-8"
            try:
                text = payload.decode(charset, errors="replace")
            except LookupError:
                text = payload.decode("utf-8", errors="replace")
            if part.get_content_type() == "text/plain":
                plain.append(text)
            elif part.get_content_type() == "text/html":
                html.append(text)
        if plain:
            return "\n".join(plain).strip()
        if html:
            return BeautifulSoup("\n".join(html), "html.parser").get_text("\n", strip=True)
        return ""

# Reddit Free Alert Bridge: F5Bot email → Telegram

This project requires no Reddit API credentials. F5Bot detects keyword matches in Reddit posts and comments and emails alerts. This Python bridge reads those emails over IMAP, stores message IDs in SQLite, and forwards alerts to Telegram.

## Honest limitations
- F5Bot says it monitors Reddit posts and comments every few minutes: https://f5bot.com/faq
- Free use has limits on keyword count, common terms, alert volume, and delivery delay. Check current limits at https://f5bot.com/ and https://f5bot.com/faq.
- Configure keywords and subreddit flags on the F5Bot website, not in this project's JSON.
- This bridge does not independently search Reddit. It forwards only emails F5Bot sends.
- F5Bot's API/webhook integration is for eligible paid plans; this project uses email/IMAP instead.
- No third-party service can guarantee every match is detected.

## A. Configure F5Bot
1. Create a free account at https://f5bot.com/.
2. Add your keywords in its dashboard.
3. For all Reddit, don't add `only-subreddit` filters.
4. For selected subreddits, use F5Bot's `only-subreddit=subreddit1,subreddit2` flag. Its documentation warns that `only-` flags are ORed; don't combine `only-reddit` with `only-subreddit`.
5. Ensure alert emails arrive in the inbox used below. Confirm the actual sender address and change `sender_contains` in `config.json` if needed.

## B. Telegram
1. Message @BotFather in Telegram and run `/newbot`.
2. Copy the bot token into `.env`.
3. Open the new bot and press Start.
4. Send a message to the bot, then visit `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates` to find your chat ID. Keep the token private.
5. Put the chat ID in `.env`.

## C. Gmail / IMAP
Use Gmail IMAP settings and a Google App Password where required; don't use your normal Google password. Other providers require their own IMAP host/port. Consider a dedicated inbox for alerts.

## D. Install on Ubuntu / WSL
```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
chmod 600 .env
```
Edit `.env` and `config.json`.

## E. Test and run
```bash
python -m unittest discover -s tests -v
python main.py --test-telegram
python main.py --once
python main.py
```
`--test-telegram` sends a test message. `--once` reads one batch. Normal mode polls continuously. Failed Telegram sends remain unread so the bridge can retry.

## Configuration
- `email_reader.poll_interval_seconds`: inbox polling frequency.
- `email_reader.sender_contains`: sender substring/domain to accept.
- `filters.include_text` / `filters.exclude_text`: optional local filtering of email content.
- `database.path`: SQLite file.
- Telegram prefix and log file are configurable.

## Security
Never commit `.env`. This program reads alert email content and sends it to the Telegram chat configured by you.

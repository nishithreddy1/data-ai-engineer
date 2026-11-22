"""Send alerts.txt to Slack / email. Dry-run by default.

    python src/alert.py            # prints what WOULD be sent
    SLACK_WEBHOOK_URL=... python src/alert.py --send

Set the webhook via environment variable only — never hard-code secrets.
For email, wire `send_email()` to your SMTP/SES settings.
"""
import os
import sys
import urllib.request
import json

def main():
    with open("outputs/alerts.txt") as f:
        text = f.read().strip()
    if text == "No anomalies today.":
        print("Nothing to send."); return
    if "--send" not in sys.argv:
        print("[dry-run] Would send:\n" + text); return
    url = os.environ.get("SLACK_WEBHOOK_URL")
    if not url:
        raise SystemExit("Set SLACK_WEBHOOK_URL env var to send.")
    req = urllib.request.Request(url, data=json.dumps({"text": text}).encode(),
                                 headers={"Content-Type": "application/json"})
    urllib.request.urlopen(req, timeout=10)
    print("Sent to Slack.")

if __name__ == "__main__":
    main()

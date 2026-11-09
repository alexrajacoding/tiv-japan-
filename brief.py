import argparse
import os
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import urlencode, urlsplit
from xml.etree import ElementTree

import requests
import yfinance as yf

JST = timezone(timedelta(hours=9))
MARKETS = (
    ("Emas (futures GC=F, acuan XAUUSD)", "GC=F"),
    ("Nasdaq-100 (futures NQ=F)", "NQ=F"),
)

def quote(label, symbol):
    try:
        bars = yf.Ticker(symbol).history(period="5d", interval="60m", timeout=10)
        closes = bars["Close"].dropna()
        latest = closes.iloc[-1]
        stamp = closes.index[-1].astimezone(JST)
        earlier = closes[closes.index <= closes.index[-1] - timedelta(hours=12)]
        change = f" | {latest / earlier.iloc[-1] - 1:+.2%} vs bar sebelumnya (≥12 jam)" if len(earlier) else ""
        return f"• {label}: {latest:,.2f}{change} | bar {stamp:%d/%m %H:%M} JST"
    except Exception:
        return f"• {label}: data tidak tersedia."

def headlines(now):
    query = urlencode({"q": "global economy Fed OR inflation OR oil when:1d",
                       "hl": "en-US", "gl": "US", "ceid": "US:en"})
    try:
        response = requests.get("https://news.google.com/rss/search?" + query, timeout=15)
        response.raise_for_status()
        items = ElementTree.fromstring(response.content).findall("./channel/item")
    except (requests.RequestException, ElementTree.ParseError):
        return ["• Feed berita tidak tersedia."]
    lines, seen = [], set()
    for item in items:
        try:
            stamp = parsedate_to_datetime(item.findtext("pubDate", "")).astimezone(JST)
        except (TypeError, ValueError):
            continue
        title = " ".join(item.findtext("title", "").split())
        link = item.findtext("link", "")
        if not title or title.casefold() in seen or not link.startswith("https://news.google.com/"):
            continue
        if not now - timedelta(hours=12) <= stamp <= now:
            continue
        line = f"• {title[:175]} ({stamp:%H:%M} JST) <{link}>"
        if len(line) > 520:
            continue
        lines.append(line)
        seen.add(title.casefold())
        if len(lines) == 3:
            break
    return lines or ["• Tidak ada headline yang lolos filter 12 jam terakhir."]

def send(message):
    url = os.environ.get("DISCORD_WEBHOOK_URL", "")
    parsed = urlsplit(url)
    if parsed.scheme != "https" or parsed.netloc != "discord.com" or not parsed.path.startswith("/api/webhooks/"):
        raise SystemExit("Atur secret DISCORD_WEBHOOK_URL.")
    try:
        response = requests.post(url, params={"wait": "true"},
                                 json={"content": message, "allowed_mentions": {"parse": []}},
                                 timeout=20, allow_redirects=False)
    except requests.RequestException:
        raise SystemExit("Koneksi Discord gagal. Cek channel sebelum mengulang.") from None
    if response.status_code != 200:
        raise SystemExit(f"Discord menolak kiriman (HTTP {response.status_code}).")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--send", action="store_true")
    args = parser.parse_args()
    now = datetime.now(JST)
    lines = [f"**TIC JAPAN | Market Brief · {now:%d/%m/%Y %H:%M} JST**",
             "**Pasar · Yahoo Finance**", *(quote(*market) for market in MARKETS),
             "Harga mengikuti bar terakhir yang tersedia dan dapat tertunda saat pasar tutup.",
             "**Ekonomi global · headline 12 jam terakhir**"]
    for line in headlines(now):
        if len("\n".join([*lines, line]).encode("utf-16-le")) // 2 <= 2000:
            lines.append(line)
    message = "\n".join(lines)
    if args.send:
        send(message)
        print("Discord menerima kiriman.")
    else:
        print(message)

if __name__ == "__main__":
    main()

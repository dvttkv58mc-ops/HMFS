# sources.py – jede Datenquelle genau eine Funktion.
# Bricht eine Quelle weg, tauschst du nur die eine Funktion aus.

import os
import datetime as dt
import xml.etree.ElementTree as ET

import requests
import yfinance as yf

FINNHUB_KEY = os.environ.get("FINNHUB_KEY", "")
MARKETAUX_KEY = os.environ.get("MARKETAUX_KEY", "")

# Die SEC verlangt einen User-Agent mit Kontakt. Trag deine Mail ein.
UA = {"User-Agent": "HMFS/1.0 (deine.mail@example.com)"}


def quotes(symbols):
    """Letzter Schlusskurs + Tagesveraenderung. Quelle: yfinance, kein Key."""
    out = []
    data = yf.Tickers(" ".join(symbols))
    for sym in symbols:
        try:
            h = data.tickers[sym].history(period="7d", interval="1d", auto_adjust=False)
            closes = h["Close"].dropna()
            if len(closes) < 2:
                print("  ! zu wenig Daten:", sym)
                continue
            last, prev = float(closes.iloc[-1]), float(closes.iloc[-2])
            out.append({
                "symbol": sym,
                "price": round(last, 2),
                "change_pct": round((last / prev - 1) * 100, 2),
            })
        except Exception as e:
            print("  ! Fehler bei", sym, "->", e)
    return out


def news(symbols, want):
    """Finanznachrichten mit Ticker-Zuordnung. Quelle: Marketaux.
    Free-Tier liefert 3 Artikel pro Request, deshalb blaettern wir."""
    if not MARKETAUX_KEY:
        print("  ! kein MARKETAUX_KEY gesetzt")
        return []
    items, page, seen = [], 1, set()
    while len(items) < want and page <= 8:
        try:
            r = requests.get(
                "https://api.marketaux.com/v1/news/all",
                timeout=25,
                params={
                    "api_token": MARKETAUX_KEY,
                    "symbols": ",".join(symbols[:50]),
                    "filter_entities": "true",
                    "language": "en,de",
                    "limit": 3,
                    "page": page,
                },
            )
            r.raise_for_status()
            batch = r.json().get("data", [])
        except Exception as e:
            print("  ! Marketaux:", e)
            break
        if not batch:
            break
        for a in batch:
            if a.get("url") in seen:
                continue
            seen.add(a.get("url"))
            tickers = [e.get("symbol") for e in a.get("entities", []) if e.get("symbol")]
            items.append({
                "title": a.get("title", ""),
                "url": a.get("url", ""),
                "source": a.get("source", ""),
                "published": (a.get("published_at") or "")[:16].replace("T", " "),
                "tickers": sorted(set(tickers))[:4],
            })
        page += 1
    return items[:want]


def earnings(days_ahead):
    """Earnings-Termine. Quelle: Finnhub (Free-Tier: US, ca. 1 Monat)."""
    if not FINNHUB_KEY:
        print("  ! kein FINNHUB_KEY gesetzt")
        return []
    today = dt.date.today()
    try:
        r = requests.get(
            "https://finnhub.io/api/v1/calendar/earnings",
            timeout=25,
            params={
                "from": today.isoformat(),
                "to": (today + dt.timedelta(days=days_ahead)).isoformat(),
                "token": FINNHUB_KEY,
            },
        )
        r.raise_for_status()
        rows = r.json().get("earningsCalendar", [])
    except Exception as e:
        print("  ! Finnhub:", e)
        return []
    rows.sort(key=lambda x: (x.get("date") or "", x.get("symbol") or ""))
    return [{
        "date": x.get("date"),
        "symbol": x.get("symbol"),
        "hour": {"bmo": "vor Eroeffnung", "amc": "nach Schluss"}.get(x.get("hour"), "offen"),
        "eps_est": x.get("epsEstimate"),
    } for x in rows]


def sec_filings(limit):
    """Aktuelle 8-K-Meldungen (Ad-hoc-Pflichtmitteilungen US).
    Quelle: SEC EDGAR, offiziell und ohne Key."""
    url = ("https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent"
           "&type=8-K&company=&dateb=&owner=include&count=40&output=atom")
    try:
        r = requests.get(url, headers=UA, timeout=25)
        r.raise_for_status()
        root = ET.fromstring(r.content)
    except Exception as e:
        print("  ! SEC:", e)
        return []
    ns = {"a": "http://www.w3.org/2005/Atom"}
    out = []
    for entry in root.findall("a:entry", ns)[:limit]:
        title = (entry.findtext("a:title", "", ns) or "").strip()
        link = entry.find("a:link", ns)
        out.append({
            "title": title,
            "url": link.get("href") if link is not None else "",
            "updated": (entry.findtext("a:updated", "", ns) or "")[:16].replace("T", " "),
        })
    return out

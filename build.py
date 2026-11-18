# build.py – holt alles ab und schreibt docs/index.html.

import datetime as dt
import html
import os

import config as C
import sources as S
import clock 

CSS = """
:root{--bg:#0b0e14;--card:#141822;--bd:#242b3a;--ink:#e6e9ef;--ink2:#99a3b8;
--ink3:#5d6779;--up:#3fb950;--dn:#f85149;--mono:ui-monospace,SFMono-Regular,Menlo,monospace}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.6 -apple-system,
BlinkMacSystemFont,'Segoe UI',sans-serif;-webkit-font-smoothing:antialiased}
.wrap{max-width:880px;margin:0 auto;padding:22px 16px 40px}
h1{font-size:19px;margin:0}
.stamp{font-family:var(--mono);font-size:12px;color:var(--ink3);margin-top:5px}
h2{font-size:11px;letter-spacing:.09em;text-transform:uppercase;color:var(--ink3);
margin:30px 0 10px}
.idx{display:grid;gap:8px;grid-template-columns:repeat(auto-fit,minmax(135px,1fr))}
.tile{background:var(--card);border:1px solid var(--bd);border-radius:10px;padding:11px 12px}
.tile .k{font-size:11.5px;color:var(--ink3)}
.tile .v{font-family:var(--mono);font-size:17px;font-weight:600;margin-top:3px}
.tile .c{font-family:var(--mono);font-size:12.5px;font-weight:600;margin-top:2px}
.cols{display:grid;gap:10px;grid-template-columns:1fr}
@media(min-width:640px){.cols{grid-template-columns:1fr 1fr}}
table{width:100%;border-collapse:collapse;background:var(--card);
border:1px solid var(--bd);border-radius:10px;overflow:hidden}
td{padding:8px 11px;border-top:1px solid #1d2330;font-size:13.5px}
tr:first-child td{border-top:0}
td.sym{font-family:var(--mono);font-weight:500}
td.num{font-family:var(--mono);text-align:right;font-variant-numeric:tabular-nums}
.up{color:var(--up)}.dn{color:var(--dn)}
ul.news{list-style:none;padding:0;margin:0}
ul.news li{background:var(--card);border:1px solid var(--bd);border-radius:10px;
padding:11px 13px;margin-bottom:7px}
ul.news a{color:var(--ink);text-decoration:none;font-size:14px;font-weight:500}
ul.news .m{font-size:11.5px;color:var(--ink3);margin-top:4px;font-family:var(--mono)}
.tag{display:inline-block;background:#1f2533;color:var(--ink2);border-radius:4px;
padding:1px 5px;margin-right:4px;font-size:10.5px}
.empty{color:var(--ink3);font-size:13px;font-style:italic}
footer{margin-top:32px;padding-top:14px;border-top:1px solid var(--bd);
font-size:11.5px;color:var(--ink3)}
"""


def esc(s):
    return html.escape(str(s if s is not None else ""))


def tiles(rows, names):
    if not rows:
        return '<p class="empty">keine Kursdaten</p>'
    out = []
    for q in rows:
        cls = "up" if q["change_pct"] > 0 else ("dn" if q["change_pct"] < 0 else "")
        out.append(
            f'<div class="tile"><div class="k">{esc(names.get(q["symbol"], q["symbol"]))}</div>'
            f'<div class="v">{q["price"]:,.2f}</div>'
            f'<div class="c {cls}">{q["change_pct"]:+.2f}%</div></div>'
        )
    return '<div class="idx">' + "".join(out) + "</div>"


def movers_table(rows):
    if not rows:
        return '<p class="empty">keine Daten</p>'
    body = []
    for q in rows:
        cls = "up" if q["change_pct"] > 0 else ("dn" if q["change_pct"] < 0 else "")
        body.append(
            f'<tr><td class="sym">{esc(q["symbol"])}</td>'
            f'<td class="num">{q["price"]:,.2f}</td>'
            f'<td class="num {cls}">{q["change_pct"]:+.2f}%</td></tr>'
        )
    return "<table>" + "".join(body) + "</table>"


def news_list(items):
    if not items:
        return '<p class="empty">keine Nachrichten geladen</p>'
    out = []
    for n in items:
        tags = "".join(f'<span class="tag">{esc(t)}</span>' for t in n["tickers"])
        out.append(
            f'<li><a href="{esc(n["url"])}">{esc(n["title"])}</a>'
            f'<div class="m">{tags}{esc(n["source"])} · {esc(n["published"])}</div></li>'
        )
    return '<ul class="news">' + "".join(out) + "</ul>"


def earnings_table(rows):
    if not rows:
        return '<p class="empty">keine Termine</p>'
    body = []
    for e in rows[:25]:
        est = f'{e["eps_est"]:.2f}' if isinstance(e["eps_est"], (int, float)) else "–"
        body.append(
            f'<tr><td class="sym">{esc(e["symbol"])}</td>'
            f'<td>{esc(e["date"])} · {esc(e["hour"])}</td>'
            f'<td class="num">{est}</td></tr>'
        )
    return "<table>" + "".join(body) + "</table>"


def filings_list(rows):
    if not rows:
        return '<p class="empty">keine Meldungen</p>'
    out = []
    for f in rows:
        out.append(
            f'<li><a href="{esc(f["url"])}">{esc(f["title"])}</a>'
            f'<div class="m">{esc(f["updated"])}</div></li>'
        )
    return '<ul class="news">' + "".join(out) + "</ul>"


def main():
    now = dt.datetime.now(dt.timezone.utc)

    print("1/5 Indizes ...")
    idx = S.quotes(list(C.INDICES.keys()))

    print("2/5 Watchlist ...")
    watch = S.quotes(C.US + C.EU)
    ranked = sorted(watch, key=lambda q: q["change_pct"], reverse=True)
    winners = ranked[: C.MOVERS]
    losers = ranked[-C.MOVERS :][::-1]

    print("3/5 News ...")
    items = S.news(C.US + C.EU, C.NEWS_ITEMS)

    print("4/5 Earnings ...")
    earn = S.earnings(C.EARNINGS_DAYS)

    print("5/5 SEC ...")
    filings = S.sec_filings(12)

    page = f"""<!DOCTYPE html>
<html lang="de"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>HMFS · {now:%d.%m.%Y}</title><style>{CSS}</style></head><body>
<div class="wrap">
<h1>HMFS</h1>
<div class="stamp">Stand {now:%d.%m.%Y %H:%M} UTC · {len(watch)} Werte · {len(items)} Meldungen</div>

<h2>Indizes &amp; Makro</h2>
{tiles(idx, C.INDICES)}

<h2>Bewegung in deiner Watchlist</h2>
<div class="cols">
  <div><h2 style="margin-top:0">Gewinner</h2>{movers_table(winners)}</div>
  <div><h2 style="margin-top:0">Verlierer</h2>{movers_table(losers)}</div>
</div>

<h2>Nachrichten</h2>
{news_list(items)}

<h2>Earnings-Kalender · naechste {C.EARNINGS_DAYS} Tage</h2>
{earnings_table(earn)}

<h2>SEC 8-K · aktuelle Pflichtmitteilungen</h2>
{filings_list(filings)}

<footer>Kurse via yfinance (unoffiziell) · News via Marketaux · Termine via Finnhub ·
Filings via SEC EDGAR. Keine Anlageberatung, keine Gewaehr auf Richtigkeit.</footer>
</div></body></html>"""

    page = clock.inject(page)
    
    os.makedirs(os.path.dirname(C.OUT), exist_ok=True)
    with open(C.OUT, "w", encoding="utf-8") as fh:
        fh.write(page)
    print("fertig ->", C.OUT, f"({len(page)/1024:.1f} KB)")


if __name__ == "__main__":
    main()

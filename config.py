# config.py – alles, was du regelmaessig anfasst, steht hier.

# Deine Watchlist. US-Symbole ohne Suffix, europaeische mit Boersensuffix:
# .DE = Xetra, .AS = Amsterdam, .PA = Paris, .SW = Schweiz, .L = London
US = ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA", "AMD", "JPM", "XOM"]
EU = ["SAP.DE", "SIE.DE", "ALV.DE", "BMW.DE", "RHM.DE", "DTE.DE",
      "ASML.AS", "MC.PA", "NESN.SW"]

# Indizes und Makro-Kontext fuer die Kopfzeile
INDICES = {
    "^GDAXI":    "DAX",
    "^STOXX50E": "Euro Stoxx 50",
    "^GSPC":     "S&P 500",
    "^IXIC":     "Nasdaq Composite",
    "^VIX":      "VIX",
    "^TNX":      "US 10Y Rendite",
}

NEWS_ITEMS = 18          # wie viele Schlagzeilen auf die Seite
EARNINGS_DAYS = 7        # Vorlauf fuer den Earnings-Kalender
MOVERS = 8               # Top-Gewinner / -Verlierer je Liste
OUT = "docs/index.html"

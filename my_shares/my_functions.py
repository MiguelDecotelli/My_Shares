import csv
import requests
import datetime
import pytz
import uuid
import urllib.parse
from flask import render_template
import yfinance as yf


def apology(message, code=400):
    """Render an error message to the user."""
    return render_template("apology.html", top=message, bottom=code), code

def lookup(symbol):
    """Look up quote for symbol using yfinance."""
    symbol = symbol.upper().strip()
    try:
        ticker = yf.Ticker(symbol)
        # fast_info é mais rápido para pegar o último preço
        price = ticker.fast_info.get("lastPrice")
        
        if price is None:
            return None
            
        # Busca o nome da empresa (fallback para o próprio símbolo se demorar/falhar)
        info = ticker.info
        name = info.get("shortName") or info.get("longName") or symbol

        return {
            "name": name,
            "price": round(float(price), 2),
            "symbol": symbol
        }
    except Exception:
        return None

def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"

def get_history(symbol, period="1mo"):
    """Fetch historical closing prices for a given symbol."""
    import yfinance as yf
    symbol = symbol.upper().strip()
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period)
        
        if hist.empty:
            return None
            
        # Formatar datas para o eixo X e preços para o eixo Y do gráfico
        dates = hist.index.strftime('%Y-%m-%d').tolist()
        prices = hist['Close'].round(2).tolist()
        
        return {"dates": dates, "prices": prices}
    except Exception:
        return None
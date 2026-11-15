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

def brl(value):
    """Formata o valor como Real Brasileiro (BRL)."""
    # Formata com 2 casas decimais e separador de milhar americano
    formatted = f"R$ {value:,.2f}"
    # Inverte vírgula e ponto para o padrão brasileiro
    return formatted.replace(",", "X").replace(".", ",").replace("X", ".")

def lookup(symbol):
    """Look up quote for symbol using yfinance."""
    import yfinance as yf
    symbol = symbol.upper().strip()
    
    # Mágica Bovespa: Adiciona .SA automaticamente se não houver
    if not symbol.endswith(".SA"):
        symbol += ".SA"
        
    try:
        ticker = yf.Ticker(symbol)
        price = ticker.fast_info.get("lastPrice")
        if price is None:
            return None
        info = ticker.info
        name = info.get("shortName") or info.get("longName") or symbol

        return {
            "name": name,
            "price": round(float(price), 2),
            "symbol": symbol
        }
    except Exception:
        return None

def get_history(symbol, period="1mo"):
    """Fetch historical closing prices for a given symbol."""
    import yfinance as yf
    symbol = symbol.upper().strip()
    
    # Mágica Bovespa: Adiciona .SA automaticamente se não houver
    if not symbol.endswith(".SA"):
        symbol += ".SA"
        
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period)
        if hist.empty:
            return None
        dates = hist.index.strftime('%Y-%m-%d').tolist()
        prices = hist['Close'].round(2).tolist()
        return {"dates": dates, "prices": prices}
    except Exception:
        return None

def format_datetime(value):
    """Formata datas para o padrão DD/MM/YYYY HH:MM:SS no Jinja."""
    if value is None:
        return ""
    
    # Se for um objeto datetime real do Python/SQLAlchemy
    if hasattr(value, 'strftime'):
        return value.strftime("%d/%m/%Y %H:%M:%S")
        
    # Se o banco SQLite tiver salvo a data como texto puro (ex: "2026-11-14 23:47:04.12345")
    val_str = str(value)
    if len(val_str) >= 10:
        year = val_str[0:4]
        month = val_str[5:7]
        day = val_str[8:10]
        time_part = val_str[11:19]
        return f"{day}/{month}/{year} {time_part}"
        
    return val_str


# def lookup(symbol):
#     """Look up quote for symbol using yfinance."""
#     symbol = symbol.upper().strip()
#     try:
#         ticker = yf.Ticker(symbol)
#         # fast_info é mais rápido para pegar o último preço
#         price = ticker.fast_info.get("lastPrice")
        
#         if price is None:
#             return None
            
#         # Busca o nome da empresa (fallback para o próprio símbolo se demorar/falhar)
#         info = ticker.info
#         name = info.get("shortName") or info.get("longName") or symbol

#         return {
#             "name": name,
#             "price": round(float(price), 2),
#             "symbol": symbol
#         }
#     except Exception:
#         return None


# def brl(value):
#     """Format value as brl."""
#     return f"${value:,.2f}"

# def get_history(symbol, period="1mo"):
#     """Fetch historical closing prices for a given symbol."""
#     import yfinance as yf
#     symbol = symbol.upper().strip()
#     try:
#         ticker = yf.Ticker(symbol)
#         hist = ticker.history(period=period)
        
#         if hist.empty:
#             return None
            
#         # Formatar datas para o eixo X e preços para o eixo Y do gráfico
#         dates = hist.index.strftime('%Y-%m-%d').tolist()
#         prices = hist['Close'].round(2).tolist()
        
#         return {"dates": dates, "prices": prices}
#     except Exception:
#         return None
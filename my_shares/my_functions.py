import csv
import requests
import datetime
import pytz
import uuid
import urllib.parse
from flask import render_template



def apology(message, code=400):
    """Render an error message to the user."""
    return render_template("apology.html", top=message, bottom=code), code

# def lookup(symbol):
#     """Look up quote for symbol."""
#     # Contact API
#     try:
#         api_key = API_KEY
#         url = f"https://api.iex.cloud/v1/data/core/quote/{urllib.parse.quote_plus(symbol)}?token={api_key}"
#         response = requests.get(url)
#         response.raise_for_status()
#     except requests.RequestException:
#         print("Deu ruim")
#         return None

#     # Parse response
#     try:
#         quote = response.json()
#         return {
#             "name": quote["companyName"],
#             "price": float(quote["latestPrice"]),
#             "symbol": quote["symbol"]
#         }
#     except (KeyError, TypeError, ValueError):
#         return None

def lookup(symbol):
    """Look up quote for symbol."""

    # Prepare API request
    symbol = symbol.upper()
    end = datetime.datetime.now(pytz.timezone("US/Eastern"))
    start = end - datetime.timedelta(days=7)

    # Yahoo Finance API
    url = (
        f"https://query1.finance.yahoo.com/v7/finance/download/{urllib.parse.quote_plus(symbol)}"
        f"?period1={int(start.timestamp())}"
        f"&period2={int(end.timestamp())}"
        f"&interval=1d&events=history&includeAdjustedClose=true"
    )

    # Query API
    try:
        response = requests.get(url, cookies={"session": str(uuid.uuid4())}, headers={"User-Agent": "python-requests", "Accept": "*/*"})
        response.raise_for_status()

        # CSV header: Date,Open,High,Low,Close,Adj Close,Volume
        quotes = list(csv.DictReader(response.content.decode("utf-8").splitlines()))
        quotes.reverse()
        price = round(float(quotes[0]["Adj Close"]), 2)
        return {
            "name": symbol,
            "price": price,
            "symbol": symbol
        }
    except (requests.RequestException, ValueError, KeyError, IndexError):
        return None

def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"
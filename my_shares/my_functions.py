from config_json import API_KEY
import requests
import urllib.parse
from flask import render_template


def apology(message, code=400):
    """Render an error message to the user."""
    return render_template("apology.html", top=message, bottom=code), code

def lookup(symbol):
    """Look up quote for symbol."""
    # Contact API
    try:
        api_key = API_KEY
        url = f"https://cloud.iexapis.com/stable/stock/{urllib.parse.quote_plus(symbol)}/quote?token={api_key}"
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        quote = response.json()
        return {
            "name": quote["companyName"],
            "price": float(quote["latestPrice"]),
            "symbol": quote["symbol"]
        }
    except (KeyError, TypeError, ValueError):
        return None

def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"
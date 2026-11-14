from flask import flash, redirect, render_template, request, url_for, jsonify
from flask_login import current_user, login_user, login_required, logout_user
from sqlalchemy import func
from my_shares import app, db
from my_shares.credit_card import check_credit_card
from my_shares.forms import *
from my_shares.models import User, Portfolio, Watchlist
from my_shares.my_functions import apology, lookup, usd, get_history
from werkzeug.security import check_password_hash, generate_password_hash

app.config["TEMPLATES_AUTO_RELOAD"] = True

app.jinja_env.filters["usd"] = usd


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    form = RegistrationForm()

    if form.validate_on_submit():

        user = User(username=form.username.data,
                    password=form.password.data,
                    )
        try:
            db.session.add(user)
            db.session.commit()
        except Exception:
            return apology('Username is already taken!')

        flash("Registered!")
        return redirect(url_for("login"))

    return render_template("/register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():

        user = User.query.filter_by(username=form.username.data).first()

        if user is None or not user.check_password(form.password.data):
            return apology("Invalid username or password", 403)

        login_user(user)
        flash(f'Welcome, {user.username}!')

        return redirect(url_for("index"))

    return render_template("/login.html", form=form)


@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    """Change username's password"""

    form = ChangePassword()

    if form.validate_on_submit():
        old_password = request.form.get("old_password")

        # Verifica direto no usuário logado
        if not current_user.check_password(old_password):
            return apology("Password is incorrect!", 400)
        
        new_password = generate_password_hash(request.form.get("new_password"))
        current_user.password_hash = new_password

        db.session.commit()
        flash("Password changed!")
        return redirect("/")

    return render_template("change_password.html", form=form)


@app.route('/logout')
@login_required
def logout():

    logout_user()
    flash('See you soon!')
    return redirect(url_for('index'))

@app.route("/reset_account", methods=["POST"])
@login_required
def reset_account():
    """Declare bankruptcy and reset account to default."""
    Portfolio.query.filter_by(user_id=current_user.id).delete()
    Watchlist.query.filter_by(user_id=current_user.id).delete()
    current_user.cash = 10000.00
    db.session.commit()
    
    flash("Bankruptcy declared. Account reset to US$ 10,000.00.")
    return redirect("/")

@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote and historical data."""
    form = QuoteForm()

    if request.method == "GET":
        symbol_from_url = request.args.get("symbol")
        if symbol_from_url:
            form.symbol.data = symbol_from_url.upper()
    
    if form.validate_on_submit():
        symbol = request.form.get("symbol")
        ticker = lookup(symbol)
        
        if not ticker:
            return apology("Invalid ticker symbol", 400)
            
        # Busca o histórico dos últimos 30 dias
        history = get_history(symbol)
            
        return render_template("quoted.html", ticker=ticker, history=history)
        
    return render_template("quote.html", form=form)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    form = BuyForm()

    if request.method == "GET":
        symbol_from_url = request.args.get("symbol")
        if symbol_from_url:
            form.symbol.data = symbol_from_url.upper()

    if form.validate_on_submit():

        if not request.form.get("symbol"):
            return apology("Missing symbol", 400)

        try:
            new_shares = int(request.form.get("shares"))
        except:
            return apology("Must be integer", 400)

        try:
            ticker = lookup(request.form.get("symbol"))
            new_stocks = ticker["price"] * float(new_shares)
        except (KeyError, TypeError, ValueError):
            return apology("Invalid ticker symbol", 400)

        if new_shares <= 0:
            return apology("Must be positive number", 400)
        else:
            user_cash = current_user.cash

            if new_stocks > user_cash:
                return apology("Can't afford", 400)
            else:
                current_user.cash -= new_stocks

                portfolio = Portfolio(user_id=current_user.id,
                                      symbol=form.symbol.data.upper(),
                                      name=ticker["name"],
                                      shares=form.shares.data,
                                      transaction_type="Buy",
                                      price=ticker["price"],
                                      total=ticker["price"]*new_shares,
                                      )
                db.session.add(portfolio)
                db.session.commit()
                flash("Bought!")
                return redirect("/")

    return render_template("/buy.html", form=form)

@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    my_portfolio = db.session.query(
        Portfolio.symbol,
        Portfolio.name,
        func.sum(Portfolio.shares).label('shares'),
        func.sum(Portfolio.total).label('total') # Total líquido investido
    ).filter_by(user_id=current_user.id).group_by(Portfolio.symbol, Portfolio.name).all()

    portfolio = []
    chart_labels = []
    chart_data = []

    for share in my_portfolio:
        if share.shares > 0: # Só processa ações que você ainda possui
            share_info = lookup(share.symbol)
            if share_info:
                current_price = share_info["price"]
                current_total_value = current_price * share.shares
                
                # Calcula o Lucro/Prejuízo (P&L)
                pl_value = current_total_value - share.total
                pl_percent = (pl_value / share.total) * 100 if share.total > 0 else 0

                updated_share = {
                    "symbol": share.symbol,
                    "name": share.name,
                    "shares": share.shares,
                    "price": current_price,
                    "total": current_total_value,
                    "pl_value": pl_value,
                    "pl_percent": pl_percent
                }
                portfolio.append(updated_share)
                
                # Prepara os dados para o gráfico
                chart_labels.append(share.symbol)
                chart_data.append(current_total_value)

    cash = current_user.cash
    total_cash = cash + sum(entry["total"] for entry in portfolio)
    
    # Adiciona o dinheiro em caixa no gráfico
    chart_labels.append("Cash")
    chart_data.append(cash)

    return render_template("index.html", 
                           portfolio=portfolio, 
                           cash=cash, 
                           total_cash=total_cash,
                           chart_labels=chart_labels,
                           chart_data=chart_data)

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    portfolio = Portfolio.query.all()
    form = SellForm()

    if form.validate_on_submit():
        ticker = lookup(request.form.get("symbol"))

        if not ticker:
            return apology("Missing symbol", 400)

        if ticker is None:
            return apology("Invalid symbol", 400)

        try:
            shares_to_sell = int(request.form.get("shares"))
        except ValueError:
            return apology("Must be integer", 400)

        my_shares = (
            db.session.query(
                Portfolio.shares
            )
            .filter_by(
                user_id=current_user.id,
                symbol=ticker["symbol"])
            .all()
        )
        all_shares = sum(int(value.shares) for value in my_shares)

        if not my_shares:
            return apology("You don't have any of this shares!", 400)

        if shares_to_sell > all_shares:
            return apology("Not enough shares", 400)
        elif shares_to_sell <= 0:
            return apology("Must be positive number", 400)

        current_price = ticker["price"]

        new_sell = current_price * shares_to_sell

        current_user.cash += new_sell

        sold_shares = Portfolio(
            user_id=current_user.id,
            symbol=ticker["symbol"],
            name=ticker["name"],
            shares=-shares_to_sell,
            transaction_type="Sell",
            price=current_price,
            total=-new_sell
        )
        db.session.add(sold_shares)

        db.session.commit()

        flash("Sold!")
        return redirect("/")

    return render_template("sell.html", form=form, portfolio=portfolio)


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    transactions = Portfolio.query.filter_by(
        user_id=current_user.id).all()

    return render_template("history.html", transactions=transactions)


@app.route("/list_of_stocks", methods=["GET", "POST"])
@login_required
def list_of_stocks():
    """Show the list of all stocks"""

    form = StockListForm()

    import csv
    list_of_shares = []
    no_company = False

    if form.validate_on_submit():
        search_query = form.symbol_search.data.lower()

        with open('all_stocks.csv') as file:
            stocks = csv.DictReader(file)
            for row in stocks:
                if search_query in row["Company Name"].lower():
                    list_of_shares.append({"symbol": row["Symbol"], "company_name": row["Company Name"],
                                           "industry": row["Industry"], "market_cap": row["Market Cap"]})

        if not list_of_shares:
            no_company = True

    return render_template("list_of_stocks.html", form=form,  list_of_shares=list_of_shares, no_company=no_company)


@app.route("/add_cash", methods=["GET", "POST"])
@login_required
def add_cash():
    """Add more cash into user's account"""

    form = CashForm()

    if form.validate_on_submit():
        user_password = current_user.password_hash
        if not check_password_hash(user_password, request.form.get("password")):
            return apology("Password is incorrect!", 403)
        else:
            card = request.form.get("add_card")
            if check_credit_card(card) == False:
                return apology("CARD IS INVALID", 403)
            else:
                add_cash = int(request.form.get("add_cash"))
                current_user.cash += add_cash
                db.session.commit()
                flash("Cash Added!")

            return redirect("/")

    return render_template("/add_cash.html", form=form)

@app.route("/watchlist")
@login_required
def watchlist():
    user_watchlist = Watchlist.query.filter_by(user_id=current_user.id).all()
    stocks = []
    
    for item in user_watchlist:
        info = lookup(item.symbol)
        if info:
            stocks.append(info)
            
    return render_template("watchlist.html", stocks=stocks)

# 2. Endpoint da API para adicionar/remover da Watchlist via AJAX
@app.route("/toggle_watchlist", methods=["POST"])
@login_required
def toggle_watchlist():
    data = request.get_json()
    symbol = data.get("symbol")
    name = data.get("name")
    
    existing = Watchlist.query.filter_by(user_id=current_user.id, symbol=symbol).first()
    
    if existing:
        db.session.delete(existing)
        db.session.commit()
        return jsonify({"status": "removed", "symbol": symbol})
    else:
        new_fav = Watchlist(user_id=current_user.id, symbol=symbol, name=name)
        db.session.add(new_fav)
        db.session.commit()
        return jsonify({"status": "added", "symbol": symbol})

# 3. Endpoint da API para a Busca ao Vivo (Live Search) no CSV
@app.route("/api/search_stocks")
@login_required
def api_search_stocks():
    query = request.args.get("q", "").lower()
    if not query or len(query) < 2:
        return jsonify([]) # Retorna vazio se a busca for muito curta

    results = []
    import csv
    with open('all_stocks.csv') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if query in row["Company Name"].lower() or query in row["Symbol"].lower():
                results.append({
                    "symbol": row["Symbol"],
                    "name": row["Company Name"],
                    "industry": row["Industry"],
                    "market_cap": row["Market Cap"]
                })
            if len(results) >= 20: # Limita a 20 resultados para performance
                break
                
    # Verifica quais resultados já estão na watchlist do usuário
    user_watchlist_symbols = [w.symbol for w in Watchlist.query.filter_by(user_id=current_user.id).all()]
    
    for res in results:
        res["is_favorite"] = res["symbol"] in user_watchlist_symbols

    return jsonify(results)

@app.route("/api/history/<symbol>")
@login_required
def api_history(symbol):
    """API endpoint to get historical data for the dashboard chart."""
    history = get_history(symbol)
    if history:
        return jsonify(history)
    return jsonify({"error": "No data found"}), 404

if __name__ == "__main__":
    app.run(debug=True)

import os
from datetime import datetime

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    userid = session["user_id"]

    #which stocks the user owns,  the numbers of shares owned, the current price of each stock SUM of amounts
    ownstocks = db.execute("SELECT symbol, amount FROM stock WHERE userid=?", userid)

    # Current price of each stock
    for stock in ownstocks:
        # passing through the symbol to lookup API for current stock price & name
        quote = lookup(stock['symbol'])
        stock["price"] = quote["price"]
        stock["name"] = quote["name"]
        stock["total"] = stock["amount"] * stock["price"]

    print(ownstocks)

    # Get users current cash
    results = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
    usercash = results[0]["cash"]

    print(usercash)

    total = usercash
    for stock in ownstocks:
        total = total + stock["total"]

    print(total)

    return render_template("index.html", ownstocks=ownstocks, usercash=usd(usercash), total=usd(total))



@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":

        symbol = request.form.get("symbol")
        shares = int(request.form.get("shares"))

        #Return apology if no input was found
        if not symbol:
            return apology("must provide symbol", 403)

        #looking up symbol
        buy = lookup(symbol)

        #Return apology if symbol not found
        if not buy:
            return apology("stock not found", 403)

        if not shares:
            return apology("must provide amount of shares", 403)

        if shares < 1 :
            return apology("must provide a postive number", 403)

        # how much cash user has from user table

        results = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])

        # calculates pruchase price times the price found in buy variable
        stockprice = shares * buy["price"]

        # if user doesn't have enough cash to buy, return apology
        if results[0]["cash"] < stockprice :
            return apology("must provide more money", 403)

        # purchase price
        sum = results[0]["cash"] - stockprice

        # update users cash with new amount after purchase
        db.execute("UPDATE users SET cash=? WHERE id = ?", sum, session["user_id"])

        #Add transatction to new table, username, purchase date, stock, stock amount, pruchase price
        date = datetime.now()
        userid = session["user_id"]
        price = buy["price"]

        db.execute("INSERT INTO purchases (date, userid, stock, amount, price) VALUES(?, ?, ?, ?, ?)", date, userid, symbol,shares, price)

        # Update users stock table with their new stocks
        stocks = db.execute("SELECT * FROM stock WHERE userid = ? AND symbol = ?", userid, symbol)

        print(stocks)

        # first time buying this stock, insert a new row
        if len(stocks) == 0:

            db.execute("INSERT INTO stock (userid, symbol, amount) VALUES(?, ?, ?)", userid, symbol, shares)

        # they already own some of this stock, update the row
        else:
            amount = db.execute("SELECT amount FROM stock WHERE symbol=? AND userid=?",symbol, userid)
            newAmount = amount[0]["amount"] + shares
            db.execute("UPDATE stock SET amount=? WHERE symbol=? AND userid=?", newAmount, symbol, userid)

        #redirect user to homepage
        return redirect("/")
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    userid = session["user_id"]

    #query for buy table
    buys = db.execute("SELECT * FROM purchases WHERE id = ?", session["user_id"])

    for buy in buys:
        buy["buy"] = True

    #query for the sell table
    sales = db.execute("SELECT * FROM sell WHERE id = ?", session["user_id"])

    for sale in sales:
        sale["buy"] = False
        sale["price"] = sale["sellprice"]
        sale["stock"] = sale["symbol"]

    history = buys + sales

    return render_template("history.html", history=history)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    # if POST - Display requested stock
    if request.method == "POST":
        symbol = request.form.get("symbol")

        #confirming the users input
        if not symbol:
            return apology("must provide a symbol", 403)

        # passing through the symbol
        quote = lookup(symbol)

        if not quote:
            return apology("stock not found", 403)

        # pass quote into quoted
        return render_template("quoted.html", quote=quote)
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # if POST - check user entered name and password
    if request.method == "POST":

        # Saves username from request into variable
        username = request.form.get("username")
        password = request.form.get("password")
        passconfirm = request.form.get("password-confirm")

        # Ensure username was submitted
        if not username:
            return apology("must provide username", 403)

        # Ensure password was given
        if not password:
            return apology("must provide a password", 403)

        # Ensure password confirmation was given
        if not passconfirm:
            return apology("must confirm password", 403)

        # Ensure passwords match
        if password != passconfirm:
            return apology("passwords did not match", 403)

        # Hash password
        passwordHash = generate_password_hash(password)

        # create user in database
        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)",username, passwordHash)

         # Redirect user to home page
        return redirect("/")

    # else - return register.html to ask user for name and password
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    userid = session["user_id"]

    if request.method == "POST":

        symbol = request.form.get("symbol")
        amount = int(request.form.get("shares"))

        #Return apology if no input was found
        if not symbol:
            return apology("must provide symbol", 403)

        #looking up symbol
        sell = lookup(symbol)

        #Return apology if symbol not found
        if not sell:
            return apology("stock not found", 403)

        if not amount:
            return apology("must provide amount of shares", 403)

        if amount < 1 :
            return apology("must provide a postive number", 403)

        # Update users stock table with their sold stocks
        usersamount = db.execute("SELECT amount FROM stock WHERE symbol=? AND userid=?",symbol, userid)
        newAmount = usersamount[0]["amount"] - amount

        if (newAmount < 0):
            return apology("must provide more stock", 403)

        # how much cash user has from user table
        results = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])

        # calculates pruchase price times the price found in buy variable
        stockprice = amount * sell["price"]

        # purchase price
        sum = results[0]["cash"] + stockprice

        # update users cash with new amount after purchase
        db.execute("UPDATE users SET cash=? WHERE id = ?", sum, session["user_id"])

        #Add sell data into a new table userid, symbol, amount, sellprice, date
        date = datetime.now()

        sellprice = sell["price"]

        db.execute("INSERT INTO sell (date, userid, symbol, amount, sellprice) VALUES(?, ?, ?, ?, ?)", date, userid, symbol, amount, sellprice)

        # User sold all their stock selling this stock, insert a new row
        if newAmount == 0:
            db.execute("DELETE FROM stock WHERE userid=? AND symbol=?", userid, symbol)

        # they didnt sell all this stock, update the row
        else:
            db.execute("UPDATE stock SET amount=? WHERE symbol=? AND userid=?", newAmount, symbol, userid)

        # Redirect user to home page
        return redirect("/")

    else:

        stocks = db.execute("SELECT symbol FROM stock WHERE userid = ?", userid)
        return render_template("sell.html", stocks=stocks)

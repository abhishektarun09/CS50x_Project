import os
import datetime
import numpy as np
import pandas as pd

from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from babel.numbers import format_currency

from src.pipeline.predict_pipeline import CustomData, PredictPipeline
from src.utils import apology, login_required

app = Flask(__name__)
## Route for a home page

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route('/')
def index():
    return render_template('index.html', current_year = datetime.now().year) 

@app.route('/prediction', methods = ['GET','POST'])
#@login_required
def predict():
    if request.method == 'GET':
        return render_template('prediction.html')
    else:
        data = CustomData(
            km_driven=request.form.get('km_driven'),
            fuel=request.form.get('fuel'),
            seller_type=request.form.get('seller_type'),
            transmission=request.form.get('transmission'),
            owner=request.form.get('owner'),
            mileage=request.form.get('mileage'),
            engine=request.form.get('engine'),
            max_power=request.form.get('max_power'),
            seats=request.form.get('seats'),
            age=request.form.get('age')
        )
        pred_df = data.get_data_as_data_frame()
        print(pred_df)
        print("Before Prediction")

        predict_pipeline = PredictPipeline()
        print("Mid Prediction")
        
        results = predict_pipeline.predict(pred_df)
        print("After Prediction")
        
        formatted_prediction = results[0]
        formatted_prediction = format_currency(formatted_prediction, 'INR', locale='en_IN')
        return render_template('predicted.html', results = formatted_prediction)
    
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
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/predict")

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


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure confirmation password was submitted
        elif not request.form.get("confirmation"):
            return apology("must re enter password", 400)

        # Ensure password is same as confirmation password
        elif not (request.form.get("password") == request.form.get("confirmation")):
            return apology("passwords don't match", 400)

        # Hash the password
        hash = generate_password_hash(request.form.get("password"))

        try:
            # Store credentials in the database
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)",
                       request.form.get("username"), hash)

            result = db.execute("SELECT * FROM users WHERE username = ?",
                                request.form.get("username"))

            # Remember which user has logged in
            session["user_id"] = result[0]["id"]

            # Redirect user to home page
            return redirect("/predict")

        except:
            # Username already exists
            return apology("think of another username", 400)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")
    
@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    """Change Password"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure old password was submitted
        if not request.form.get("old_password"):
            return apology("must provide old password", 403)

        # Ensure new password was submitted
        elif not request.form.get("new_password"):
            return apology("must provide new password", 403)

        # Ensure new password was reentered
        elif not request.form.get("confirmation_password"):
            return apology("must re enter password", 403)

        # Ensure new password is same as confirmation password
        elif not (request.form.get("new_password") == request.form.get("confirmation_password")):
            return apology("passwords don't match", 403)

        # Ensure new password is not same as old password
        elif not (request.form.get("new_password") != request.form.get("old_password")):
            return apology("enter new password", 403)

        # Query database for PASSWORD
        rows = db.execute(
            "SELECT * FROM users WHERE id = ?", session["user_id"]
        )

        # Ensure old password is correct
        if not check_password_hash(
            rows[0]["hash"], request.form.get("old_password")
        ):
            return apology("must provide valid old password", 403)

        # Hash the new password
        hash = generate_password_hash(request.form.get("confirmation_password"))

        # Query database to store new PASSWORD
        db.execute(
            "UPDATE users SET hash = ? WHERE id = ?", hash, session["user_id"]
        )

        flash("Password Changed!")

        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("change_password.html")
    

if __name__ == "__main__":      
    app.run(debug = True, host = "0.0.0.0", port = 80) 

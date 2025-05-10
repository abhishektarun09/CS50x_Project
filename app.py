import os
import datetime
import numpy as np
import pandas as pd

from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

if os.getenv("SSL_CA_PATH") != "/app/cert/DigiCertGlobalRootCA.crt.pem":
    from dotenv import load_dotenv
    load_dotenv()

from babel.numbers import format_currency

from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

from src.pipeline.predict_pipeline import CustomData, PredictPipeline
from src.utils import apology, login_required

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

user = os.getenv("MYSQL_USER")
password = os.getenv("MYSQL_PASSWORD")
host = os.getenv("MYSQL_HOST")
port = os.getenv("MYSQL_PORT")
db_name = os.getenv("MYSQL_DB")

base_dir = os.path.dirname(os.path.abspath(__file__))
ssl_ca_path = os.path.join(base_dir, "cert", "DigiCertGlobalRootCA.crt.pem")

app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}"
    f"?ssl_ca={ssl_ca_path}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    hash = db.Column(db.String(500), nullable=False)

with app.app_context():
    print("SSL_CA_PATH used:", ssl_ca_path)
    db.create_all()

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

csrf = CSRFProtect(app)

@app.route('/')
def index():
    return render_template('index.html', current_year = datetime.now().year) 

@app.route('/prediction', methods = ['GET','POST'])
@login_required
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
        user = User.query.filter_by(username=request.form.get("username")).first()

        # Ensure username exists and password is correct
        if not user or not check_password_hash(user.hash, request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = user.id
        
        flash("Login Successful!")

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
    
    flash("You have logged out successfully.")

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
            # Check if username already exists
            existing_user = User.query.filter_by(username=request.form.get("username")).first()
            if existing_user:
                return apology("think of another username", 400)

            # Create and add user
            new_user = User(username=request.form.get("username"), hash=hash)
            db.session.add(new_user)
            db.session.commit()

            # Remember which user has logged in
            session["user_id"] = new_user.id
            
            flash("Registered!")

            # Redirect user to home page
            return redirect("/")

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

        # Query database for User details
        user = User.query.get(session["user_id"])

        # Ensure old password is correct
        if not user or not check_password_hash(user.hash, request.form.get("old_password")):
            return apology("must provide valid old password", 403)

        # Hash new password and update
        user.hash = generate_password_hash(request.form.get("confirmation_password"))
        db.session.commit()

        flash("Password Changed!")

        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("change_password.html")
    

if __name__ == "__main__":      
    app.run(host = "0.0.0.0", port = 80) 

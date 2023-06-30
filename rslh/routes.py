from flask import redirect, render_template, request, url_for
from flask_login import login_user, logout_user

from rslh import app, db
from rslh.forms import LoginForm, RegistrationForm
from rslh.models import User


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response


@app.route("/", methods=["GET"])
def index():
    return redirect(url_for("signin"))


@app.route("/signin", methods=["GET", "POST"])
def signin():
    form = LoginForm()
    if form.validate_on_submit():
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username, password=password).first()
        if not user:
            return redirect(url_for("signin"))
        login_user(user)
        return redirect(url_for("home"))
    return render_template("signin.html", form=form)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=request.form.get("username"),
            password=request.form.get("password"))
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("signin"))
    return render_template("signup.html", form=form)


@app.route("/home", methods=["GET"])
def home():
    return render_template("home.html")


@app.route("/signout", methods=["GET"])
def signout():
    logout_user()
    return redirect(url_for("signin"))

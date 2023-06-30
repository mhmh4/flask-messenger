from flask import redirect, render_template, request, url_for

from rslh import app
from rslh.forms import LoginForm, RegistrationForm


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
    if request.method == "POST":
        ...
        return redirect(url_for("home"))
    return render_template("signin.html", form=form)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = RegistrationForm()
    if request.method == "POST":
        ...
        return redirect(url_for("signin"))
    return render_template("signup.html", form=form)


@app.route("/home", methods=["GET"])
def home():
    return render_template("home.html")


@app.route("/signout", methods=["GET"])
def signout():
    return redirect(url_for("signin"))

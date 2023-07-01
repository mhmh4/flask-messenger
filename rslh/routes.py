from flask import redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from rslh import app, db
from rslh.forms import ConversationForm, LoginForm, RegistrationForm
from rslh.models import Conversation, User


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response


@app.route("/", methods=["GET"])
def index():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    return redirect(url_for("signin"))


@app.route("/signin", methods=["GET", "POST"])
def signin():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
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
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=request.form.get("username"),
            password=request.form.get("password"))
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("signin"))
    return render_template("signup.html", form=form)


@app.route("/home", methods=["GET", "POST"])
@login_required
def home():
    form = ConversationForm()
    if request.method == "POST":
        recipient = User.query.filter_by(username=request.form.get("username")).first()
        if not recipient:
            return redirect(url_for("home"))
        db.session.add(Conversation(user_id=current_user.id))
        db.session.add(Conversation(user_id=recipient.id))
        db.session.commit()
        return redirect(url_for("home"))
    conversations = Conversation.query.filter_by(user_id=current_user.id).all()
    return render_template("home.html", form=form, conversations=conversations)


@app.route("/signout", methods=["GET"])
@login_required
def signout():
    logout_user()
    return redirect(url_for("signin"))

from flask import redirect, render_template, request, session, url_for
from flask_login import current_user, login_required, login_user, logout_user
from flask_socketio import join_room, leave_room
from sqlalchemy import func

from msgs import app, db, socketio
from msgs.forms import ConversationForm, LoginForm, MessageForm, RegistrationForm
from msgs.models import Conversation, Message, User


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


@app.route("/signout", methods=["GET"])
@login_required
def signout():
    logout_user()
    return redirect(url_for("signin"))


@app.route("/home", methods=["GET", "POST"])
@login_required
def home():
    form = ConversationForm()
    if form.validate_on_submit():
        recipient = User.query.filter_by(username=request.form.get("username")).first()
        if not recipient:
            return redirect(url_for("home"))

        latest_conversation_id = db.session.query(func.max(Conversation.conversation_id)).scalar() or 0

        c1 = Conversation(user_id=current_user.id, conversation_id=latest_conversation_id + 1)
        db.session.add(c1)
        db.session.commit()
        # c1.conversation_id
        c2 = Conversation(user_id=recipient.id, conversation_id=latest_conversation_id + 1)
        db.session.add(c2)
        db.session.commit()
        return redirect(url_for("home"))
    conversations = Conversation.query.filter_by(user_id=current_user.id).all()
    return render_template("home.html", form=form, conversations=conversations)


@app.route("/conversation/<int:conversation_id>", methods=["GET", "POST"])
@login_required
def conversation(conversation_id):
    conversation = Conversation.query.filter_by(conversation_id=conversation_id).first()
    session["conversation_id"] = conversation_id
    form = MessageForm()
    if form.validate_on_submit():
        message = Message(
            content=request.form.get("content"),
            conversation_id=conversation_id,
            user_id=current_user.id)
        db.session.add(message)
        db.session.commit()
        return redirect(url_for("conversation", conversation_id=conversation_id))
    tmp = Message.query.filter_by(conversation_id=conversation_id)
    messages = tmp.all()
    other_user = Conversation.query.filter_by(conversation_id=conversation_id).filter(Conversation.user_id != current_user.id).first().user.username
    return render_template("conversation.html", form=form, conversation=conversation, messages=messages, other_user=other_user)


@socketio.on("join")
def on_join():
    join_room(session["conversation_id"])


@socketio.on("message")
def handle_message(data):
    print(f"Received message: {data}")
    print(current_user.id, session["conversation_id"])
    message = Message(
            content=data,
            conversation_id=session["conversation_id"],
            user_id=current_user.id)
    db.session.add(message)
    db.session.commit()

    socketio.emit("new_message", {
        "content": data,
        "username": message.user.username,
        "timestamp": str(message.created_at)
        }, to=session["conversation_id"])

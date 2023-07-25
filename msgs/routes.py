from flask import flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required, login_user, logout_user
from flask_socketio import join_room
from sqlalchemy import select
from sqlalchemy.orm import aliased

from msgs import app, db, socketio
from msgs.forms import ConversationForm, LoginForm, MessageForm, RegistrationForm
from msgs.models import Conversation, Message, Participation, User


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response


@app.route("/", methods=["GET"])
def index():
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
            flash("Invalid username or password.")
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
        username = request.form.get("username")
        if User.query.filter_by(username=username).count():
            flash("Username already exists.")
            return redirect(url_for("signup"))
        user = User(username=username, password=request.form.get("password"))
        db.session.add(user)
        db.session.commit()
        flash("Your account has been created.")
        return redirect(url_for("signin"))
    return render_template("signup.html", form=form)


@app.route("/signout", methods=["POST"])
@login_required
def signout():
    logout_user()
    return redirect(url_for("signin"))


@app.route("/home", methods=["GET", "POST"])
@login_required
def home():
    form = ConversationForm()

    if form.validate_on_submit():
        other_user = User.query.filter_by(username=request.form.get("username")).first()
        if not other_user:
            flash("Cannot find other user.")
            return redirect(url_for("home"))

        participant1 = aliased(Participation)
        participant2 = aliased(Participation)

        conversation = (
            db.session.query(participant1)
            .join(
                participant2,
                participant1.conversation_id == participant2.conversation_id,
            )
            .filter(participant1.user_id == current_user.id)
            .filter(participant2.user_id == other_user.id)
            .first()
        )
        if conversation:
            flash(f"Conversation with {other_user.username} already exists.")
            return redirect(url_for("home"))

        conversation = Conversation()
        db.session.add(conversation)
        db.session.commit()  # `conversation.id` now usuable

        db.session.add(
            Participation(user_id=current_user.id, conversation_id=conversation.id)
        )
        db.session.add(
            Participation(user_id=other_user.id, conversation_id=conversation.id)
        )
        db.session.commit()

        flash(f"Added conversation with {other_user.username}.")
        return redirect(url_for("home"))

    participating_conversations = (
        select(Participation.conversation_id)
        .where(Participation.user_id == current_user.id)
        .alias("participating_conversations")
    )

    conversations = (
        db.session.query(
            participating_conversations.c.conversation_id,
            User.username.label("other_user"),
        )
        .join(
            Participation,
            Participation.conversation_id
            == participating_conversations.c.conversation_id,
        )
        .join(User, User.id == Participation.user_id)
        .filter(User.id != current_user.id)
        .all()
    )

    return render_template("home.html", form=form, conversations=conversations)


@app.route("/conversation/<int:conversation_id>", methods=["GET", "POST"])
@login_required
def conversation(conversation_id):
    conversation = Conversation.query.filter_by(id=conversation_id).first()
    session["conversation_id"] = conversation_id

    form = MessageForm()

    if form.validate_on_submit():
        message = Message(
            content=request.form.get("content"),
            conversation_id=conversation_id,
            user_id=current_user.id,
        )
        db.session.add(message)
        db.session.commit()
        return redirect(url_for("conversation", conversation_id=conversation_id))

    messages = Message.query.filter_by(conversation_id=conversation_id).all()

    other_user = (
        Participation.query.filter(
            Participation.conversation_id == conversation_id,
            Participation.user_id != current_user.id,
        )
        .first()
        .user.username
    )

    return render_template(
        "conversation.html",
        form=form,
        conversation=conversation,
        messages=messages,
        other_user=other_user,
    )


@socketio.on("join")
def on_join():
    join_room(session["conversation_id"])


@socketio.on("message")
def handle_message(data):
    message = Message(
        content=data,
        conversation_id=session["conversation_id"],
        user_id=current_user.id,
    )
    db.session.add(message)
    db.session.commit()

    socketio.emit(
        "new_message",
        {
            "content": data,
            "username": message.user.username,
            "created_at": str(message.created_at),
        },
        to=session["conversation_id"],
    )

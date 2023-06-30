from datetime import datetime

from flask_login import UserMixin
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from rslh import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    conversations = relationship("Conversation", backref="user", lazy=True)


class Conversation(db.Model):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    messages = relationship("Message", backref="conversation", lazy=True)


class Message(db.Model):
    id = Column(Integer, primary_key=True)
    content = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow())
    conversation_id = Column(Integer, ForeignKey("conversation.id"))
    user_id = Column(Integer, ForeignKey("user.id"))

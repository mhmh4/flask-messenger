from datetime import datetime

from flask_login import UserMixin
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from msgs import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id             = Column(Integer, primary_key=True)
    username       = Column(String(255), nullable=False, unique=True)
    password       = Column(String(255), nullable=False)
    messages       = relationship("Message", backref="user", lazy=True)
    participations = relationship("Participation", backref="user", lazy=True)


class Participation(db.Model):
    id              = Column(Integer, primary_key=True)
    user_id         = Column(Integer, ForeignKey("user.id"))
    conversation_id = Column(Integer, ForeignKey("conversation.id"))


class Conversation(db.Model):
    id = Column(Integer, primary_key=True)



class Message(db.Model):
    id              = Column(Integer, primary_key=True)
    content         = Column(String(255))
    created_at      = Column(DateTime, default=lambda: datetime.utcnow())
    conversation_id = Column(Integer, ForeignKey("conversation.id"))
    user_id         = Column(Integer, ForeignKey("user.id"))

    def __repr__(self):
        return f"({self.created_at}) {self.user.username}: {self.content}"

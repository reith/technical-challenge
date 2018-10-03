from flask_ext import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean, nullable=True)
    problems = db.relationship('Problem', lazy='dynamic', backref='user')

    _logged_in = False

    def __init__(self, username, password):
        self.username = username
        self.password = generate_password_hash(password)

    def login(self):
        self._logged_in = True

    @property
    def is_authenticated(self):
        return self._logged_in

    @property
    def is_active(self):
        return self.active is not False

    def password_match(self, plain_password):
        return check_password_hash(self.password, plain_password)

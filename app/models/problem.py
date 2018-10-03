from flask_ext import db
from time import time
from datetime import datetime

_MAX_REQUEST_SIZE = 10000


class Problem(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date = db.Column(db.Integer)
    time_cost = db.Column(db.Integer)
    request = db.Column(db.String(_MAX_REQUEST_SIZE))
    response = db.Column(db.String(2000))

    def __init__(self, user):
        self.date = int(time())
        self.user = user

    def setRequest(self, request):
        self.request = request[:_MAX_REQUEST_SIZE]

    def to_dict(self):
        return {
            'date': datetime.fromtimestamp(self.date).strftime('%F %X'),
            'request': self.request,
            'response': self.response,
            'time_cost': self.time_cost
        }

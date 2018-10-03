import base64
from time import time
from functools import wraps

from flask import request
from flask_ext import login_manager, db
from flask_login import current_user

from models.user import User
from models.problem import Problem


@login_manager.header_loader
def load_user_by_header(header):
    header_val = header[6:]
    try:
        user_pass = base64.b64decode(header_val)
        username, password = user_pass.split(':')
        user = User.query.filter_by(username=username).first()
    except Exception:
        return None
    if user is not None and user.password_match(password):
        user.login()
        return user
    return None


def request_audit(f):
    @wraps(f)
    def wrapper(*a, **kw):
        if current_user is not None:
            problem = Problem(current_user)
            problem.setRequest(request.args.get('input'))
            before = time()
            ret = f(*a, **kw)
            problem.response = str(ret)
            problem.time_cost = time() - before
            db.session.add(problem)
            db.session.commit()
        else:
            ret = f(*a, **kw)
        return ret
    return wrapper

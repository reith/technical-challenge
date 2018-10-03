from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import sys
import argparse
import random

from solver.solver import solver
from exc import ApiError
from flask import Flask, request, jsonify

import json
from prometheus_client import Counter, start_wsgi_server as prometheus_server

from auth import request_audit
from flask_login import login_required, current_user
from flask_ext import db, login_manager

MAX_VALUE = 1000

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_pyfile('app.cfg')
requests_total = Counter('requests_total', 'Total number of requests')


# The root endpoint returns the app value. Some percentage of the time
# (given by app.config['failure_rate']) calls to this endpoint will cause the
# app to crash (exits non-zero).
@app.route('/v1/')
@login_required
@request_audit
def index():
    input_val = json.loads(request.args.get("input"))
    result = solver(input_val)
    return result

@app.route('/v2/')
@login_required
@request_audit
def index_v2():
    input_val = json.loads(request.args.get("input"))
    result = solver(input_val, repetitive=True)
    return result

@app.route('/report/')
@login_required
def report_requests():
    print (current_user.problems)
    return jsonify([p.to_dict() for p in current_user.problems])

@app.errorhandler(ApiError)
def show_api_error(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status
    return response

# To help with testing this endpoint will cause the app to crash
# every time it is called
@app.route('/crash')
def crash():
    requests_total.inc()
    request.environ.get('werkzeug.server.shutdown')()
    app.config.update({'crashed': True})
    return "{}"

@app.before_first_request
def create_tables():
    db.create_all()

@app.before_first_request
def create_test_user():
    from models.user import User
    test_user = User(*app.config.get('TEST_USER_CREDS').split(':'))
    db.session.add(test_user)
    db.session.commit()

def setup_app(app):
    db.init_app(app)
    login_manager.init_app(app)

def main(args):
    prometheus_server(args.monitor)

    app.config.update({
        'input': args.input,
        'failure_rate': args.failure_rate,
        'crashed': False
    })
    setup_app(app)
    app.run('0.0.0.0', port=args.port)

    if app.config['crashed']:
        print('app crashed, exiting non-zero')
        sys.exit(1)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--input',
        type=str,
        required=False,
        help='the input string'
    )
    parser.add_argument(
        '--port',
        type=int,
        required=True,
        help='the serving port'
    )
    parser.add_argument(
        '--monitor',
        type=int,
        required=True,
        help='the monitoring port'
    )
    parser.add_argument(
        '--failure-rate',
        type=float,
        default=0.2,
        help='the failure rate'
    )
    return parser.parse_args()


if __name__ == '__main__':
    main(parse_args())

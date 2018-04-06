#!/usr/bin/env python
from flask import Flask
from digital_milliet.digital_milliet import DigitalMilliet
import yaml
import argparse

app = Flask('digital_milliet')
dm = DigitalMilliet(app, config_file="../tests/testconfig.cfg")
mongo = dm.get_db()


def clear():
    with app.app_context():
        mongo.db.annotation.drop()


def install(fixture):
    clear()
    with open(fixture, 'r') as (stream):
        data = yaml.load(stream)
        with app.app_context():
            mongo.db.annotation.insert_many(data)


def run(loggedin=False):
    if loggedin is True:
        app.config["OAUTH_USER_OVERRIDE"] = {
            "oauth_user_uri": "http://fake",
            "oauth_user_name": "test user"
        }
        dm.oauth.auth_override = app.config["OAUTH_USER_OVERRIDE"]
    app.run(debug=True, host="0.0.0.0", port=5000)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Run a mongo example application')
    parser.add_argument(
        '--fixture',
        help='Path to fixtures',
        default="./tests/dbfixtureiiif.yml")
    parser.add_argument(
        '--clear',
        action='store_true',
        default=False,
        help='Clear fixtures')
    parser.add_argument(
        '--norun',
        dest="norun",
        action='store_true',
        default=False,
        help='Do not run the app')
    parser.add_argument(
        '--install',
        action='store_true',
        default=False,
        help='Install fixtures')
    parser.add_argument(
        '--loggedin',
        action='store_true',
        default=False,
        help='Mocks login')

    args = parser.parse_args()
    if args.install is True:
        install(args.fixture)
    elif args.clear is True:
        clear()

    if args.norun is False:
        print(args.loggedin)
        run(args.loggedin)

#!/usr/bin/env python
from flask import Flask
from digital_milliet.digital_milliet import DigitalMilliet
from digital_milliet.lib.configuration import Configuration
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--config', nargs='+', default=['config.cfg'],
                    help='list config files (default config.cfg)')
parser.add_argument("--env", action='store_true',
                    help="include configuration from environment")
args = parser.parse_args()

config_files = args.config
config_objects = []
if args.env:
    config_objects = [Configuration]

app = Flask('digital_milliet')
dm = DigitalMilliet(app, config_files, config_objects)
app.run(debug=True, host="0.0.0.0", port=5000)

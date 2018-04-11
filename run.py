#!/usr/bin/env python
from flask import Flask
from digital_milliet.digital_milliet import DigitalMilliet
import sys

config_files = ["config.cfg"]
if len(sys.argv) > 1:
    config_files = sys.argv[1:]

app = Flask('digital_milliet')
dm = DigitalMilliet(app, config_files=config_files)
app.run(debug=True, host="0.0.0.0", port=5000)

#!/usr/bin/env python
from flask import Flask
from digital_milliet.digital_milliet import DigitalMilliet
from digital_milliet.lib.configuration import Configuration
import sys

config_files = ["config.cfg"]
if len(sys.argv) > 1:
    config_files = sys.argv[1:]

config_files = []
config_objects = []
for arg in sys.argv[1:]:
    if arg == "ENV":
        config_objects.append(Configuration)
    else:
        config_files.append(arg)

if len(config_files) == 0:
    config_files = ["config.cfg"]

app = Flask('digital_milliet')
dm = DigitalMilliet(app, config_files, config_objects)
app.run(debug=True, host="0.0.0.0", port=5000)

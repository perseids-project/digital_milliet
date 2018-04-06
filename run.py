#!/usr/bin/env python
from flask import Flask
from digital_milliet.digital_milliet import DigitalMilliet
app = Flask('digital_milliet')
dm = DigitalMilliet(app, config_file="config.cfg")
app.run(debug=True, host="0.0.0.0", port=5000)

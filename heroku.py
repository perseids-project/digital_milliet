#!/usr/bin/env python
from flask import Flask
from digital_milliet.digital_milliet import DigitalMilliet
from digital_milliet.lib.configuration import Configuration

app = Flask('digital_milliet')
dm = DigitalMilliet(app, ['config.cfg'], [Configuration])

if __name__ == "__main__":
    app.run()

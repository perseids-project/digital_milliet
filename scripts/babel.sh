#!/bin/sh

pybabel extract -F babel.cfg -o digital_milliet/messages.pot .
pybabel update -i digital_milliet/messages.pot -d digital_milliet/translations
pybabel compile -d digital_milliet/translations

# -*- coding: utf-8 -*-
from __future__ import absolute_import
import logging
from logging.handlers import RotatingFileHandler

import pytimeparse
from flask import (Flask, flash, request, render_template, redirect,
                   url_for, abort)

from oniondoor.door import DoorController
from oniondoor.fritz import FritzWLAN

app = Flask(__name__, instance_relative_config=True)
app.config['LOG_FILE_LOCATION'] = '/var/log/oniondoor.log'

# Load a config file from instance/config.py containing the app
# secret key: SECRET_KEY='<SECRET_KEY>'
app.config.from_pyfile('config.py')

door = DoorController(app)


def main():

    # Configure log file
    file_handler = RotatingFileHandler(app.config['LOG_FILE_LOCATION'])
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(fmt="%(asctime)s "
                                                "[%(levelname)s]: "
                                                "%(message)s"))
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.DEBUG)

    app.logger.info("Starting OnionDoor")

    # Configure connection to the FritzBox
    if app.config.get('ENABLE_FRITZ'):
        try:
            app.fritz = FritzWLAN(password=app.config.get('FRITZ_PASSWORD', ''))
            app.logger.debug("%d devices associated to the WLAN.",
                             app.fritz.associated_devices)
        except KeyError:
            app.logger.exception("Error with FritzBox connection, is the password "
                                 "configured correctly?")

    app.run(use_reloader=False)


@app.route('/')
def index():
    """Index page for the door system"""
    if door.is_activated():
        return render_template('index.tpl',
                               activated=True,
                               active_until=door.active_until,
                               active_until_human=door.active_until.humanize())
    else:
        return render_template('index.tpl',
                               activated=False)


@app.route('/<key>')
def manual_open(key):
    """
    Endpoint for manually unlocking the door with the need to press the door button
    """
    if key == app.config.get("UNLOCK_ENDPOINT", "open"):
        door.unlock_door()
        flash("Unlocking the door", 'success')
        return redirect(url_for('index'))
    else:
        abort(404)


@app.route('/activate', methods=['POST'])
def activate():
    """Endpoint to activate the door system

    Activate door for two minutes is no argument is provided. Otherwise
    parse the provided time period and activate for that period of time.
    """

    time_period = request.form.get('time')
    time_seconds = pytimeparse.parse(str(time_period))

    if not time_seconds or time_seconds <= 0:
        time_seconds = 2 * 60  # Default activation period of 2 minutes
        flash(u'Invalid time period provided', 'danger')
    else:
        flash(u'Door activated!', 'success')

    door.activate(time_seconds=time_seconds)

    return redirect(url_for('index'))


@app.route('/deactivate', methods=['GET'])
def deactivate():
    """Endpoint to deactivate the door system"""
    door.deactivate()
    flash(u'Door deactivated!', 'success')
    return redirect(url_for('index'))


if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-
from __future__ import absolute_import
import logging
from logging.handlers import RotatingFileHandler

import pytimeparse
from flask import (Flask, flash, request, render_template, redirect,
                   url_for)

from oniondoor.door import DoorController
from oniondoor.fritz import FritzWLAN

app = Flask(__name__, instance_relative_config=True)
app.config['LOG_FILE_LOCATION'] = '/var/log/oniondoor.log'

# Load a config file from instance/config.py containing the app
# secret key: SECRET_KEY='<SECRET_KEY>'
app.config.from_pyfile('config.py')

door = DoorController(app)


def main():
    app.logger.info("Starting OnionDoor")

    # Configure log file
    file_handler = RotatingFileHandler(app.config['LOG_FILE_LOCATION'])
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(fmt="%(asctime)s "
                                                "[%(levelname)s]: "
                                                "%(message)s"))
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.DEBUG)

    # Configure connection to the FritzBox
    try:
        app.fritz = FritzWLAN(password=app.config.get('FRITZ_PASSWORD', ''))
        app.logger.debug("%d devices associated to the WLAN.",
                         app.fritz.associated_devices)
    except KeyError:
        app.logger.exception("Error with FritzBox connection, is the password "
                             "configured correctly?")

    app.run()


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


@app.route('/activate', methods=['GET'])
def activate():
    """Endpoint to activate the door system

    Activate door for two minutes is no argument is provided. Otherwise
    parse the provided time period and activate for that period of time.
    """

    time_period = request.args.get('time')
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

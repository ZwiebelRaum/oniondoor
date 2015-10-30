# -*- coding: utf-8 -*-
import time
import datetime
import arrow

import RPi.GPIO as GPIO


class DoorController(object):
    """Controller object to manage the door interface"""

    def __init__(self, app):
        """
        Configure the door controller and RPi GPIO pins for the door circuit
        """

        # Configure using the 'BOARD' pin numbers (the physical layout on
        # board). These pin numbers should be changed if a different board
        # model (not a Raspberry Pi 2) is used.
        self.app = app

        self.channel_in = 11
        self.channel_out = 13

        self.active_until = None

        self.unlocked = False
        self.unlocked_duration = 3  # Open door for 3 seconds

        GPIO.setmode(GPIO.BOARD)

        # Set input pin hign for pull-down signaling
        GPIO.setup(self.channel_in, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # Set output pin low for pull-up signaling
        GPIO.setup(self.channel_out, GPIO.OUT, initial=GPIO.LOW)
        GPIO.add_event_detect(self.channel_in, GPIO.FALLING,
                              callback=self.button_pressed, bouncetime=200)

    def activate(self, time_seconds=0):
        """Activate the door unlock mechanism for `time_period` seconds"""
        self.active_until = (arrow.now() +
                             datetime.timedelta(seconds=time_seconds))
        self.app.logger.debug("Door activated until {}".format(
                              self.active_until))

    def deactivate(self):
        """
        Deactivate the door unlock mechanism
        """
        self.active_until = None

    def is_activated(self):
        """
        Check if the door is in the active state. Deactivate it if the
        timer has expired.
        """
        if not self.active_until:
            return False

        else:
            time_remaining = self.active_until - arrow.now()
            if time_remaining.total_seconds() > 0:
                return True
            else:
                self.activate_until = False
                return False

    def button_pressed(self, channel):
        """Callback when the doorbell button is pressed"""
        if self.is_activated():
            self.app.logger.debug("Door button pressed when activated.")
            # Unlock door if it is not currently unlocked.
            if not self.unlocked:
                self.unlock_door()
        else:
            self.app.logger.debug("Door button pressed when not activated.")

    def unlock_door(self):
        """Send signal to unlock the door mechanism."""

        self.app.logger.debug("Unlocking the door")
        self.unlocked = True

        # Wait a "human" delay from button press to door unlocking.
        time.sleep(2)

        GPIO.output(self.channel_out, GPIO.HIGH)
        time.sleep(self.unlocked_duration)
        GPIO.output(self.channel_out, GPIO.LOW)

        self.unlocked = False

    def clean_up(self):
        GPIO.cleanup()

# -*- coding: utf-8 -*-
import time
import datetime
import arrow

import RPi.GPIO as GPIO


class SecretHandshake(object):
    """
    Track the current state of a buzzer "secret handshake" attempt.

    Holding the buzzer send a signal to the RPi approximately once every 5
    seconds. To unlock the door the button should be pressed once,
    then pressed again during the 3rd five second time period.

    Presses outside of this time period will reset the handshake state. This
    process should reduce the likelihood of someone accidentally opening the
    door by repeatedly pressing the buzzer.


    0 sec          5 sec          10 sec         15 sec         20 sec
    |**************|**************|--------------|**************|
    ^                             ^              ^
    Initial                        --- Active ---
    """

    # Handshake States
    START = 0
    WAITING = 1

    def __init__(self, app, action):
        """Action is the callable to run when the handshake is successful"""
        self.app = app
        self.activate = action
        self.event_time = 0
        self.state = self.START

    def shake_event(self):
        """Got a new shake event (e.g someone pressed the buzzer)"""

        if self.state == self.START:
            # After first event, go into the waiting state
            self.state = self.WAITING
            self.event_time = time.time()
            return None

        elif self.state == self.WAITING:
            # The second shake event should be in the 3 period (10-15 seconds)
            time_elapsed = time.time() - self.event_time
            if time_elapsed >= 10 and time_elapsed <= 15:
                self.app.logger.info('Successful handshake')
                self.activate()

            # Second shake event was outside the third period
            else:
                self.app.logger.debug('Failed handshake after %d seconds',
                                      time_elapsed)

            # Reset the handshake state now regardless of the outcome
            self.event_time = 0
            self.state = self.START
            return None


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

        # Object which tracks the progress of the "handshake"
        self.handshake = SecretHandshake(app, action=self.unlock_door)

        GPIO.setwarnings(False)
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

    def is_office_occupied(self):
        """Unlock if devices are associated on the WLAN"""
        if self.app.fritz.associated_devices > self.app.config.FRITZ_BASELINE:
            self.app.logger.debug("%d devices on the WLAN, opening!",
                                  self.app.fritz.associated_devices)
            return True
        else:
            return False

    def button_pressed(self, channel):
        """Callback when the doorbell button is pressed"""

        # If the door is activated, unlock immediately
        if self.is_activated() or self.is_office_occupied():
            self.app.logger.debug("Door button pressed when activated.")
            self.unlock_door()

        else:
            # Otherwise update the state of the handshake with this new event
            self.app.logger.debug("Door button pressed when not activated.")
            self.handshake.shake_event()

    def unlock_door(self):
        """Send signal to unlock the door mechanism."""

        # Unlock door if it is not currently unlocked.
        if not self.unlocked:
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

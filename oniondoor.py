# -*- coding: utf-8 -*-
import time

import RPi.GPIO as GPIO

# Configure using the 'BOARD' pin numbers (their physical layout on board)
# These pin numbers should be changed if a different board model is used.
CHANNEL_IN = 11
CHANNEL_OUT = 13

# PUSHES_REQUIRED = 3
# TIME_PERIOD = 15  # pushes in N seconds

DOOR_OPEN = False
DOOR_OPEN_DURATION = 3  # Open door for 3 seconds


def door_button_pressed(channel):
    """
    Callback when the doorbell button is pressed
    """

    # Check if door is already open
    print("Detected door button press")
    if not DOOR_OPEN:
        open_door()


def open_door():
    """
    Connect the door open switch and open the door.
    """
    global DOOR_OPEN

    # Open door
    print("Door openning")

    # Wait a "human" time period before pressing the button
    DOOR_OPEN = True
    time.sleep(2)
    GPIO.output(CHANNEL_OUT, GPIO.HIGH)

    time.sleep(DOOR_OPEN_DURATION)

    # Close door
    print("Door locked")
    GPIO.output(CHANNEL_OUT, GPIO.LOW)
    DOOR_OPEN = False


def main():
    """
    Configure the RPi GPIO pins for the door circuit
    """
    GPIO.setmode(GPIO.BOARD)

    # Set input pin hign for pull-down signaling
    GPIO.setup(CHANNEL_IN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # Set output pin low for pull-up signaling
    GPIO.setup(CHANNEL_OUT, GPIO.OUT, initial=GPIO.LOW)
    GPIO.add_event_detect(CHANNEL_IN, GPIO.FALLING,
                          callback=door_button_pressed, bouncetime=200)

    print("Entering waiting loop")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Door buzzer system shutting down")
        GPIO.cleanup()

if __name__ == '__main__':
    main()

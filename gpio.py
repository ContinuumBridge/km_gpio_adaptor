import RPi.GPIO as GPIO

SWITCH_GPIO = 18
PIR_GPIO = 17

class KitchenMinderInputs(object):
    def __init__(self):
        # Refer to pins as Broadcom SOC channel
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

    def setupSwitch(self, callback):
        GPIO.setup(SWITCH_GPIO, GPIO.IN)
        GPIO.add_event_detect(SWITCH_GPIO, GPIO.FALLING, callback=callback, bouncetime=300)

    def setupPIR(self, callback):
        GPIO.setup(PIR_GPIO, GPIO.IN)
        GPIO.add_event_detect(PIR_GPIO, GPIO.FALLING, callback=callback, bouncetime=300)

    def cleanup(self):
        GPIO.cleanup()

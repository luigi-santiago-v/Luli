from machine import Pin
import time
import Luli_CONFIG

class MotorAndLEDControl:
    def __init__(self, motor_pin=Luli_CONFIG.PIN_MOTOR, led_pin=Luli_CONFIG.PIN_LED):
        # Initialize motor and LED pins
        self.motor_gate = Pin(motor_pin, Pin.OUT)
        self.led_gate = Pin(led_pin, Pin.OUT)

    def motor_on(self):
        # Turn the motor on
        print("MOTOR ON")
        self.motor_gate.value(1)

    def motor_off(self):
        # Turn the motor off
        print("MOTOR OFF")
        self.motor_gate.value(0)

    def leds_on(self):
        # Turn the LED on
        print("LEDS ON")
        self.led_gate.value(1)

    def leds_off(self):
        # Turn the LED off
        print("LEDS OFF")
        self.led_gate.value(0)

# Testing the class functionality
if __name__ == "__main__":
    control = MotorAndLEDControl()

    # Testing Motor Control
    control.motor_off()
    control.leds_off()
    time.sleep(3)
    control.motor_on()
    time.sleep(45)
    control.motor_off()
    time.sleep(5)

    # Testing LED Control
    while True:
        control.led_on()
        time.sleep(1)
        control.led_off()
        time.sleep(1)


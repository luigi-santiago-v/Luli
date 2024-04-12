from machine import Pin
import time

# Setup the GPIO pin for the MOSFET gate control
mosfet_gate = Pin(22, Pin.OUT)

def led_on():
    # Setting the gate HIGH will turn on the MOSFET, completing the circuit
    print("LED ON")
    mosfet_gate.value(1)

def led_off():
    # Setting the gate LOW will turn off the MOSFET, breaking the circuit
    print("LED OFF")
    mosfet_gate.value(0)

# Main loop to turn LED on and off
while True:
    led_on()
    time.sleep(1)  # LED is on for 1 second
    led_off()
    time.sleep(1)  # LED is off for 1 second


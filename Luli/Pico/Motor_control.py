from machine import Pin
import time

# Setup the GPIO pin for the MOSFET gate control
mosfet_gate = Pin(21, Pin.OUT)

def motor_on():
    # Setting the gate HIGH will turn on the MOSFET, completing the circuit
    print("MOTOR ON")
    mosfet_gate.value(1)

def motor_off():
    # Setting the gate LOW will turn off the MOSFET, breaking the circuit
    print("MOTOR OFF")
    mosfet_gate.value(0)

# Main loop to turn motor on and off
while True:
    motor_on()
    time.sleep(5)  # motor is on for 5 seconds
    motor_off()
    time.sleep(5)  # motor is off for 5 seconds



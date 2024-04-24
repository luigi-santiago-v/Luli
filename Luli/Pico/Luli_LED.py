from machine import Pin
import time

# Setup the GPIO pin for the MOSFET gate control


def on(mosfet_gate = Pin(22, Pin.OUT)):
    # Setting the gate HIGH will turn on the MOSFET, completing the circuit
    print("LED ON")
    mosfet_gate.value(1)

def off(mosfet_gate = Pin(22, Pin.OUT)):
    # Setting the gate LOW will turn off the MOSFET, breaking the circuit
    print("LED OFF")
    mosfet_gate.value(0)

if __name__ == "__main__":
    # Main loop to turn LED on and off
    while True:
        on()
        time.sleep(1)  # LED is on for 1 second
        off()
        time.sleep(1)  # LED is off for 1 second


from machine import Pin
import time

def on(mosfet_gate = Pin(21, Pin.OUT)):
    # Setting the gate HIGH will turn on the MOSFET, completing the circuit
    print("MOTOR ON")
    mosfet_gate.value(1)

def off(mosfet_gate = Pin(21, Pin.OUT)):
    # Setting the gate LOW will turn off the MOSFET, breaking the circuit
    print("MOTOR OFF")
    mosfet_gate.value(0)


if __name__ == "__main__":
    # Main loop to turn motor on and off
    while True:
        off()
        time.sleep(3)
        on()
        time.sleep(45)  # motor is on for 5 seconds
        off()
        time.sleep(5)  # motor is off for 5 seconds



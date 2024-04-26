from machine import Pin, ADC
import time

# Setup the data pin
data_pin = ADC(Pin(28))  # Assuming GPIO0 is set up as ADC for voltage reading

# Setup select pins
sA = Pin(2, Pin.OUT)
sB = Pin(3, Pin.OUT)
sC = Pin(4, Pin.OUT)

def select_input(a, b, c):
    """Set the select pins based on the desired input"""
    sA.value(a)
    sB.value(b)
    sC.value(c)

def read_voltage():
    """Read and return the voltage from the ADC connected to the MUX output"""
    voltage = data_pin.read_u16() * 3.3 / 65535  # Convert ADC reading to voltage (3.3V reference)
    return voltage


while True:
    # Test the MUX by selecting different inputs and printing the read voltage
    for input_number in range(3):  # Test for D0, D1, and D2
        select_input((input_number & 0x4) >> 2, (input_number & 0x2) >> 1, input_number & 0x1)
        time.sleep(1)  # Wait a bit for MUX to stabilize and ADC to settle
        voltage = read_voltage()
        print(f"Input {input_number}: Voltage = {voltage:.2f} V")


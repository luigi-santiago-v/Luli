from machine import Pin
import Luli.Pico.Luli_DHT as Luli_DHT
import time

# Initialize the GPIO pins for MUX control
s0 = Pin(18, Pin.OUT)
s1 = Pin(19, Pin.OUT)
s2 = Pin(20, Pin.OUT)
g_not = Pin(2, Pin.OUT)  # G_NOT strobe pin
data_pin = Pin(16, Pin.IN, Pin.PULL_UP)  # Data pin connected to MUX output
measure_all_pin = Luli_DHT.DHT22(Pin(3,Pin.OUT,Pin.PULL_UP)) # Pin used to send measure() signal


def select_input(n):
    """ Set the select pins and enable MUX output based on the desired input n (0 to 7) """
    lsb = n & 0x01
    mid = (n & 0x02) >> 1
    msb = (n & 0x04) >> 2
    
    s0.value(lsb)  # LSB
    s1.value(mid)
    s2.value(msb)
    g_not.value(0)  # Enable MUX output by setting G_NOT low
    print(f"select {n} via {msb}{mid}{lsb}")
    time.sleep(1)  # Wait for MUX and sensor to stabilize

def disable_mux_output():
    """ Disable MUX output by setting G_NOT high """
    g_not.value(1)

def read_sensor(data_pin):
    """ Initialize sensor on specified pin and read temperature and humidity """
    sensor = Luli_DHT.DHT22(data_pin)
    time.sleep(2)
    try:
        sensor.measure()
        temp = sensor.temperature()
        hum = sensor.humidity()
        return temp, hum
    except OSError as e:
        print(f"Error reading sensor:", e)
        return -1, -1

# Example of cycling through the first four sensors and reading data
while True:
    for i in range(4):
        select_input(i)
        temperature, humidity = read_sensor(data_pin)
        if temperature == -1 and humidity == -1:
            print("Failed to read from sensor", i)
        else:
            print("Sensor", i, "Temperature:", temperature, "Humidity:", humidity)
        #disable_mux_output()  # Disable the MUX output
        time.sleep(1)  # Optional: Pause between sensor switches for debugging

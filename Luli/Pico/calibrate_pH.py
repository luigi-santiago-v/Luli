from machine import ADC, Pin
import utime

# Constants based on sensor characteristics
VOLTAGE_AT_PH7 = 2.51  # Voltage at pH 7
VOLTAGE_AT_PH4 = 3.03  # Voltage at pH 4
PH_STEP = (VOLTAGE_AT_PH7 - VOLTAGE_AT_PH4) / (7 - 4)  # Voltage change per pH unit

# Initialize the ADC (0-3.3V range on the Pico)
adc = ADC(Pin(26))  # ADC0 corresponds to GPIO26

# Function to read and average the sensor value
def read_sensor():
    buf = []
    for _ in range(10):
        adc_value = adc.read_u16()
        buf.append(adc_value)
        utime.sleep_ms(50)  # Adjusted to match the sensor's response time
    # Sort buffer and remove the lowest and highest readings
    buf.sort()
    avg_adc_value = sum(buf[1:-1]) / (len(buf) - 2)
    return avg_adc_value

# Function to convert ADC value to pH level
def adc_to_ph(adc_value):
    # Convert ADC value to voltage
    voltage = adc_value * (3.3 / 65535)
    # Calculate pH value based on the sensor's characteristics
    ph_value = 7 + (VOLTAGE_AT_PH7 - voltage) / PH_STEP
    return ph_value

# Main loop
while True:
    # Read the average sensor value
    avg_adc_value = read_sensor()
    # Convert ADC value to pH
    ph = adc_to_ph(avg_adc_value)
    print("Sensor =", ph)
    utime.sleep(2)  # Settling time of the sensor is considered in the delay


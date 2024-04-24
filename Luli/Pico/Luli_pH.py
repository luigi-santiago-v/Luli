from machine import ADC, Pin
import utime

class PHSensor:
    # Constants for pH calculation
    VOLTAGE_AT_PH7 = 2.51  # Voltage at pH 7
    VOLTAGE_AT_PH4 = 3.03  # Voltage at pH 4
    PH_STEP = (VOLTAGE_AT_PH7 - VOLTAGE_AT_PH4) / (7 - 4)  # Voltage change per pH unit

    def __init__(self, pin_number=26):
        self.adc = ADC(Pin(pin_number))  # Initialize ADC on specified pin

    def read_sensor(self):
        buf = []
        for _ in range(10):
            adc_value = self.adc.read_u16()
            buf.append(adc_value)
            utime.sleep_ms(50)  # Sleep to match sensor response time
        buf.sort()
        avg_adc_value = sum(buf[1:-1]) / (len(buf) - 2)  # Calculate average excluding outliers
        return avg_adc_value

    def adc_to_ph(self, adc_value):
        voltage = adc_value * (3.3 / 65535)  # Convert ADC value to voltage
        ph_value = 7 + (self.VOLTAGE_AT_PH7 - voltage) / self.PH_STEP  # Calculate pH
        return ph_value

    def get_ph(self):
        avg_adc_value = self.read_sensor()
        return self.adc_to_ph(avg_adc_value)

def main():
    ph_sensor = PHSensor()
    while True:
        ph = ph_sensor.get_ph()
        print("Sensor pH level =", ph)
        utime.sleep(2)

if __name__ == "__main__":
    main()

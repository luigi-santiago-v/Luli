import machine
import utime
import Luli_CONFIG

class WaterLevelSensor:
    def __init__(self, trig_pin=Luli_CONFIG.PIN_ULTRASONIC_TRIG, echo_pin=Luli_CONFIG.PIN_ULTRASONIC_ECHO):
        self.trig = machine.Pin(trig_pin, machine.Pin.OUT)
        self.echo = machine.Pin(echo_pin, machine.Pin.IN)
        self.tank_full_distance = 3
        self.tank_empty_distance = Luli_CONFIG.TANK_EMPTY_DISTANCE

    def read_distance(self):
        self.trig.low()
        utime.sleep_us(5)

        self.trig.high()
        utime.sleep_us(10)
        self.trig.low()

        timeout = 10000  # Timeout in microseconds

        start_time = utime.ticks_us()
        while self.echo.value() == 0:
            if utime.ticks_diff(utime.ticks_us(), start_time) > timeout:
                return None  # Timeout with no echo received

        signal_off = utime.ticks_us()

        start_time = utime.ticks_us()
        while self.echo.value() == 1:
            if utime.ticks_diff(utime.ticks_us(), start_time) > timeout:
                return None  # Timeout while echo is still high

        signal_on = utime.ticks_us()

        time_passed = utime.ticks_diff(signal_on, signal_off)
        distance = (time_passed * 0.0343) / 2  # Convert time to distance
        return distance

    def calibrate_tank_full(self):
        print("Calibrating tank full... Please ensure the tank is full.")
        utime.sleep(5)
        self.tank_full_distance = self.read_distance()
        if self.tank_full_distance is not None:
            print("Tank full distance calibrated at:", self.tank_full_distance, "cm")
        else:
            print("Calibration failed. Make sure the tank is full and try again.")

    def calibrate_tank_empty(self):
        print("Calibrating tank empty... Please ensure the tank is empty.")
        utime.sleep(5)
        self.tank_empty_distance = self.read_distance()
        if self.tank_empty_distance is not None:
            print("Tank empty distance calibrated at:", self.tank_empty_distance, "cm")
        else:
            print("Calibration failed. Make sure the tank is empty and try again.")

    def display_water_level(self):
        distance = self.read_distance()
        if distance is not None and distance > 2:
            if self.tank_full_distance is not None and self.tank_empty_distance is not None:
                water_level = self.tank_empty_distance - distance
                tank_capacity = self.tank_empty_distance - self.tank_full_distance
                percent_full = (water_level / tank_capacity) * 100
                print("Water level:", round(percent_full, 2), "% full")
            else:
                print("Tank 'full' or 'empty' distance not calibrated.")
        else:
            print("Out of range, too close, or sensor error.")

    def get_water_level(self):
        distance = self.read_distance()
        if distance is not None:
            if self.tank_full_distance is not None and self.tank_empty_distance is not None:
                # Calculate the current water level above the sensor
                water_level = distance - self.tank_full_distance
                # Calculate the total possible water level (empty minus full)
                tank_capacity = self.tank_empty_distance - self.tank_full_distance
                # Calculate the percentage of water left in the tank
                percent_full = ((tank_capacity - water_level) / tank_capacity) * 100
                return round(percent_full, 2)
            else:
                print("Tank calibration not set.")
                return None
        else:
            print("Sensor error or out of range.")
            return None

def main():
    sensor = WaterLevelSensor()
    # Uncomment to calibrate on startup
    # sensor.calibrate_tank_full()
    # sensor.calibrate_tank_empty()

    while True:
        sensor.display_water_level()
        utime.sleep(1)

if __name__ == "__main__":
    main()

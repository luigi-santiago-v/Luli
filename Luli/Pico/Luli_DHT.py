import Luli.Pico.Luli_DHT as Luli_DHT
from machine import Pin
import time

class DHT22Handler:
    def __init__(self):
        # Initialize all DHT22 sensors on their respective pins
        self.sensors = [
            Luli_DHT.DHT22(Pin(6, Pin.IN, Pin.PULL_DOWN)),
            Luli_DHT.DHT22(Pin(7, Pin.IN, Pin.PULL_DOWN)),
            Luli_DHT.DHT22(Pin(8, Pin.IN, Pin.PULL_DOWN)),
            Luli_DHT.DHT22(Pin(9, Pin.IN, Pin.PULL_DOWN))
        ]

    def measure_all(self):
        # Attempt to measure from all sensors up to three times
        retry = 0
        while retry < 3:
            try:
                for sensor in self.sensors:
                    sensor.measure()
                return True
            except Exception as e:
                print(".", end="")
                retry += 1
                time.sleep(0.5)
        return False

    def get_temperature(self, sensor_index):
        # Return the temperature from the specified sensor
        if self.measure_all():
            return self.sensors[sensor_index].temperature()
        else:
            print("Failed to read temperature after several attempts.")
            return None

    def get_humidity(self, sensor_index):
        # Return the humidity from the specified sensor
        if self.measure_all():
            return self.sensors[sensor_index].humidity()
        else:
            print("Failed to read humidity after several attempts.")
            return None

def main():
    dht_handler = DHT22Handler()
    while True:
        print("Measuring.")
        for i in range(4):
            temp = dht_handler.get_temperature(i)
            hum = dht_handler.get_humidity(i)
            if temp is not None and hum is not None:
                print(f"Sensor {i}: Temperature: {temp} °C, Humidity: {hum} %")
        time.sleep(3)

if __name__ == "__main__":
    main()

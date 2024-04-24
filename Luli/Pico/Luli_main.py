import machine
import Luli_Motor
import Luli_LED
from Luli_UV import LTR390
from Luli_Ultrasonic import WaterLevelSensor
from Luli_pH import PHSensor
from Luli_OLED import OLEDMenuDisplay
from Luli_DHT import DHT22Handler
import utime


# Motor and LED Control Circuit
MOTOR_PIN = machine.Pin(21, machine.Pin.OUT)
LED_PIN = machine.Pin(22, machine.Pin.OUT)
MOTOR = Luli_Motor
LEDS = Luli_LED()

# Sensor Initialization
PH_SENSOR = PHSensor()
UV_SENSOR = LTR390()
TANK_SENSOR = WaterLevelSensor()
DHTS = DHT22Handler()

# External Hardware/Misc Initialization
OLED = OLEDMenuDisplay()
SOLUTION = 'Half'

def sensor_uv_read():
    # Give the sensor some time to start
    utime.sleep(1)
    uv_data = UV_SENSOR.read_uvs()
    print("UVS data: {}".format(uv_data))
    return uv_data

def sensor_ph_read():
    ph_level = PH_SENSOR.get_ph()
    print("Current pH level:", ph_level)

#def sensor_tank_calibrate():
#    TANK_SENSOR.calibrate_tank_full()
#    TANK_SENSOR.calibrate_tank_empty()

def sensor_tank_read():
    return TANK_SENSOR.get_water_level()
    

def sensor_temp_read():
    # Compute average temp of sensors 0 to 3
    total_temp = 0
    for i in range(4):
        # Average and convert to Fahrenheit
        total_temp += ((DHTS.get_temperature(i) * 9/5) + 32)
    avg_temp = total_temp / 4
    print("Average temperature:", avg_temp)
    return avg_temp

def sensor_humidity_read():
    # Compute average humidity of sensors 0 to 3
    total_hum = 0
    for i in range(4):
        total_hum += DHTS.get_humidity(i)
    avg_hum = total_hum / 4
    print("Average humidity:", avg_hum)
    return avg_hum

def update_display(plant_name='Lettuce', planted_date='3/15/24', harvest_date='5/10/24'):
    OLED.print_sensor_data(ph=PH_SENSOR.get_ph(), temp=sensor_temp_read(), light=sensor_uv_read(), humidity=sensor_humidity_read(), solution=SOLUTION)
    utime.sleep(5)
    OLED.print_plant_menu(plant_name=plant_name, planted_date=planted_date, harvest_date=harvest_date)
    utime.sleep(5)

def motor_on():
    Luli_Motor.motor_on(MOTOR_PIN)

def motor_off():
    Luli_Motor.motor_off(MOTOR_PIN)

def LEDS_on():
    LEDS.on(LED_PIN)

def LEDS_off():
    LEDS.off(LED_PIN)


if __name__ == '__main__':
    motor_off()
    LEDS_off()

    utime.sleep(3) # 3 Second startup delay

    motor_on()
    LEDS_on()
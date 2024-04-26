import machine
#import Luli.Pico.test.Luli_Motor as Luli_Motor
#import Luli.Pico.test.Luli_LED as Luli_LED
from Luli_UV import LTR390
from Luli_Ultrasonic import WaterLevelSensor
from Luli_pH import PHSensor
from Luli_OLED import OLEDMenuDisplay
from Luli_DHT import DHT22Handler
from Luli_Networkhandler import NetworkHandler
from Luli_MotorLEDControl import MotorAndLEDControl
import Luli_CONFIG
import utime

MOTOR_LED_CONTROL = MotorAndLEDControl()

# Sensor Initialization
PH_SENSOR = PHSensor()
UV_SENSOR = LTR390()
TANK_SENSOR = WaterLevelSensor()
DHTS = DHT22Handler()


# External Hardware/Misc Initialization
OLED = OLEDMenuDisplay()
NETWORK = NetworkHandler(Luli_CONFIG.WIFI_SSID, Luli_CONFIG.WIFI_PASSWORD, Luli_CONFIG.SERVER_URL)

def log_error(e):
    with open('error_log.txt', 'a') as file:  # 'a' opens the file for appending
        timestamp = utime.localtime()  # Get the current time
        readable_timestamp = "{year}/{month}/{day} {hours}:{minutes}:{seconds}".format(
            year=timestamp[0], month=timestamp[1], day=timestamp[2],
            hours=timestamp[3], minutes=timestamp[4], seconds=timestamp[5]
        )
        file.write('{} - Error: {}\n'.format(readable_timestamp, e))

def sensor_uv_read():
    # Give the sensor some time to start
    utime.sleep(Luli_CONFIG.DELAY_UV_STARTUP)
    raw, uv_index = UV_SENSOR.get_uv_data()
    print("RAW: {}".format(raw))
    print("UV Index: {}".format(uv_index))
    #return raw, uv_index
    return uv_index

def sensor_ph_read():
    ph_level = PH_SENSOR.get_ph()
    print("Current pH level:", ph_level)
    return ph_level

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

def update_display(plant_name='Lettuce', planted_date='3/15/24', harvest_date='5/10/24', ph_param=None, temp_param=None, light_param=None, humidity_param=None, tank_param=None):
    ph = ph_param if ph_param is not None else sensor_ph_read()
    temp = temp_param if temp_param is not None else sensor_temp_read()
    light = light_param if light_param is not None else sensor_uv_read()
    humidity = humidity_param if humidity_param is not None else sensor_humidity_read()
    tank = tank_param if tank_param is not None else sensor_tank_read()

    OLED.print_sensor_data(ph=ph, temp=temp, light=light, humidity=humidity, tank=tank)
    utime.sleep(Luli_CONFIG.DELAY_OLED)
    OLED.print_plant_menu(plant_name=plant_name, planted_date=planted_date, harvest_date=harvest_date)
    utime.sleep(Luli_CONFIG.DELAY_OLED)

def send_all_data(ph_param=None, temp_param=None, light_param=None, humidity_param=None, tank_param=None):
    ph = ph_param if ph_param is not None else sensor_ph_read()
    temp = temp_param if temp_param is not None else sensor_temp_read()
    light = light_param if light_param is not None else sensor_uv_read()
    humidity = humidity_param if humidity_param is not None else sensor_humidity_read()
    tank = tank_param if tank_param is not None else sensor_tank_read()


    data = {
        "ph": ph,
        "temp": temp,
        "light": light,
        "humidity": humidity,
        "tank": tank
    }

    response = NETWORK.send_data(Luli_CONFIG.ENDPOINT_UPDATE_ALL_SENSOR_DATA, data)
    return response

def send_data(data, data_label):
    response = None
    match data_label:
        case 'ph':
            response = NETWORK.send_data(Luli_CONFIG.ENDPOINT_UPDATE_PH_DATA, data)
        case 'temp':
            response = NETWORK.send_data(Luli_CONFIG.ENDPOINT_UPDATE_TEMP_DATA, data)
        case 'light':
            response = NETWORK.send_data(Luli_CONFIG.ENDPOINT_UPDATE_UV_DATA, data)
        case 'humidity':
            response = NETWORK.send_data(Luli_CONFIG.ENDPOINT_UPDATE_HUMIDITY_DATA, data)
        case 'tank':
            response = NETWORK.send_data(Luli_CONFIG.ENDPOINT_UPDATE_TANK_DATA, data)
        case _:
            print("Invalid data label")

    # if response was successful, return True
    if response.status_code == 200:
        return True
    else:
        return False



if __name__ == '__main__':
    # Projects Day Demo Timings
    # 1. Read UV Sensor Data every 2 minutes
    # 2. Read pH Sensor Data and tank level data after every water pump cycle
    # 3. Read Temperature and Humidity every 30 seconds


    #NETWORK.connect_wifi('Liam', 'liampassword', 'http://'
    MOTOR_LED_CONTROL.motor_off()
    MOTOR_LED_CONTROL.leds_on()

    try:
        # Start time
        start_time = utime.time()
        next_uv_time = start_time + Luli_CONFIG.UV_READ_INTERVAL
        next_temp_humidity_time = start_time + Luli_CONFIG.TEMP_HUMIDITY_READ_INTERVAL
        next_motor_start_time = start_time # Start motor on startup
        next_motor_stop_time = start_time + Luli_CONFIG.DURATION_WATER_CYCLE
        
        temperature = None
        humidity = None
        ph = None
        tank = None
        uv = None

        # Assumes tank is full on startup
        TANK_SENSOR.calibrate_tank_full()

        while True:
            current_time = utime.time()

            # Read UV and update display every 120 seconds
            if current_time >= next_uv_time:
                uv = sensor_uv_read()
                update_display()
                try:
                    send_data(uv, 'light')
                except Exception as e:
                    print("Error sending UV data:", e)
                next_uv_time = current_time + Luli_CONFIG.UV_READ_INTERVAL  # Schedule next run

            # Read Temperature and Humidity every 30 seconds
            if current_time >= next_temp_humidity_time:
                temperature = sensor_temp_read()
                humidity = sensor_humidity_read()
                update_display()
                try:
                    send_data(temperature, 'temp')
                    send_data(humidity, 'humidity')
                except Exception as e:
                    print("Error sending temp/humidity data:", e)
                next_temp_humidity_time = current_time + Luli_CONFIG.TEMP_HUMIDITY_READ_INTERVAL # Schedule next run

            # Start Water Cycle that reads pH and tank level
            if current_time >= next_motor_start_time:
                tank_level_percent = sensor_tank_read()  # Get the current water level percentage
                if tank_level_percent is not None and tank_level_percent > Luli_CONFIG.MINIMUM_WATER_LEVEL:
                    MOTOR_LED_CONTROL.motor_on()
                    next_motor_stop_time = current_time + Luli_CONFIG.DURATION_WATER_CYCLE  # Schedule to stop in 10 minutes
                else:
                    print("Water level too low to start pump")
                    #next_motor_start_time = current_time + Luli_CONFIG.CHECK_WATER_LEVEL_INTERVAL  # Check again after some time
                    
            if current_time >= next_motor_stop_time:
                MOTOR_LED_CONTROL.motor_off()
                ph = sensor_ph_read()
                tank = sensor_tank_read()  # Read again after pump off in case level has changed
                update_display(ph=ph, tank=tank)
                try:
                    send_data(ph, 'ph')
                    send_data(tank, 'tank')
                except Exception as e:
                    print("Error sending pH/tank data:", e)
                next_motor_start_time = current_time + Luli_CONFIG.NEXT_WATER_CYCLE  # Schedule next cycle
            

            utime.sleep(0.1)  # Sleep for 100ms to reduce CPU usage

    except Exception as e:
        # Log the error
        log_error(e)
        print("Error:", e)
        MOTOR_LED_CONTROL.motor_off()
        for _ in range(10):
            MOTOR_LED_CONTROL.leds_off()
            utime.sleep(0.5)
            MOTOR_LED_CONTROL.leds_on()
            utime.sleep(0.5)
        MOTOR_LED_CONTROL.leds_off()
        machine.reset() # Reset the board if an error occurs
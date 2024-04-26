
from Luli_UV import LTR390
from Luli_Ultrasonic import WaterLevelSensor
from Luli_pH import PHSensor
from Luli_OLED import OLEDMenuDisplay
from Luli_DHT import DHT22Handler
from Luli_Networkhandler import NetworkHandler
from Luli_MotorLEDControl import MotorAndLEDControl
import machine
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
    raw, uv_intensity = UV_SENSOR.get_uv_data()
    print("RAW: {}".format(raw))
    print("UV Intensity: {}µW/cm²".format(uv_intensity))
    #return raw, uv_intensity
    return uv_intensity

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
        temp = DHTS.get_temperature(i)
        num_DHTs = 4
        if temp is not None:
            total_temp += ((temp * 9/5) + 32)
        else:
            total_temp += 0
            num_DHTs = num_DHTs - 1
    if num_DHTs <= 1:
        num_DHTs = 1
    avg_temp = total_temp / num_DHTs
    print("Average temperature:", avg_temp)
    return avg_temp

def sensor_humidity_read():
    # Compute average humidity of sensors 0 to 3
    total_hum = 0
    num_DHTs = 4
    for i in range(4):
        hum = DHTS.get_humidity(i)
        if hum is not None:
            total_hum += DHTS.get_humidity(i)
            
        else:
            total_hum += 0
            num_DHTs = num_DHTs - 1
    if num_DHTs <= 1:
        num_DHTs = 1
    avg_hum = total_hum / num_DHTs
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
    try:
        response = NETWORK.send_data(Luli_CONFIG.ENDPOINT_UPDATE_ALL_SENSOR_DATA, data)
    except Exception as e:
        print("Error sending all sensor data:", e)
        #log_error(e)
    return response

def send_data(data, data_label):
    response = None
    
    if data_label == 'ph':
        try:
            response = NETWORK.send_data(Luli_CONFIG.ENDPOINT_UPDATE_PH_DATA, data)
        except Exception as e:
            print("Error sending pH data:", e)
            #log_error(e)
    elif data_label == 'temp':
        try:
            response = NETWORK.send_data(Luli_CONFIG.ENDPOINT_UPDATE_TEMP_DATA, data)
        except Exception as e:
            print("Error sending temperature data:", e)
            #log_error(e)
    elif data_label == 'light':
        try:
            response = NETWORK.send_data(Luli_CONFIG.ENDPOINT_UPDATE_UV_DATA, data)
        except Exception as e:
            print("Error sending UV data:", e)
            #log_error(e)
    elif data_label == 'humidity':
        try:
            response = NETWORK.send_data(Luli_CONFIG.ENDPOINT_UPDATE_HUMIDITY_DATA, data)
        except Exception as e:
            print("Error sending humidity data:", e)
            #log_error(e)
    elif data_label == 'tank':
        try:
            response = NETWORK.send_data(Luli_CONFIG.ENDPOINT_UPDATE_TANK_DATA, data)
        except Exception as e:
            print("Error sending tank data:", e)
            #log_error(e)
    else:
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


    MOTOR_LED_CONTROL.motor_off()
    MOTOR_LED_CONTROL.leds_on()

    try:
        # Start time
        start_time = utime.time()
        next_uv_time = start_time + Luli_CONFIG.UV_READ_INTERVAL
        next_temp_humidity_time = start_time + Luli_CONFIG.TEMP_HUMIDITY_READ_INTERVAL
        next_motor_start_time = start_time # Start motor on startup
        next_motor_stop_time = start_time + Luli_CONFIG.DURATION_WATER_CYCLE
        next_manual_override_check_time = utime.time() + Luli_CONFIG.MANUAL_OVERRIDE_CHECK_INTERVAL  # Setting up the next time to check for manual overrides

        
        temperature = None
        humidity = None
        ph = None
        tank = None
        uv = None

        # Assumes tank is full on startup
        TANK_SENSOR.calibrate_tank_full()

        while True:

            current_time = utime.time()
            
            
            # Start Water Cycle that reads pH and tank level
            if current_time >= next_motor_start_time:
                tank_level_percent = sensor_tank_read()  # Get the current water level percentage
                if tank_level_percent is not None and tank_level_percent > Luli_CONFIG.MINIMUM_WATER_LEVEL:
                    MOTOR_LED_CONTROL.motor_on()
                    next_motor_stop_time = current_time + Luli_CONFIG.DURATION_WATER_CYCLE  # Schedule to stop
                    next_motor_start_time = next_motor_stop_time + Luli_CONFIG.NEXT_WATER_CYCLE
                else:
                    print("Water level too low to start pump")
                    #next_motor_start_time = current_time + Luli_CONFIG.CHECK_WATER_LEVEL_INTERVAL  # Check again after some time
                    
            #print("CURRENT: ", current_time)
            #print("SToP TIME: ", next_motor_stop_time)
            if current_time >= next_motor_stop_time:
                MOTOR_LED_CONTROL.motor_off()
                print("MOTOR SHOULD BE OFF")
                ph = sensor_ph_read()
                tank = sensor_tank_read()  # Read again after pump off in case level has changed
                update_display(ph_param=ph, tank_param=tank)
                try:
                    send_data(ph, 'ph')
                    send_data(tank, 'tank')
                except Exception as e:
                    print("Error sending pH/tank data:", e)
                next_motor_start_time = current_time + Luli_CONFIG.NEXT_WATER_CYCLE  # Schedule next cycle

            # Check for manual override every 30 seconds
            if current_time >= next_manual_override_check_time:
                try:
                    # Check for manual override
                    override_commands = NETWORK.get_manual_override()
                    if override_commands:
                        print("Manual override commands received:", override_commands)
                        if 'motor' in override_commands:
                            if override_commands['motor'] == 'on':
                                MOTOR_LED_CONTROL.motor_on()
                            elif override_commands['motor'] == 'off':
                                MOTOR_LED_CONTROL.motor_off()
                        if 'leds' in override_commands:
                            if override_commands['leds'] == 'on':
                                MOTOR_LED_CONTROL.leds_on()
                            elif override_commands['leds'] == 'off':
                                MOTOR_LED_CONTROL.leds_off()
                        if 'read_light' in override_commands:
                            uv = sensor_uv_read()
                            update_display()
                            send_data(uv, 'light')
                        if 'read_temp' in override_commands:
                            temperature = sensor_temp_read()
                            update_display()
                            send_data(temperature, 'temp')
                        if 'read_humidity' in override_commands:
                            humidity = sensor_humidity_read()
                            update_display()
                            send_data(humidity, 'humidity')
                        if 'read_ph' in override_commands:
                            ph = sensor_ph_read()
                            update_display(ph_param=ph)
                            send_data(ph, 'ph')
                        if 'read_tank' in override_commands:
                            tank = sensor_tank_read()
                            update_display(tank_param=tank)
                            send_data(tank, 'tank')
                except Exception as e:
                    print("Error getting manual override:", e)
                    #log_error(e)
                
                # Update the next check time for manual overrides
                next_manual_override_check_time = current_time + Luli_CONFIG.MANUAL_OVERRIDE_CHECK_INTERVAL
            

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

            
            

            utime.sleep(0.1)  # Sleep for 100ms to reduce CPU usage

    except Exception as e:
        # SHUTDOWN ERROR CODE
        # Log the error
        log_error(e)
        print("Error:", e)
        MOTOR_LED_CONTROL.motor_off()
        for _ in range(3):
            MOTOR_LED_CONTROL.leds_off()
            utime.sleep(0.5)
            MOTOR_LED_CONTROL.leds_on()
            utime.sleep(0.5)
        MOTOR_LED_CONTROL.leds_off()
        #machine.reset() # Reset the board if an error occurs

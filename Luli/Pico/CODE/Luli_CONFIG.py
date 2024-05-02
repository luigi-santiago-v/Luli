# Luli Hydroponics Config File
# This file will define all necessary pins and timing constants for the Luli Hydroponics system

#####################
#   PIN SETTINGS    #
#####################
PIN_UV_SENSOR_SDA = 0
PIN_UV_SENSOR_SCL = 1

PIN_OLED_SCK = 14
PIN_OLED_MOSI = 11 
PIN_OLED_CS = 13 # marked
PIN_OLED_RST = 10 
PIN_OLED_DC = 15 

PIN_ULTRASONIC_ECHO = 9
PIN_ULTRASONIC_TRIG = 17

PIN_DHT0 = 16
PIN_DHT1 = 18
PIN_DHT2 = 19
PIN_DHT3 = 20

PIN_MOTOR = 21
PIN_LED = 22
PIN_PH_SENSOR = 26




#########################
#   TIMING CONSTANTS    #
#########################
DELAY_OLED = 5 # seconds
DELAY_PH_RESPONSE = 50 # ms
DELAY_UV_STARTUP = 1 # seconds

TEMP_HUMIDITY_READ_INTERVAL = 30 # seconds
UV_READ_INTERVAL = 120 # seconds
MANUAL_OVERRIDE_CHECK_INTERVAL = 30 # seconds
#DURATION_WATER_CYCLE = 600 # seconds
DURATION_WATER_CYCLE = 60
NEXT_WATER_CYCLE = 3600 # seconds
DURATION_LED_CYCLE = 3600 # seconds



#########################
#   NETWORK SETTINGS    #
#########################
WIFI_SSID = 'Liam'
WIFI_PASSWORD = 'liampassword'
#WIFI_PASSWORD = None
SERVER_URL = 'https://lulihydroponics.ddns.net'



#########################
#   ENDPOINT SETTINGS   #
#########################
ENDPOINT_TEST = '/api/test'
ENDPOINT_GET_SETTINGS = '/api/get_settings'
ENDPOINT_SET_HARDWARE_ID = '/api/set_hardware_id'
ENDPOINT_UPDATE_SETTINGS = '/api/update_settings'
ENDPOINT_UPDATE_UV_DATA = '/api/update_uv_data'
ENDPOINT_UPDATE_PH_DATA = '/api/update_ph_data'
ENDPOINT_UPDATE_TEMP_DATA = '/api/update_temp_data'
ENDPOINT_UPDATE_HUMIDITY_DATA = '/api/update_humidity_data'
ENDPOINT_UPDATE_TANK_DATA = '/api/update_tank_data'
ENDPOINT_UPDATE_ALL_SENSOR_DATA = '/api/update_all_sensor_data'
ENDPOINT_MANUAL_OVERRIDE = '/api/get_manual_override'


######################
#   MISC CONSTANTS   #
######################
# https://optoelectronics.liteon.com/upload/download/DS86-2015-0004/LTR-390UV_Final_%20DS_V1%201.pdf
UVS_CONVERSION_FACTOR = 2300 # Conversion factor from the datasheet
VOLTAGE_AT_PH7 = 2.51
VOLTAGE_AT_PH4 = 3.03
MINIMUM_WATER_LEVEL = 20 # Minimum water level in the tank in percentage (%)
TANK_EMPTY_DISTANCE = 12 # Distance in cm when the tank is empty
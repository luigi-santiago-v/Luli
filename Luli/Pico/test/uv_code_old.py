from machine import Pin, I2C

# Set MUX select pins
selA = Pin(20, Pin.OUT)    # MUX Select A
selB = Pin(19, Pin.OUT)    # MUX Select B
selC = Pin(18, Pin.OUT)    # MUX Select C

muxData = Pin(15, Pin.IN)  # MUX Y Connection (Data Out)

####################
# UV I2C CONSTANTS #
####################
# Initialize I2C
# On the Raspberry Pi Pico, id=0 corresponds to GPIO 8 (SCL) and 9 (SDA)
UV_I2C = I2C(id=0, scl=Pin(1), sda=Pin(0), freq=400000)  # 400KHz SCL frequency

# UV Sensor constants
UVS_ADDRESS = 0x53          # UV Sensor I2C address
UVS_MAIN_CTRL = 0x00        # Main control register address
ALS_UVS_MEAS_RATE = 0x04    # Measurement rate register address
ALS_UVS_GAIN = 0x05         # Gain register address
UVS_DATA_0 = 0x10           # UV data LSB register address
UVS_DATA_1 = 0x11           # UV data middle byte register address
UVS_DATA_2 = 0x12           # UV data MSB register address

####################
# UV SENSOR CONFIG #
####################
# MAIN_CTRL - Enable UV sensor in UVS mode
UV_I2C.writeto_mem(UVS_ADDRESS, UVS_MAIN_CTRL, bytearray([0x02]))

# ALS_UVS_MEAS_RATE - Set measurement rate to 2000ms and resolution to 18 bits
# According to the datasheet, the measurement rate is the last 3 bits
# 0b00000011 corresponds to 2000ms
UV_I2C.writeto_mem(UVS_ADDRESS, ALS_UVS_MEAS_RATE, bytearray([0x03]))

# ALS_UVS_GAIN - Set gain to 3 (default according to datasheet)
# Gain value is in the last 3 bits, 0b00000001 corresponds to gain of 3
UV_I2C.writeto_mem(UVS_ADDRESS, ALS_UVS_GAIN, bytearray([0x01]))

################
# UV READ DATA #
################
def read_uv_data():
    # Read UV data bytes from the sensor
    uv_data_lsb = UV_I2C.readfrom_mem(UVS_ADDRESS, UVS_DATA_0, 1)[0]  # Least Significant Byte
    uv_data_mid = UV_I2C.readfrom_mem(UVS_ADDRESS, UVS_DATA_1, 1)[0]  # Middle Byte
    uv_data_msb = UV_I2C.readfrom_mem(UVS_ADDRESS, UVS_DATA_2, 1)[0]  # Most Significant Byte
    
    # Combine the three bytes to get the full UV data reading
    uv_data = (uv_data_msb << 16) | (uv_data_mid << 8) | uv_data_lsb
    return uv_data

# Poll the sensor and print the UV data
try:
    while True:
        uv_data = read_uv_data()
        print("UV Data reading:", uv_data)
except KeyboardInterrupt:
    print("Stopped polling UV data.")

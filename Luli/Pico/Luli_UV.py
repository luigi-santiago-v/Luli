# Adapted from  https://forums.pimoroni.com/t/ltr390-micropython-code/22314/2
import utime
from machine import Pin, I2C
import Luli_CONFIG

class LTR390:
    # Constants
    ADDR = 0x53
    MAIN_CTRL = 0x00
    MEAS_RATE = 0x04
    GAIN = 0x05
    PART_ID = 0x06
    MAIN_STATUS = 0x07
    ALSDATA = 0x0D
    UVSDATA = 0x10
    INT_CFG = 0x19
    INT_PST = 0x1A
    THRESH_UP = 0x21
    THRESH_LOW = 0x24
    RESOLUTION_20BIT_utime400MS = 0x00
    RESOLUTION_19BIT_utime200MS = 0x10
    RESOLUTION_18BIT_utime100MS = 0x20  # Default
    RESOLUTION_17BIT_utime50MS = 0x03
    RESOLUTION_16BIT_utime25MS = 0x40
    RESOLUTION_13BIT_utime12_5MS = 0x50
    RATE_25MS = 0x0
    RATE_50MS = 0x1
    RATE_100MS = 0x2  # Default
    RATE_200MS = 0x3
    RATE_500MS = 0x4
    RATE_1000MS = 0x5
    RATE_2000MS = 0x6
    GAIN_1 = 0x0
    GAIN_3 = 0x1  # Default
    GAIN_6 = 0x2
    GAIN_9 = 0x3
    GAIN_18 = 0x4

    def __init__(self):
        self.i2c = I2C(0, scl=Pin(Luli_CONFIG.PIN_UV_SENSOR_SCL), sda=Pin(Luli_CONFIG.PIN_UV_SENSOR_SDA), freq=100000)
        self.ID = self.read_byte(self.PART_ID)
        if self.ID != 0xB2:
            print("Read ID error! Check the hardware...")
            return
        self.write_byte(self.MAIN_CTRL, 0x0A)  # UVS in Active Mode
        self.write_byte(self.MEAS_RATE, self.RESOLUTION_20BIT_utime400MS | self.RATE_2000MS)
        self.write_byte(self.GAIN, self.GAIN_3)

    def read_byte(self, cmd):
        data = self.i2c.readfrom_mem(self.ADDR, cmd, 1)
        return data[0]

    def write_byte(self, cmd, val):
        self.i2c.writeto_mem(self.ADDR, cmd, bytes([val]))

    def read_uvs(self):
        data1 = self.read_byte(self.UVSDATA)
        data2 = self.read_byte(self.UVSDATA + 1)
        data3 = self.read_byte(self.UVSDATA + 2)
        return (data3 << 16) | (data2 << 8) | data1
    
    def get_uv_index(self):
        raw_uvs = self.read_uvs()
        
        uv_index = raw_uvs / Luli_CONFIG.UVS_CONVERSION_FACTOR  # Conversion factor from the datasheet
        return uv_index
    
    def get_uv_data(self):
        raw_uvs = self.read_uvs()
        uv_index = raw_uvs / Luli_CONFIG.UVS_CONVERSION_FACTOR  # Conversion factor from the datasheet
        return raw_uvs, uv_index
    


if __name__ == '__main__':
    sensor = LTR390()
    utime.sleep(1)
    try:
        while True:
            uvs = sensor.read_uvs()
            print("UVS: %d" % uvs)
            utime.sleep(0.5)
    except KeyboardInterrupt:
        print("Interrupted by user")
        exit()

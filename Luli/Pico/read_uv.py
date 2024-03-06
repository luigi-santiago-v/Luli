# WS Sensor UV 1 Sept 2021 Working
import utime
import math
from machine import Pin, I2C
# ========= Start LTR390 UV sensor driver =============
ADDR  = (0X53)

LTR390_MAIN_CTRL = (0x00)  # Main control register
LTR390_MEAS_RATE = (0x04)  # Resolution and data rate
LTR390_GAIN = (0x05)  # ALS and UVS gain range
LTR390_PART_ID = (0x06)  # Part id/revision register
LTR390_MAIN_STATUS = (0x07)  # Main status register
LTR390_ALSDATA = (0x0D)  # ALS data lowest byte, 3 byte
LTR390_UVSDATA = (0x10)  # UVS data lowest byte, 3 byte
LTR390_INT_CFG = (0x19)  # Interrupt configuration
LTR390_INT_PST = (0x1A)  # Interrupt persistance config
LTR390_THRESH_UP = (0x21)  # Upper threshold, low byte, 3 byte
LTR390_THRESH_LOW = (0x24)  # Lower threshold, low byte, 3 byte

#ALS/UVS measurement resolution, Gain setting, measurement rate
RESOLUTION_20BIT_utime400MS = (0X00)
RESOLUTION_19BIT_utime200MS = (0X10)
RESOLUTION_18BIT_utime100MS = (0X20)#default
RESOLUTION_17BIT_utime50MS  = (0x3)
RESOLUTION_16BIT_utime25MS  = (0x40)
RESOLUTION_13BIT_utime12_5MS  = (0x50)
RATE_25MS = (0x0)
RATE_50MS = (0x1)
RATE_100MS = (0x2)# default
RATE_200MS = (0x3)
RATE_500MS = (0x4)
RATE_1000MS = (0x5)
RATE_2000MS = (0x6)

# measurement Gain Range.
GAIN_1  = (0x0)
GAIN_3  = (0x1)# default
GAIN_6 = (0x2)
GAIN_9 = (0x3)
GAIN_18 = (0x4)

UV_SENSITIVITY = 2300 # From datasheet
UVI_TO_UW_CM2 = 25  # 1 UVI = 25 µW/cm²

class LTR390:
    def __init__(self, address=ADDR):
		self.i2c = I2C(id=0, scl=Pin(1), sda=Pin(0), freq=400000)
		self.i2c.writeto_mem(address, LTR390_MAIN_CTRL, bytearray([0x02]))
		self.address = address

		self.ID = self.Read_Byte(LTR390_PART_ID)
		# print("ID = %#x" %self.ID)
		if(self.ID != 0xB2):
			print("read ID error!,Check the hardware...")
			return

		self.Write_Byte(LTR390_MAIN_CTRL, 0x0A) #  UVS in Active Mode
		self.Write_Byte(LTR390_MEAS_RATE, RESOLUTION_20BIT_utime400MS | RATE_2000MS) #  Resolution=18bits, Meas Rate = 100ms
		self.Write_Byte(LTR390_GAIN, GAIN_18) #  Gain Range=3.
		# self.Write_Byte(LTR390_INT_CFG, 0x34) # UVS_INT_EN=1, Command=0x34
		# self.Write_Byte(LTR390_GAIN, GAIN_3) #  Resolution=18bits, Meas Rate = 100ms
        
    def Read_Byte(self, cmd):
        rdate = self.i2c.readfrom_mem(int(self.address), int(cmd), 1)
        return rdate[0]

    def Write_Byte(self, cmd, val):
        self.i2c.writeto_mem(int(self.address), int(cmd), bytes([int(val)]))
        
    def UVS(self):
        # self.Write_Byte(LTR390_MAIN_CTRL, 0x0A) #  UVS in Active Mode
        Data1 = self.Read_Byte(LTR390_UVSDATA)
        Data2 = self.Read_Byte(LTR390_UVSDATA + 1)
        Data3 = self.Read_Byte(LTR390_UVSDATA + 2)
        uv =  (Data3 << 16)| (Data2 << 8) | Data1
        # UVS = Data3*65536+Data2*256+Data1
        # print("UVS = ", UVS)
        return uv
    
    def UVI(self):
        raw_uv = self.UVS()
        WFAC = 1  # WFAC = 1 for no window/glass, WFAC > 1 for tinted window
        uvi = (raw_uv / UV_SENSITIVITY) * WFAC
        return uvi, raw_uv
   
    def UV_intensity(self):
        # convert raw UV data to microwatts per square centimeter (µW/cm^2)
        raw_uv = self.UVS()
        uvi = raw_uv / UV_SENSITIVITY
        uv_intensity = uvi * UVI_TO_UW_CM2
        return uv_intensity


    
# ========= End LTR390 UV sensor driver =============
if __name__ == '__main__':
    sensor = LTR390()
    utime.sleep(1)
    try:
        while True:
            #UVI, raw = sensor.UVI()
            UV_level = sensor.UV_intensity()
            print("UV Intensity: {:.2f} µW/cm²".format(UV_level))
            utime.sleep(0.5)
            
    except KeyboardInterrupt:
        exit()
        
        
"""UV Intensity: 0.00 µW/cm²
UV Intensity: 0.00 µW/cm²
UV Intensity: 0.41 µW/cm²
UV Intensity: 0.41 µW/cm²
UV Intensity: 0.41 µW/cm²
UV Intensity: 0.41 µW/cm²
UV Intensity: 0.40 µW/cm²
UV Intensity: 0.40 µW/cm²
UV Intensity: 0.40 µW/cm²
UV Intensity: 0.40 µW/cm²
UV Intensity: 0.38 µW/cm²
UV Intensity: 0.38 µW/cm²
UV Intensity: 0.38 µW/cm²
UV Intensity: 0.38 µW/cm²
UV Intensity: 0.46 µW/cm²
UV Intensity: 0.46 µW/cm²
UV Intensity: 0.46 µW/cm²
UV Intensity: 0.46 µW/cm²
UV Intensity: 0.00 µW/cm²
UV Intensity: 0.00 µW/cm²
UV Intensity: 0.00 µW/cm²
UV Intensity: 0.00 µW/cm²
UV Intensity: 0.00 µW/cm²
"""

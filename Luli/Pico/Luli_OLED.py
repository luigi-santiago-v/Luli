from machine import Pin, SPI
import ssd1306
import time

class OLEDMenuDisplay:
    def __init__(self):
        # SPI setup
        self.spi = SPI(1, baudrate=1000000, polarity=1, phase=1, bits=8, firstbit=SPI.MSB,
                       sck=Pin(10), mosi=Pin(11))
        # Display setup
        self.cs = Pin(13)   # Chip select
        self.dc = Pin(15)   # Data/command
        self.rst = Pin(14, Pin.OUT)   # Reset
        self.display = ssd1306.SSD1306_SPI(128, 64, self.spi, self.dc, self.rst, self.cs)

        self.display.poweron()
        self.display.show()

    def init_main_menu(self):
        self.display.fill(0)
        self.display.rect(0, 0, 10, 20, 1)
        self.display.rect(11, 0, 117, 20, 1)
        self.display.text('Sensor Data', 13, 5, 1)

        self.display.rect(0, 21, 10, 20, 1)
        self.display.rect(11, 21, 117, 20, 1)
        self.display.text('Cycle Info', 13, 25, 1)
        
        self.display.rect(0, 42, 10, 20, 1)
        self.display.rect(11, 42, 117, 20, 1)
        self.display.text('Plants', 13, 45, 1)
        self.display.show()

    def print_main_menu(self, select):
        self.display.fill(0)
        menu_highlight = 20 * select + select
        self.init_main_menu()
        self.display.fill_rect(0, menu_highlight, 10, 20, 1)
        self.display.show()

    def print_sensor_data(self, ph, temp, light, humidity, tank):
        self.display.fill(0)
        self.display.text('Tank: ' + str(tank), 0, 0, 1)
        self.display.text('pH: ' + str(ph), 0, 16, 1)
        self.display.text('Temp: ' + str(temp), 0, 27, 1)
        self.display.text('Light: ' + str(light), 0, 39, 1)
        self.display.text('Humidity: ' + str(humidity), 0, 51, 1)
        self.display.show()

    def print_plant_menu(self, plant_name='Spinach', planted_date='5/5/24', harvest_date='9/3/24'):
        self.display.fill(0)
        self.display.text('Plants', 0, 0, 1)
        self.display.text(f'Plant: {plant_name}', 0, 16, 1)
        self.display.text(f'Planted: {planted_date}', 0, 27, 1)
        self.display.text(f'Harvest: {harvest_date}', 0, 39, 1)
        self.display.show()

def main():
    display = OLEDMenuDisplay()
    display.init_main_menu()
    time.sleep(1)

    # Loop through menu printing functions as an example
    while True:
        display.print_sensor_data(7.2, 22.5, 150, 45, 'Full')
        time.sleep(6)
        display.print_plant_menu('Tomatoes', '4/1/24', '6/28/24')
        time.sleep(6)

if __name__ == "__main__":
    main()

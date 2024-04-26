import network
import urequests as requests
import ujson
import machine
class NetworkHandler:
    def get_hardware_id(self):
        # Get the unique hardware ID
        unique_id = machine.unique_id()
        # Convert ID bytes to hexadecimal string
        hex_string = "".join("{:02x}".format(byte) for byte in unique_id)
        print("Unique Hardware ID:", hex_string)
        return unique_id

    
    def __init__(self, ssid, password, base_url):
        self.ssid = ssid
        self.password = password
        self.base_url = base_url
        self.wlan = network.WLAN(network.STA_IF)
        self.hardware_id = self.get_hardware_id()

    def connect_wifi(self):
        """Connects to WiFi using the SSID and password provided during initialization."""
        self.wlan.active(True)
        if not self.wlan.isconnected():
            print('Connecting to network...')
            self.wlan.connect(self.ssid, self.password)
            while not self.wlan.isconnected():
                pass
        print('Network config:', self.wlan.ifconfig())

    def send_data(self, endpoint, data):
        """Sends data to a specified API endpoint using HTTP POST."""
        headers = {'Content-Type': 'application/json', 'X-Device-ID': self.hardware_id}
        response = requests.post(self.base_url + endpoint, data=ujson.dumps(data), headers=headers)
        print(response.text)
        # Free up memory once the request is complete
        if 'response' in locals():
            response.close()
        return response

def main():
    ssid = 'YourSSID'
    password = 'YourPassword'
    base_url = 'http://yourapi.com/api/'
    endpoint = 'update_all_sensor_data'
    sensor_data = {
        "temp": 23.5,
        "humidity": 45,
        "light": 300,
        "ph": 7.0,
        "tank": 80
    }

    network_handler = NetworkHandler(ssid, password, base_url)
    network_handler.connect_wifi()
    network_handler.send_data(endpoint, sensor_data)

if __name__ == '__main__':
    main()

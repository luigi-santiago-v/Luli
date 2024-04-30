import network
import urequests as requests
import ujson
import machine
import Luli_CONFIG
class NetworkHandler:
    def get_hardware_id(self):
        # Get the unique hardware ID
        unique_id = machine.unique_id()
        # Convert ID bytes to hexadecimal string
        hex_string = "".join("{:02x}".format(byte) for byte in unique_id)
        print("Unique Hardware ID:", hex_string)
        return unique_id
    

    
    def __init__(self, ssid, password, base_url):
        self.ssid = Luli_CONFIG.WIFI_SSID
        self.password = Luli_CONFIG.WIFI_PASSWORD
        self.base_url = Luli_CONFIG.SERVER_URL
        self.wlan = network.WLAN(network.STA_IF)
        self.hardware_id = str(self.get_hardware_id())

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
        try:
            response = requests.post(self.base_url + endpoint, data=ujson.dumps(data), headers=headers)
            print(response.text)
            # Free up memory once the request is complete
            if 'response' in locals():
                response.close()
            return response
        except Exception as e:
            print("Failed to send data:", e)
            return None
        
    
    def get_manual_override(self):
        """Checks for manual override commands from the server using device-specific endpoint."""
        device_specific_endpoint = Luli_CONFIG.ENDPOINT_MANUAL_OVERRIDE + '/' + self.hardware_id
        try:
            response = requests.get(self.base_url + device_specific_endpoint)
            if response.status_code == 200:
                commands = response.json()
                return commands
            else:
                print("Failed to get manual override, status code:", response.status_code)
                return None
        except Exception as e:
            print("Failed to get manual override:", e)
            return None
        finally:
            if 'response' in locals():
                response.close()

    def fetch_and_update_settings(self):
        headers = {'X-Device-ID': Luli_CONFIG.DEVICE_ID}
        try:
            response = requests.get(self.base_url + Luli_CONFIG.ENDPOINT_GET_SETTINGS, headers=headers)
            if response.status_code == 200:
                new_settings = response.json()
                return new_settings
            else:
                print("Failed to fetch settings:", response.text)
        except Exception as e:
            print("Failed to fetch settings:", e)
            return None
        finally:
            if 'response' in locals():
                response.close()

    

if __name__ == '__main__':
    ssid = 'YourSSID'
    password = 'YourPassword'
    base_url = 'http://yourapi.com'
    endpoint = '/api/update_all_sensor_data'
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


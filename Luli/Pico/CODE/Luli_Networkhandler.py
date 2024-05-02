import network
import urequests as requests
import ujson
import machine
#import ubinascii
import Luli_CONFIG
class NetworkHandler:
    def get_hardware_id(self):
        # Get the unique hardware ID
        unique_id = machine.unique_id()
        # Convert ID bytes to hexadecimal string using hex and string manipulation
        hex_string = ''.join('{:02x}'.format(x) for x in unique_id)
        print("Unique Hardware ID:", hex_string)
        return hex_string
    

    
    def __init__(self, ssid, password, base_url):
        self.ssid = Luli_CONFIG.WIFI_SSID
        self.password = Luli_CONFIG.WIFI_PASSWORD
        self.base_url = Luli_CONFIG.SERVER_URL
        self.wlan = network.WLAN(network.STA_IF)
        self.hardware_id = str(self.get_hardware_id())
        #self.mac = ubinascii.hexlify(network.WLAN().config('mac'),':').decode()
        #print(self.mac)

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
            #print(f"SENDING TO {self.base_url + endpoint}")
            response = requests.post(self.base_url + endpoint, data=ujson.dumps(data), headers=headers)
            print(response.text)
            # Free up memory once the request is complete
            if 'response' in locals():
                response.close()
            return response
        except Exception as e:
            print("Failed to send data:", e)
            #raise e
            return None
        
    def fetch_and_apply_settings(self):
        """Fetch settings from the server and apply them to the local config."""
        response = requests.get(self.base_url + Luli_CONFIG.ENDPOINT_GET_SETTINGS + '/' + self.hardware_id)
        if response.status_code == 200:
            settings = response.json()
            # Update config variables
            if 'led_duration' in settings:
                Luli_CONFIG.DURATION_LED_CYCLE = int(settings['led_duration']) * 60  # Convert minutes to seconds
            if 'pump_duration' in settings:
                Luli_CONFIG.DURATION_WATER_CYCLE = int(settings['pump_duration']) * 3600  # Convert hours to seconds
            if 'water_interval' in settings:
                Luli_CONFIG.NEXT_WATER_CYCLE = int(settings['water_interval']) * 3600  # Convert hours to seconds
            print("Updated settings:", Luli_CONFIG.DURATION_LED_CYCLE, Luli_CONFIG.DURATION_WATER_CYCLE, Luli_CONFIG.NEXT_WATER_CYCLE)
        else:
            print("Failed to fetch settings, status code:", response.status_code)
    
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


 


if __name__ == '__main__':
    ssid = Luli_CONFIG.WIFI_SSID
    password = Luli_CONFIG.WIFI_PASSWORD
    base_url = Luli_CONFIG.SERVER_URL
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
    print(f"BEFORE UPDATE: LED DURATION IS {Luli_CONFIG.DURATION_LED_CYCLE} SECONDS")
    print(f"BEFORE UPDATE: PUMP DURATION IS {Luli_CONFIG.DURATION_WATER_CYCLE} SECONDS")
    print(f"BEFORE UPDATE: PUMP INTERVAL IS {Luli_CONFIG.NEXT_WATER_CYCLE} SECONDS")
    network_handler.fetch_and_apply_settings()
    print(f"AFTER UPDATE: LED DURATION IS {Luli_CONFIG.DURATION_LED_CYCLE} SECONDS")
    print(f"AFTER UPDATE: PUMP DURATION IS {Luli_CONFIG.DURATION_WATER_CYCLE} SECONDS")
    print(f"AFTER UPDATE: PUMP INTERVAL IS {Luli_CONFIG.NEXT_WATER_CYCLE} SECONDS")
    #network_handler.send_data(endpoint, sensor_data)
    #network_handler.get_manual_override()
    while True:
        pass

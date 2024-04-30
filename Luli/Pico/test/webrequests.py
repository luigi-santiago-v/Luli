#mongodb://localhost:27017/

import dht
import machine
import urequests as requests
import network
import time
import ujson

# Function to collect data from DHT sensors
def collect_sensor_data():
    rows, cols = (2, 4)
    measurement = [[0 for i in range(cols)] for j in range(rows)]
    testNum = 69
    
    for i in range(4):
        d0 = dht.DHT22(machine.Pin(18))
        d0.measure()
        d1 = dht.DHT22(machine.Pin(19))
        d1.measure()
        d2 = dht.DHT22(machine.Pin(20))
        d2.measure()
        d3 = dht.DHT22(machine.Pin(21))
        d3.measure()
        temperature = (d0.temperature() + d1.temperature() + d2.temperature() + d3.temperature())/4
        humidity = (d0.humidity() + d1.humidity() + d2.humidity() + d3.humidity())/4
        # temperature averages
        measurement [0][i] = temperature
        # humidity averages
        measurement [1][i] = humidity
        time.sleep(2)
        
    temperatureAverage = (measurement[0][0] + measurement[0][1] + measurement[0][2] + measurement[0][3])/4
    humidityAverage = (measurement[1][0] + measurement[1][1] + measurement[1][2] + measurement[1][3])/4
    
    return {"temp": temperatureAverage, "humidity": humidityAverage, "light" : testNum, "ph" : testNum, "tank" : testNum}

def connect_wifi(ssid,password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Connecting to network...')
        wlan.connect(ssid,password)
        while not wlan.isconnected():
            pass
    print('Network config: ', wlan.ifconfig())
    
def test_api(api_url):
    
    sensorData = collect_sensor_data()
    data = ujson.dumps(sensorData)   
    headers = {'Content-Type': 'application/json'}
    response = requests.post(api_url, data=ujson.dumps(data), headers=headers)
    print(response.text)

    

def main():
    ssid = 'Liam'
    password = 'liampassword'
    api_test_url = 'http://172.20.10.4:9696/api/update_all_sensor_data'   
    connect_wifi(ssid,password)
    test_api(api_test_url)
    
if __name__ == '__main__' :
    main()
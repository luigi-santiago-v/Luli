import urequests
import network

def connect_wifi(ssid,password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Connecting to network...')
        wlan.connect(ssid,password)
        while not wlan.isconnected():
            pass
    print('Network config: ', wlan.ifconfig())
    

def test_https():
    try:
        # Attempt to make an HTTPS GET request
        response = urequests.get('https://httpbin.org/get')
        # If the request was successful, print the response text
        print(response.text)
        print("HTTPS request successful. SSL/TLS is working.")
    except OSError as e:
        # Handle errors related to network issues, including SSL handshake failures
        print("An OSError occurred. Possible SSL/TLS problem.")
        print("Error details:", str(e))
    except Exception as e:
        # Handle other exceptions that may occur
        print("An unexpected error occurred.")
        print("Error details:", str(e))
    finally:
        # Close the response to free up resources, if the request was made successfully
        if 'response' in locals():
            response.close()

# Run the test function
if __name__ == "__main__":
    connect_wifi("Liam", "liampassword")
    test_https()


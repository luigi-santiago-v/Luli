import machine
import utime

# Pin assignments
trig = machine.Pin(17, machine.Pin.OUT)
echo = machine.Pin(9, machine.Pin.IN)

def read_distance():
    # Ensure the trigger pin is low for a short time
    trig.low()
    utime.sleep_us(5)

    # Send a 10us pulse to start the measurement
    trig.high()
    utime.sleep_us(10)
    trig.low()

    timeout = 10000  # timeout in microseconds

    # Measure the length of the echo signal
    start_time = utime.ticks_us()
    while echo.value() == 0:
        if (utime.ticks_diff(utime.ticks_us(), start_time) > timeout):
            return None  # return None if no signal detected within the timeout
    signal_off = utime.ticks_us()

    start_time = utime.ticks_us()
    while echo.value() == 1:
        if (utime.ticks_diff(utime.ticks_us(), start_time) > timeout):
            return None  # return None if signal doesn't end within the timeout
    signal_on = utime.ticks_us()

    # Calculate the duration of the echo pulse
    time_passed = utime.ticks_diff(signal_on, signal_off)

    # Calculate distance in centimeters
    distance = (time_passed * 0.0343) / 2

    return distance

while True:
    distance = read_distance()
    if distance is not None and distance > 2:  # Check if distance is plausible
        print("Distance:", distance, "cm")
    else:
        print("Out of range or too close")
    utime.sleep(1)

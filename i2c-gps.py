import time
import smbus
import signal
import sys
import math
import servo_test
import RPi.GPIO as GPIO

latitude_list = [37.0, 15.0, 18.0]
longtitude_list = [45.0, 12.0, 19.0]
altitude = 0.0
nichrome_duration = 20
servo_clock = 0
servo_ctrclock = 180

# Set up GPIO for servo control
servo1_pin = 12
servo2_pin = 7
GPIO.setmode(GPIO.BCM)
GPIO.setup(servo1_pin, GPIO.OUT)
GPIO.setup(servo2_pin, GPIO.OUT)
servo_test.servo1 = GPIO.PWM(servo1_pin, 50)
servo_test.servo2 = GPIO.PWM(servo2_pin, 50)
servo_test.servo1.start(0)
servo_test.servo2.start(0)

# Define divergence angle and maximum divergence angle
max_divergence_angle = 180  # Maximum angle for panel divergence
min_divergence_angle = 0  # Minimum angle for panel divergence

# Define servo min and max duty cycle
servo_test.servo_min_duty = 3
servo_test.servo_max_duty = 12

servo_test.set_servo_degree(1, 90)
servo_test.set_servo_degree(2, 90)


# I2C 버스에 연결
BUS = None
address = 0x42
gpsReadInterval = 0.03

# Define attitude threshold
altitude_threshold = 10  # degrees

# Define CanSat falling status
CanSat_is_falling = True

# Set up GPIO for nichrome wire control
nichrome_pin = 18  # Set the pin number for the nichrome wire
GPIO.setup(nichrome_pin, GPIO.OUT)

def connectBus():
    global BUS
    BUS = smbus.SMBus(1)

def parseResponse(gpsLine):
    if (gpsLine.count(36) == 1):
        if len(gpsLine) < 84:
            CharError = 0
            for c in gpsLine:
                if (c < 32 or c > 122) and c != 13:
                    CharError += 1
            if CharError == 0:
                gpsChars = ''.join(chr(c) for c in gpsLine)
                if gpsChars.find('txbuf') == -1:
                    gpsStr, chkSum = gpsChars.split('*', 2)
                    gpsComponents = gpsStr.split(',')
                    chkVal = 0
                    for ch in gpsStr[1:]:
                        chkVal ^= ord(ch)
                    if chkVal == int(chkSum, 16):
                        if gpsChars.count('GNGGA') == 1:
                            latitude = float(gpsComponents[2])
                            longitude = float(gpsComponents[4])
                            altitude = float(gpsComponents[9])

                            latitude_deg = int(latitude // 100)
                            latitude_min = latitude - latitude_deg * 100
                            latitude_sec = (latitude_min % 1) * 60

                            longitude_deg = int(longitude // 100)
                            longitude_min = longitude - longitude_deg * 100
                            longitude_sec = (longitude_min % 1) * 60

                            latitude_list = [latitude_deg, latitude_min, latitude_sec]
                            longtitude_list = [longtitude_deg, longtitude_min, longtitude_sec]

                            print("GPS data latitude: {}° {}' {:.2f}\"".format(latitude_deg, latitude_min, latitude_sec))
                            print("GPS data longitude: {}° {}' {:.2f}\"".format(longitude_deg, longitude_min, longitude_sec))
                            print("GPS data altitude: {} meters".format(altitude))

                            # Write GPS data to a file
                            with open('gps_data.txt', 'w') as file:
                                file.write("latitude:{}\nlongitude:{}\naltitude:{}".format(latitude, longitude, altitude))

def handle_ctrl_c(signal, frame):
    sys.exit(130)

# This will capture exit when using Ctrl-C
signal.signal(signal.SIGINT, handle_ctrl_c)

def readGPS():
    c = None
    response = []
    try:
        while True:  # Newline, or bad char.
            c = BUS.read_byte(address)
            if c == 255:
                return False
            elif c == 10:
                break
            else:
                response.append(c)
        parseResponse(response)
    except IOError:
        connectBus()
    except Exception as e:
        print(e)

connectBus()

target_lat = [37.0, 15.0, 16.0]
target_lon = [45.0, 12.0, 25.0]
for a in range(3):
    target_lat[a] = float(input())
for a in range(3):
    target_lon[a] = float(input())
prev_altitude = None

while True:
    #readGPS()
    #time.sleep(gpsReadInterval)
    if altitude >= altitude_threshold:
        CanSat_is_falling = True
    else:
        CanSat_is_falling = False

    if CanSat_is_falling:
        check_lat = adjust_servo_lat(target_lat, latitude_list)
        check_lon = adjust_servo_lon(target_lon, longtitude_list)
        if check_lat:
            set_servo_degree(1, servo_clock)
        else:
            set_servo_degree(1, servo_ctrclock)
        if check_lon:
            set_servo_degree(2, servo_clock)
        else:
            set_servo_degree(2, servo_ctrclock)

    else:
        # If CanSat's attitude is below the threshold, heat the nichrome wire and fold all panels
        heat_nichrome(nichrome_duration)  # Heat the nichrome wire for 5 seconds
        set_servo_degree(1, 90)
        set_servo_degree(2, 90)
        time.sleep(1.0)  # Wait for panels to fold and nichrome wire to heat up
        break


# Wait for a specific duration before updating control again
time.sleep(1.0)

# Stop PWM output and clean up GPIO
servo1.stop()
servo2.stop()
GPIO.cleanup()

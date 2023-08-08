import time
import serial
import RPi.GPIO as GPIO
from datetime import datetime

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(23, GPIO.OUT)

# Properties of serial connection: Define port, baudrate and parities
ser = serial.Serial(
    port='/dev/ttyS0',
    baudrate = 9600,
    parity = serial.PARITY_NONE,
    stopbits = serial.STOPBITS_ONE,
    bytesize = serial.EIGHTBITS,
    timeout = 1
)
counter = 0

# Data logging setup
def logdata(text):
    try:
        t = datetime.today().isoformat(sep=' ', timespec='milliseconds')
        data.write(f'[{t}] {text}')
        data.write('\n')
        print(f'[{t}] {text}')
    except:
        print("An error has been generated while inserting log data")
        return

data = open(f'./dataLog.txt', 'a')
logdata("Log file generated")

 # Send and receiving elements
 # Receiving elements:
 # 1. Humidity(float)
 # 2. Temperature(float)
 # 3. Gas Alert(string)
 # 4. Gas(float)
 # 5. UV dose(float)
 # 6. UV index(int)
 # 7. GPS data: latitude, longitude, altitude
 # 8. IMU data: Acceleration(x, y, z), Gyro(x, y, z) -> Total 6 data


# Data Packet
packet = {"humidity": None,
          "temperature": None,
          "gasAlert": None,
          "gas": None,
          "UVdose": None,
          "UVindex": None,
          "GPS": {0, 0, 0},
          "IMU": {0, 0, 0, 0, 0, 0},
          "Packet_Count": 1
          }

while 1:
    # All receiving data should be updated below here
    humidity = 1000
    temperature = 2
    gasAlert = 0
    gas = 3
    UVdose = 4
    UVindex = 5
    latitude = 6
    longitude = 7
    altitude = 8
    accel_X = 9
    accel_Y = 10
    accel_Z = 11
    gyro_X = 12
    gyro_Y = 13
    gyro_Z = 14

    packet['humidity'] = humidity
    packet['temperature'] = temperature
    packet['gasAlert'] = "Alert"
    packet['gas'] = gas
    packet['UVdose'] = UVdose
    packet['UVindex'] = UVindex
    packet['GPS'] = {latitude, longitude, altitude}
    packet['IMU'] = {accel_X, accel_Y, accel_Z, gyro_X, gyro_Y, gyro_Z}

    curtime = datetime.today().isoformat(sep=' ', timespec = 'milliseconds')

    sendstr = f"{packet['Packet_Count']}, {curtime}"
    sendstr += "/*"
    sendstr += f"{packet['humidity']}, {packet['temperature']}, {packet['gasAlert']}, {packet['gas']}, {packet['UVdose']}, {packet['UVindex']}"
    sendstr += f"{packet['GPS']}, {packet['IMU']}"
    sendstr += "*/"

    logdata(sendstr)
    ser.write(sendstr.encode())
    time.sleep(0.5)
    packet['Packet_Count'] += 1

    #x = ser.readline().strip()
    #print(x)

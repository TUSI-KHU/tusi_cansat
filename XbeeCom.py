import time
import serial
import RPi.GPIO as GPIO
from datetime import datetime
import subprocess

#import ctypes

#path = "./imu.so"
#c_module = ctypes.cdll.LoadLibrary(path)

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
          "IMU": {0, 0, 0, 0, 0, 0, 0},
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
    gyroXangle = 9
    gyroYangle = 10
    gyroZangle = 11
    AccYangle = 12
    AccXangle = 13
    CFangleX = 14
    CFangleY = 15

    # Setting imu c script as subprocess
    imu_output = subprocess.check_output(['./gyro_accelerometer_tutorial01'])
    imu_variable_lines = c_script_output.decode().split('\n')

    # Updating IMU outputs from the imu script
    gyroXangle = float(imu_variables_lines[0].strip())
    gyroYangle = float(imu_variables_lines[1].strip())
    gyroZangle = float(imu_variables_lines[2].strip())
    AccYangle = float(imu_variables_lines[3].strip())
    AccXangle = float(imu_variables_lines[4].strip())
    CFangleX = float(imu_variables_lines[5].strip())
    CFangleY = float(imu_variables_lines[6].strip())

    packet['humidity'] = humidity
    packet['temperature'] = temperature
    packet['gasAlert'] = "Alert"
    packet['gas'] = gas
    packet['UVdose'] = UVdose
    packet['UVindex'] = UVindex
    packet['GPS'] = {latitude, longitude, altitude}
    packet['IMU'] = {gyroXangle, gyroYangle, gyroZangle, AccYangle, AccXangle, CFangleX, CFangleY}

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

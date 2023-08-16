import time
import smbus
import signal
import sys
import math

BUS = None
address = 0x42
gpsReadInterval = 0.03

def connectBus():
    global BUS
    BUS = smbus.SMBus(1)

def parseResponse(gpsLine):
    if (gpsLine.count(36) == 1):  # Check #1, make sure '$' doesnt appear twice
        if len(gpsLine) < 84:  # Check #2, 83 is maximum NMEA sentence length.
            CharError = 0
            for c in gpsLine:  # Check #3, Make sure that only readable ASCII characters and Carriage Return are seen.
                if (c < 32 or c > 122) and c != 13:
                    CharError += 1
            if (CharError == 0):  # Only proceed if there are no errors.
                gpsChars = ''.join(chr(c) for c in gpsLine)
                if (gpsChars.find('txbuf') == -1):  # Check #4, skip txbuff allocation error
                    gpsStr, chkSum = gpsChars.split('*', 2)  # Check #5 only split twice to avoid unpack error
                    gpsComponents = gpsStr.split(',')
                    chkVal = 0
                    for ch in gpsStr[1:]:  # Remove the $ and do a manual checksum on the rest of the NMEA sentence
                        chkVal ^= ord(ch)
                    if (chkVal == int(chkSum, 16)):  # Compare the calculated checksum with the one in the NMEA sentence
                        if (gpsChars.count('GNGGA') == 1):
                            latitude = float(gpsComponents[2])
                            longitude = float(gpsComponents[4])
                            altitude = float(gpsComponents[9])

                            latitude_deg = int(latitude // 100)
                            latitude_min = latitude - latitude_deg * 100
                            latitude_sec = (latitude_min % 1) * 60

                            longitude_deg = int(longitude // 100)
                            longitude_min = longitude - longitude_deg * 100
                            longitude_sec = (longitude_min % 1) * 60

                            print("GPS data latitude: {}° {}' {:.2f}\"".format(latitude_deg, latitude_min, latitude_sec))
                            print("GPS data longitude: {}° {}' {:.2f}\"".format(longitude_deg, longitude_min, longitude_sec))
                            print("GPS data altitude: {} meters".format(altitude))

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

while True:
    readGPS()
    time.sleep(gpsReadInterval)

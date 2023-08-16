import time
import smbus
import signal
import sys
import pynmea2

BUS = None
address = 0x42
gpsReadInterval = 0.03

def connectBus():
    global BUS
    BUS = smbus.SMBus(1)

def parseResponse(gpsLine):
    if (gpsLine.count(36)) == 1:
        if len(gpsLine) < 84:
            CharError = 0;
            for c in gpsLine:
                if(c < 32 or c > 122) and c != 13:
                    CharError += 1
            if CharError == 0:
                gpsChars = ''.join(chr(c) for c in gpsLine)
                if (gpsChars.find('txbuf') == -1):
                    gpsStr, chkSum = gpsChars.split('*', 2)
                    gpsComponents = gpsStr.split(',')
                    chkVal = 0
                    for ch in gpsStr[1:]:
                        chkVal ^= ord(ch)
                    if (chkVal == int(chkSum, 16)):
                        msg = pynmea2.parse(gpsChars)
                        print ("Timestamp: ", msg.timestamp, "Latitude: ", msg.lat)
                        with open("gps_data.txt", "a") as f:
                            f.write(gpsChars)

def handle_ctrl_c(signal, frame):
    sys.exit(130)

# This will capture exit when using Ctrl-C
signal.signal(signal.SIGINT, handle_ctrl_c)

def readGPS():
    c = None
    response = []
    try:
        while True:
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

def parseGPS(str):
    if str.find('GGA') > 0:
        msg = pynmea2.parse(str)


connectBus()

while True:
    readGPS()
    time.sleep(gpsReadInterval)


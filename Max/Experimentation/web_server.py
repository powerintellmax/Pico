import network
import socket
from time import sleep
import machine
import json
from umqtt.simple import MQTTClient
import utime
import time

# change these to be imported from settings file
SSID = 'MOTO23F2'
PASSWORD = 'latebean866'

# MQTT server settings using HIVEMQ
mqtt_server = 'broker.hivemq.com'
client_id = 'bigles'
topic_pub = b'HotShot Detector'
topic_msg = b'Shot Found'

# ADXL345 accelerometer registers
ADXL345_ADDRESS = 0x53
ADXL345_REG_POWER_CTL = 0x2D
ADXL345_REG_DATA_FORMAT = 0x31
ADXL345_REG_DATAX0 = 0x32
ADXL345_REG_DATAY0 = 0x34
ADXL345_REG_DATAZ0 = 0x36

# Set up I2C communication
i2c = machine.I2C(0, scl=machine.Pin(1), sda=machine.Pin(0), freq=400000)

# Set up ADXL345 accelerometer
i2c.writeto_mem(ADXL345_ADDRESS, ADXL345_REG_POWER_CTL, bytes([0x08]))  # Set measurement mode
i2c.writeto_mem(ADXL345_ADDRESS, ADXL345_REG_DATA_FORMAT, bytes([0x0B]))  # Set full resolution, +/- 16g range

# Set up auto-sleep mode
i2c.writeto_mem(ADXL345_ADDRESS, 0x2C, bytes([0x0A]))  # Set activity threshold to 10mg
i2c.writeto_mem(ADXL345_ADDRESS, 0x2F, bytes([0x20]))  # Set activity mode to AC coupled, enter sleep after activity
i2c.writeto_mem(ADXL345_ADDRESS, 0x2E, bytes([0x80]))  # Enable auto-sleep



            
def connect():
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        sleep(1)
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')
    return ip

def mqtt_connect():
    client = MQTTClient(client_id, mqtt_server, keepalive=3600)
    client.connect()
    print('Connected to %s MQTT Broker'%(mqtt_server))
    return client

def reconnect():
   print('Failed to connect to the MQTT Broker. Reconnecting...')
   time.sleep(5)
   machine.reset()
   

    

# get connection to wifi and then to MQTT borker
try:
    ip = connect()
#    client = mqtt_connect()
#except OSError as e:
#   reconnect()
except KeyboardInterrupt:
    machine.reset()

def message_mqtt(message=None):
    client.publish(topic_pub,message)

activity_time = 0
# Read accelerometer data and check for activity
# Read accelerometer data

# use sleep status to determine if a message needs to be sent to MQTT
# 1 = awake
# 0 = asleep
wake_status=1
while True:
    data = i2c.readfrom_mem(ADXL345_ADDRESS, ADXL345_REG_DATAX0, 6)
    x = (data[1] << 8) | data[0]
    y = (data[3] << 8) | data[2]
    z = (data[5] << 8) | data[4]

    # Convert to g units
    x = x / 256.0
    y = y / 256.0
    z = z / 256.0

    if x > 0 or y > 250 or z > 250:
        # wakeup pico
        machine.lightsleep(0)
        activity_time = 0  # Reset activity timer
        print("Activity detected")
        # send message to MQTT
        #client.publish(topic_pub, topic_msg)
        # flip wake flag
        wake_status=1
        print({'x':x,'y':y,'z':z})
    else:
        activity_time += 1  # Increment activity timer
        #return({'x':x,'y':y,'z':z})

    # Enter auto-sleep mode if activity has been less than X for 10 seconds or more
    if activity_time >= 100:
        print("Entering low power mode")
        
        #if wake_status == 1:
            #client.publish(topic_pub, "Enter Sleep Mode")
        wake_status = 0
        #i2c.writeto_mem(ADXL345_ADDRESS, ADXL345_REG_POWER_CTL, bytes([0x04]))  # Enter standby mode
        #utime.sleep_ms(1000)  # Wait for auto-sleep to take effect
        #i2c.writeto_mem(ADXL345_ADDRESS, ADXL345_REG_POWER_CTL, bytes([0x08]))  # Set measurement mode
        machine.deepsleep()
        activity_time = 0  # Reset activity timer


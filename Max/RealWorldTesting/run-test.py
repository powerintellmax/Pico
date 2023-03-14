from machine import Pin, I2C
import utime
import json

'''
The THRESH_ACT register is eight bits and holds the threshold
value for detecting activity. The data format is unsigned, so the
magnitude of the activity event is compared with the value in the
THRESH_ACT register. The scale factor is 62.5 mg/LSB. A value
of 0 may result in undesirable behavior if the activity interrupt is
enabled.
'''
# REGISTERS
REG_THRESH_ACT = 0x24
REG_ACT_INACT_CTL = 0x27
REG_POWER_CTL = 0x2D
REG_INT_ENABLE = 0x2E
ADXL345_REG_DATA_FORMAT = 0x31
ADXL345_REG_DATAX0 = 0x32
ADXL345_REG_DATAY0 = 0x34
ADXL345_REG_DATAZ0 = 0x36

# Initialize I2C connection with ADXL345
i2c = I2C(0, scl=Pin(1), sda=Pin(0),freq=400000)
ADXL345_ADDR = 0x53

# set to measurment mode and set THRESH_ACT
i2c.writeto_mem(ADXL345_ADDR, REG_POWER_CTL, bytes([0x08]))
i2c.writeto_mem(ADXL345_ADDR, ADXL345_REG_DATA_FORMAT, bytes([0x0B]))  # Set full resolution, +/- 16g range
i2c.writeto_mem(ADXL345_ADDR, REG_THRESH_ACT, bytes([0x50]))

# set the activity X,Y,Z axis
#i2c.writeto_mem(ADXL345_ADDR, REG_ACT_INACT_CTL,b'01110111')

# Set up interrupt pin
INT_PIN = Pin(19, Pin.IN)

# enable the interrupt register
#i2c.writeto_mem(ADXL345_ADDR, REG_INT_ENABLE,b'00010000')

g_limit = 1

def handle_interrupt(pin):
    #i2c.writeto_mem(ADXL345_ADDR, REG_ACT_INACT_CTL,b'00000000')
    #i2c.writeto_mem(ADXL345_ADDR, REG_POWER_CTL, bytes([0x08]))
    data_report = {
        "timestamp_start":None,
        "timestamp_end":None,
        "x":[],
        "y":[],
        "z":[]
    }
    print("Activity Detected")
    still_high = True
    data_report["timestamp_start"]=utime.localtime()
    while still_high:
        data = i2c.readfrom_mem(ADXL345_ADDR, ADXL345_REG_DATAX0, 6)
        x = (data[1] << 8) | data[0]
        y = (data[3] << 8) | data[2]
        z = (data[5] << 8) | data[4]
        
        x = x / 256.0
        y = y / 256.0
        z = z / 256.0
        if x >= g_limit or y >= g_limit or z >=g_limit:
            data_report["x"].append(x)
            data_report["y"].append(y)
            data_report["z"].append(z)
        else:
            data_report["timestamp_end"]=utime.localtime()
            data_report
            print(json.dumps(data_report))
            still_high=False
    
    

INT_PIN.irq(trigger=Pin.IRQ_FALLING, handler=handle_interrupt)

while True:
    print("running")
    utime.sleep(2)
   


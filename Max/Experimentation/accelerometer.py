import machine
import utime

# ADXL345 accelerometer registers
def acclerometer():
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

    activity_time = 0
    # Read accelerometer data and check for activity
    while True:
        # Read accelerometer data
        data = i2c.readfrom_mem(ADXL345_ADDRESS, ADXL345_REG_DATAX0, 6)
        x = (data[1] << 8) | data[0]
        y = (data[3] << 8) | data[2]
        z = (data[5] << 8) | data[4]
        print(x,y,z)

        # Convert to g units
        x = x / 256.0
        y = y / 256.0
        z = z / 256.0

        # Check for activity greater than 2g
        if x > 5 or y > 5 or z > 5:
            activity_time = 0  # Reset activity timer
            print("Activity detected")
        else:
            activity_time += 1  # Increment activity timer

        # Enter auto-sleep mode if activity has been less than 2g for 10 seconds or more
        if activity_time >= 100:
            print("Entering auto-sleep mode")
            i2c.writeto_mem(ADXL345_ADDRESS, ADXL345_REG_POWER_CTL, bytes([0x04]))  # Enter standby mode
            utime.sleep_ms(1000)  # Wait for auto-sleep to take effect
            i2c.writeto_mem(ADXL345_ADDRESS, ADXL345_REG_POWER_CTL, bytes([0x08]))  # Set measurement mode
            activity_time = 0  # Reset activity timer
acclerometer()

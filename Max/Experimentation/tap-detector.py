from machine import Pin, I2C
import utime

# Define ADXL345 registers
REG_THRESH_TAP = 0x1D
REG_DUR = 0x21
REG_LATENT = 0x22
REG_WINDOW = 0x23
REG_ACT_TAP_STATUS = 0x2B
REG_TAP_AXES = 0x2A
REG_INT_ENABLE = 0x2E
REG_POWER_CTL = 0x2D

# Initialize I2C connection with ADXL345
i2c = I2C(0, scl=Pin(1), sda=Pin(0))
ADXL345_ADDR = 0x53
i2c.writeto_mem(ADXL345_ADDR, REG_POWER_CTL, b'\x08')

# Configure tap detection parameters
i2c.writeto_mem(ADXL345_ADDR, REG_THRESH_TAP, b'\x0A')  # 10 x 62.5 mg = 625 mg threshold
i2c.writeto_mem(ADXL345_ADDR, REG_DUR, b'\x30')  # 30 x 625 us = 18.75 ms duration
i2c.writeto_mem(ADXL345_ADDR, REG_LATENT, b'\x50')  # 50 x 1.25 ms = 62.5 ms latent window
i2c.writeto_mem(ADXL345_ADDR, REG_WINDOW, b'\xFF')  # 255 x 1.25 ms = 318.75 ms window

# Enable single tap interrupt
i2c.writeto_mem(ADXL345_ADDR, REG_INT_ENABLE, b'\x40')  # Enable single tap interrupt

# Set up interrupt pin
INT_PIN = Pin(19, Pin.IN)


# Interrupt handler for tap detection
def handle_interrupt(pin):
    tap_status = i2c.readfrom_mem(ADXL345_ADDR, REG_ACT_TAP_STATUS, 1)[0]
    tap_axes = i2c.readfrom_mem(ADXL345_ADDR, REG_TAP_AXES, 1)[0]
    print("Tap detected! Status: 0x{:02X}, Axes: 0x{:02X}".format(tap_status, tap_axes))
#print("going to sleep")
#machine.deepsleep(wake=Pin.IRQ_FALLING, pins=[INT_PIN])
# Attach interrupt handler to INT_PIN
INT_PIN.irq(trigger=Pin.IRQ_FALLING, handler=handle_interrupt)

# Main loop
while True:
    print("asleep")
    machine.lightsleep(10)
    print("awake")
    utime.sleep(5)
    

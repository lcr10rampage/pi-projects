#!/usr/bin/env python3
"""Pot sets stepper speed, joystick held up/down runs it forward/backward, centred stops it. LCD shows both.
Run with: ~/jupyter-env/bin/python3 ~/pi-projects/stepper-control/pot_stepper.py"""
import time
import lgpio
from smbus2 import SMBus
from RPLCD.i2c import CharLCD

# ---- ADS7830 ADC on I2C ----
ADS7830_ADDR = 0x4b
POT_CHANNEL = 0          # pot wiper on A0
JOY_Y_CHANNEL = 1        # joystick VRy on A1

# ---- Joystick ----
JOY_CENTER = 128         # resting value (from the joystick test)
JOY_DEADBAND = 40        # how far from centre before it counts as a push
JOY_UP_IS_LOW = True     # True if pushing UP makes the y reading go DOWN. Flip this if directions are reversed.

# ---- LCD (LCD1602 with PCF8574 backpack on I2C) ----
LCD_ADDRESSES = (0x27, 0x3f, 0x20, 0x38)

# ---- Stepper (ULN2003 + 28BYJ-48) ----
STEP_PINS = [17, 18, 27, 22]   # IN1, IN2, IN3, IN4
HALF_STEP = [
    (1, 0, 0, 0), (1, 1, 0, 0), (0, 1, 0, 0), (0, 1, 1, 0),
    (0, 0, 1, 0), (0, 0, 1, 1), (0, 0, 0, 1), (1, 0, 0, 1),
]

# ---- Speed mapping ----
FASTEST_DELAY = 0.0012   # seconds between half-steps at full speed (motor stalls much below ~1 ms)
SLOWEST_DELAY = 0.020    # seconds between half-steps just above the dead zone
DEAD_ZONE = 8            # pot raw readings (0..255) below this stop the motor
STEPS_PER_READ = 8       # re-read the pot and joystick every N steps
LCD_REFRESH = 0.25       # seconds between LCD updates (LCD writes are slow, so keep this modest)

# Re-running this cell is safe: closing the old handle releases every pin it claimed.
try:
    lgpio.gpiochip_close(gpio)
except (NameError, lgpio.error):
    pass
gpio = lgpio.gpiochip_open(0)
for pin in STEP_PINS:
    lgpio.gpio_claim_output(gpio, pin, 0)

try:
    lcd.close(clear=True)
except NameError:
    pass


def find_lcd(bus):
    for addr in LCD_ADDRESSES:
        try:
            bus.read_byte(addr)
            return addr
        except OSError:
            pass
    raise RuntimeError("No LCD found on I2C. Check wiring (SDA pin 3, SCL pin 5, VCC 5V, GND).")


with SMBus(1) as _bus:
    lcd = CharLCD(i2c_expander="PCF8574", address=find_lcd(_bus), port=1, cols=16, rows=2)
lcd.clear()


def read_adc(bus, channel):
    """Return 0..255 from an ADS7830 channel."""
    cmd = 0x84 | ((((channel << 2) | (channel >> 1)) & 0x07) << 4)
    return bus.read_byte_data(ADS7830_ADDR, cmd)


def pot_to_speed(raw):
    """Map a 0..255 pot reading to a speed percentage 0..100 (0 = stopped)."""
    if raw < DEAD_ZONE:
        return 0
    return round((raw - DEAD_ZONE) / (255 - DEAD_ZONE) * 100)


def speed_to_delay(percent):
    """Map 1..100% to the delay between half-steps."""
    return SLOWEST_DELAY - (percent / 100) * (SLOWEST_DELAY - FASTEST_DELAY)


def joystick_direction(bus):
    """+1 (forward) while the stick is pushed up, -1 (backward) while pushed down,
    0 (stop) when it's resting in the middle."""
    y = read_adc(bus, JOY_Y_CHANNEL)
    if y < JOY_CENTER - JOY_DEADBAND:
        return +1 if JOY_UP_IS_LOW else -1
    if y > JOY_CENTER + JOY_DEADBAND:
        return -1 if JOY_UP_IS_LOW else +1
    return 0


def direction_name(direction):
    return "Forward" if direction > 0 else "Backward" if direction < 0 else "Stopped"


def show_status(percent, direction):
    """Write both full lines, so it looks right even after lcd.clear()."""
    lcd.cursor_pos = (0, 0)
    lcd.write_string(f"Speed: {percent:4d}%".ljust(16))
    lcd.cursor_pos = (1, 0)
    lcd.write_string(f"Dir: {direction_name(direction)}".ljust(16))


def release():
    for pin in STEP_PINS:
        lgpio.gpio_write(gpio, pin, 0)


def pot_controls_motor():
    """Loop forever. Pot sets the speed (fully down = stop).
    Joystick held up = forward, held down = backward, centred = motor stops.
    Speed and direction are shown on the LCD."""
    step = 0
    direction = 0
    shown = None
    last_lcd = 0.0
    show_status(0, 0)                       # draw the screen fresh at every start
    print("Pot = speed, joystick up/down = direction. Press stop to end.")
    with SMBus(1) as bus:
        try:
            while True:
                speed = pot_to_speed(read_adc(bus, POT_CHANNEL))
                direction = joystick_direction(bus)

                # Update the LCD only when something changes, and not too often
                now = time.monotonic()
                if (speed, direction) != shown and now - last_lcd > LCD_REFRESH:
                    show_status(speed, direction)
                    shown = (speed, direction)
                    last_lcd = now
                    print(f"Speed: {speed:3d}%   Dir: {direction_name(direction):<8}", end="\r", flush=True)

                if speed == 0 or direction == 0:
                    release()
                    time.sleep(0.05)
                    continue

                delay = speed_to_delay(speed)
                for _ in range(STEPS_PER_READ):
                    for pin, on in zip(STEP_PINS, HALF_STEP[step]):
                        lgpio.gpio_write(gpio, pin, on)
                    step = (step + direction) % 8
                    time.sleep(delay)
        except KeyboardInterrupt:
            pass
        finally:
            release()
            show_status(0, 0)
            print("\nStopped.")


if __name__ == "__main__":
    try:
        pot_controls_motor()
    finally:
        lcd.close(clear=False)
        lgpio.gpiochip_close(gpio)

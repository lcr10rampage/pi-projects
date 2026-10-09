# pi-projects

Everything I build on the Raspberry Pi 4 lives here. One folder per project, plus the earlier
single-notebook experiments at the top level.

## Projects

| Folder / file | What it is | Status |
|---|---|---|
| `stepper-control/` | Pot sets stepper speed, joystick sets direction, LCD shows both. Has its own README and per-part test notebooks. | **Current, wired up now** |
| `Sentinel_box.ipynb` | Ultrasonic sensor detects someone, LCD asks for a password, keypad entry, servo unlocks. Uses an MCP23017 I/O expander. | Earlier |
| `Keypad.ipynb` | 4x3 matrix keypad scanning and code entry with green/red LEDs. | Earlier |
| `Motor.ipynb`, `mother's_day.ipynb` | First 28BYJ-48 stepper experiments (half-step sequence, button-triggered). | Earlier |
| `Ultrasonic_Sensor.ipynb`, `Detector.ipynb` | HC-SR04 distance measurement. | Earlier |
| `PIR Sensor.ipynb` | Motion detection. | Earlier |
| `Pentometor.ipynb` | First potentiometer reading through the ADS7830. | Earlier |
| `Stop_Light_Hardware.ipynb`, `pin_on.ipynb`, `led_board.ipynb` | LED basics: single pin on/off, traffic-light logic, gpiozero LEDBoard. | Earlier |

## What is wired up right now (stepper-control)

| Part | Part pin | Pi pin (physical) | BCM / signal |
|---|---|---|---|
| ADS7830 ADC | VCC, GND | 1 (3.3V), 6 (GND) | power |
| ADS7830 ADC | SDA, SCL | 3, 5 | GPIO 2 (SDA1), GPIO 3 (SCL1) |
| Potentiometer | outer legs | 3.3V rail, GND rail | from pins 1 / 6 |
| Potentiometer | middle leg | ADS7830 **A0** | analog |
| Joystick | VCC, GND | 3.3V rail, GND rail | power (3.3V, not 5V) |
| Joystick | VRy | ADS7830 **A1** | analog |
| Joystick | VRx | ADS7830 **A2** | analog, unused so far |
| Joystick | SW | not connected | |
| LCD1602 (PCF8574 backpack) | VCC, GND | 2 (5V), GND | power |
| LCD1602 | SDA, SCL | 3, 5 | shares the I2C bus |
| ULN2003 stepper driver | IN1, IN2, IN3, IN4 | 11, 12, 13, 15 | GPIO 17, 18, 27, 22 |
| ULN2003 stepper driver | +, - | 4 (5V), GND | power |
| 74HC595 shift register | on the breadboard but **not connected to anything** | | |

I2C addresses on bus 1: `0x4b` ADS7830, LCD backpack auto-detected (`0x27` / `0x3f` / `0x20` / `0x38`).

## Pi 4 GPIO header map

Physical pin numbers as on the board, BCM numbers as used in code (`GPIO.setmode(GPIO.BCM)`, gpiozero, lgpio).
**Now** = used by the current stepper-control wiring. **Earlier** = used by one of the older notebooks, so it's a pin that has worked before.

| Pin | BCM / function | Now | Earlier use | Pin | BCM / function | Now | Earlier use |
|---|---|---|---|---|---|---|---|
| 1 | 3.3V | ADC, pot, joystick | | 2 | 5V | LCD | |
| 3 | GPIO 2 (SDA1) | I2C: ADC + LCD | MCP23017, LCD (Sentinel box) | 4 | 5V | ULN2003 | |
| 5 | GPIO 3 (SCL1) | I2C: ADC + LCD | MCP23017, LCD (Sentinel box) | 6 | GND | ground rail | |
| 7 | GPIO 4 | | | 8 | GPIO 14 (TXD) | | |
| 9 | GND | | | 10 | GPIO 15 (RXD) | | |
| 11 | GPIO 17 | **ULN2003 IN1** | stepper IN1, ultrasonic echo, keypad column, LED | 12 | GPIO 18 | **ULN2003 IN2** | |
| 13 | GPIO 27 | **ULN2003 IN3** | stepper IN2, ultrasonic trigger, PIR, keypad column | 14 | GND | | |
| 15 | GPIO 22 | **ULN2003 IN4** | stepper IN3, keypad column, LED | 16 | GPIO 23 | | stepper IN4, keypad row |
| 17 | 3.3V | | | 18 | GPIO 24 | | keypad row, button |
| 19 | GPIO 10 (MOSI) | | | 20 | GND | | |
| 21 | GPIO 9 (MISO) | | | 22 | GPIO 25 | | keypad row |
| 23 | GPIO 11 (SCLK) | | | 24 | GPIO 8 (CE0) | | |
| 25 | GND | | | 26 | GPIO 7 (CE1) | | |
| 27 | ID_SD (reserved) | | | 28 | ID_SC (reserved) | | |
| 29 | GPIO 5 | | keypad column | 30 | GND | | |
| 31 | GPIO 6 | | LED | 32 | GPIO 12 | | servo (PWM) |
| 33 | GPIO 13 | | | 34 | GND | | |
| 35 | GPIO 19 | | | 36 | GPIO 16 | | LED |
| 37 | GPIO 26 | | LED, keypad column | 38 | GPIO 20 | | LED board |
| 39 | GND | | | 40 | GPIO 21 | | LED board |

Free GPIO right now: 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 19, 20, 21, 23, 24, 25, 26.
SPI is enabled (pins 19, 21, 23, 24, 26) but nothing uses it.

## Hardware on hand

| Part | Notes |
|---|---|
| ADS7830 | 8-channel 8-bit ADC, I2C address 0x4b. The only way to read analog on the Pi. |
| LCD1602 with PCF8574 backpack | 16x2 character LCD, I2C. Needs 5V. Contrast screw on the back. |
| 28BYJ-48 stepper + ULN2003 board | 4096 half-steps per turn. Needs 5V. |
| Potentiometer | |
| 2-axis joystick (VRx, VRy, SW) | Power from 3.3V so the ADC isn't over-ranged. |
| 74HC595 | Shift register (output only). Was mistaken for an ADC once. Not an ADC. |
| MCP23017 | 16-channel I/O expander, I2C. Used in the Sentinel box. |
| HC-SR04 ultrasonic, PIR sensor, 4x3 keypad, servo, LEDs | From earlier projects. |

## Pi setup

- Raspberry Pi 4 Model B, Raspberry Pi OS (trixie), Python 3.13.
- I2C and SPI are enabled in `/boot/firmware/config.txt`.
- Jupyter lives in `~/jupyter-env`. Start it with `~/jupyter-env/bin/jupyter notebook --notebook-dir=$HOME`.
- Installed in that venv: gpiozero, spidev, smbus2, RPLCD, plus the system lgpio module linked in.
- The older notebooks use `RPi.GPIO`, which on this OS is provided by `rpi-lgpio` in the system Python (`/usr/bin/python3`).
- Only one process can own a GPIO pin at a time. If a notebook says a pin is already in use, shut down the other kernels from Jupyter's Running tab.

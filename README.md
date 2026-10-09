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

How the power and signals actually run, in the order they're chained:

**Power rails on the breadboard**
- Positive rail <- Pi **3.3V** pin (pin 1).
- Negative rail <- Pi **GND** pin (pin 6).
- The rails feed the potentiometer and the joystick. Nothing else is on them.

**ADS7830 ADC (the only analog input)**
- Two wires from the ADS7830's SDA and SCL go straight to the Pi's SDA (pin 3, GPIO 2) and SCL (pin 5, GPIO 3).
- The ADS7830 is the I2C hub: the LCD's SDA and SCL plug into the breadboard and connect to the ADS7830's SDA and SCL, not directly to the Pi.
- I2C address `0x4b`.

**LCD1602 (PCF8574 backpack)**
- VCC <- Pi **5V** pin (pin 2). GND <- Pi GND pin.
- SDA and SCL -> breadboard -> ADS7830's SDA and SCL (which carry on to the Pi).
- Address auto-detected (`0x27` / `0x3f` / `0x20` / `0x38`).

**Potentiometer**
- Outer legs: breadboard positive rail (3.3V) and negative rail (GND).
- Middle leg -> ADS7830 **A0**.

**Joystick**
- VCC <- breadboard positive rail (3.3V). GND <- breadboard negative rail.
- VRx -> ADS7830 **A2**. VRy -> ADS7830 **A1**. SW not connected.

**Stepper motor (28BYJ-48 on ULN2003 driver board)**
- IN1 -> GPIO 17 (pin 11), IN2 -> GPIO 18 (pin 12), IN3 -> GPIO 27 (pin 13), IN4 -> GPIO 22 (pin 15).
- Driver + <- Pi **5V** pin (pin 4). Driver - <- Pi GND pin.

**Not connected:** the 74HC595 shift register sitting on the breadboard.

Summary table:

| Part | Part pin | Goes to |
|---|---|---|
| Breadboard + rail | | Pi pin 1 (3.3V) |
| Breadboard - rail | | Pi pin 6 (GND) |
| ADS7830 | SDA, SCL | Pi pin 3 (GPIO 2), pin 5 (GPIO 3) |
| ADS7830 | A0 | pot middle leg |
| ADS7830 | A1 | joystick VRy |
| ADS7830 | A2 | joystick VRx |
| LCD1602 | VCC, GND | Pi pin 2 (5V), Pi GND |
| LCD1602 | SDA, SCL | breadboard -> ADS7830 SDA, SCL |
| Potentiometer | outer legs | breadboard + and - rails |
| Joystick | VCC, GND | breadboard + and - rails |
| ULN2003 | IN1, IN2, IN3, IN4 | GPIO 17, 18, 27, 22 (pins 11, 12, 13, 15) |
| ULN2003 | +, - | Pi pin 4 (5V), Pi GND |

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

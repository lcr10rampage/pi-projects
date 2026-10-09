# Stepper control: pot + joystick + LCD

Turn the pot to set the motor speed. Hold the joystick up to run forward, down to run backward,
let it go to stop. A 16x2 LCD shows the speed and direction.

## Files
- `pot_stepper.ipynb` - the main notebook. Run cell 1 (setup), then cell 2 (run). Stop with the toolbar stop button.
- `pot_stepper.py`    - the same thing as a plain script: `~/jupyter-env/bin/python3 ~/pi-projects/stepper-control/pot_stepper.py`
- `tests/`            - one notebook per part, for checking wiring on its own:
  `pot_test`, `joystick_test`, `lcd_test`, `motor_test`

Only one notebook at a time can own the motor pins or the LCD. Shut others down from Jupyter's Running tab.

## Starting Jupyter
    ~/jupyter-env/bin/jupyter notebook --notebook-dir=$HOME

## Wiring
Everything analog goes through the ADS7830 ADC (I2C address 0x4b). The LCD shares the same I2C pins.

| Part | Pin | Pi connection |
|---|---|---|
| ADS7830 | VCC / GND | 3.3V / GND |
| ADS7830 | SDA / SCL | pin 3 (GPIO 2) / pin 5 (GPIO 3) |
| Pot | outer legs | 3.3V and GND |
| Pot | middle leg | ADS7830 A0 |
| Joystick | VCC / GND | 3.3V / GND |
| Joystick | VRy | ADS7830 A1 |
| Joystick | VRx | ADS7830 A2 (unused for now) |
| LCD backpack | VCC / GND | 5V / GND |
| LCD backpack | SDA / SCL | pin 3 / pin 5 (shared) |
| ULN2003 | IN1, IN2, IN3, IN4 | GPIO 17, 18, 27, 22 |
| ULN2003 | + / - | 5V / GND |

## Settings worth knowing (top of cell 1)
- `JOY_UP_IS_LOW`  flip if forward/backward are swapped
- `JOY_CENTER`, `JOY_DEADBAND`  if the stick twitches at rest
- `FASTEST_DELAY`  raise to 0.0015 if the motor stalls at full speed
- `DEAD_ZONE`  raise if the motor creeps with the pot fully down

## Setup already done on this Pi
- I2C enabled in /boot/firmware/config.txt (SPI too, though nothing uses it now)
- jupyter-env has gpiozero, spidev, smbus2, RPLCD installed, and the system lgpio module linked in
- The original 74HC595 chip on the breadboard is a shift register, not an ADC, and is not used

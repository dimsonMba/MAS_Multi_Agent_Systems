# Wiring Notes

- Connect PWM-capable pin to fan driver input (not directly to high-power fan).
- Share common ground between Arduino and fan power stage.
- Use a transistor/MOSFET and flyback diode where needed.
- Add temperature sensor according to its protocol (analog, I2C, or SPI).

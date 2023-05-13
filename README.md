# Micropython display driver for ILI9225 display

This is a Micropython display driver for the ILI9225 display. The driver provides a set of functions for initializing the display, drawing simple geometric shapes and displaying text.

The driver uses the SPI interface to communicate with the display and provides support for orientation setting.

## Hardware setup

The display driver requires a hardware SPI interface to communicate with the display. You will need to connect the SPI pins of your micro controller to the corresponding pins of the display.

You will also need to connect the following pins:

- SS (Slave Select) pin of the display to a GPIO pin on the microcontroller
- RS (Register Select) pin of the display to a GPIO pin on the microcontroller
- RST (Reset) pin of the display to a GPIO pin on the microcontroller

## Usage

The driver supports [Peter Hinch's font library and generator](https://github.com/peterhinch/micropython-font-to-py).
The font.py file in test directory was generated by:
```sh
font_to_py.py Exo2-SemiBold.ttf -x 35 font.py
```

To use the display driver, first import the necessary modules:

```python
import machine, ili9225, font
```

Then create an instance of the `SPI` and `ILI9225` classes:

```python
spi = machine.SPI(1, baudrate=40000000, sck=machine.Pin(6), mosi=machine.Pin(7))
display = ili9225.ILI9225(spi, ss_pin=10, rs_pin=8, rst_pin=9, rotation=1)
```

Once you have created an instance of the `ILI9225` class, you can use the various methods to draw on the display. For example:

```python
display.clear()
display.print('ILI9225', 0, 50, font, align=ili9225.ALIGN_CENTER, x2=display.width, fg_color=0x00FF99)
display.hline(20, 90, display.width - 40, color=0xFFFFFF)
```

## API Reference

The driver provides the following methods:

- `clear(color = COLOR_BLACK)`: Fills the entire display with the specified color.
- `hline(x, y, width, color = COLOR_WHITE)`: Draws a horizontal line of the specified width at the specified coordinates.
- `vline(x, y, height, color = COLOR_WHITE)`: Draws a vertical line of the specified height at the specified coordinates.
- `fill_rect(self, x, y, width, height, color = COLOR_WHITE)`: Fills a rectangle of the specified width and height at the specified coordinates.
- `line(x1, y1, x2, y2, color)`: Draws a line from (x1,y1) to (x2,y2) with the specified color.
- `print(self, text, x, y, font, fg_color = COLOR_WHITE, bg_color = COLOR_BLACK, align = ALIGN_LEFT, x2 = None)`: Displays text at the specified coordinates with the specified font, color and alignment (ALIGN_LEFT, ALIGN_CENTER, ALIGN_RIGHT).


The driver also provides the following constants:

- `COLOR_BLACK`: The color black (0x000000)
- `COLOR_WHITE`: The color white (0xFFFFFF)
- `ALIGN_LEFT`: Text alignment left (0)
- `ALIGN_CENTER`: Text alignment center (1)
- `ALIGN_RIGHT`: Text alignment

## License
This work is licensed under a Creative Commons Attribution 4.0 International License.
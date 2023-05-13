from machine import Pin, SPI
from micropython import const
import utime
import framebuf

# https://www.displayfuture.com/Display/datasheet/controller/ILI9225.pdf

# Register definitions

# Control registers
ILI9225_DRIVER_OUTPUT_CTRL=const(0x01)  # Driver Output Control
ILI9225_LCD_AC_DRIVING_CTRL=const(0x02)  # LCD AC Driving Control
ILI9225_ENTRY_MODE=const(0x03)  # Entry Mode
ILI9225_DISP_CTRL1=const(0x07)  # Display Control 1
ILI9225_DISP_CTRL2=const(0x08)  # Blank Period Control
ILI9225_FRAME_CYCLE_CTRL=const(0x0B)  # Frame Cycle Control
ILI9225_INTERFACE_CTRL=const(0x0C)  # Interface Control
ILI9225_OSC_CTRL=const(0x0F)  # Osc Control
ILI9225_POWER_CTRL1=const(0x10)  # Power Control 1
ILI9225_POWER_CTRL2=const(0x11)  # Power Control 2
ILI9225_POWER_CTRL3=const(0x12)  # Power Control 3
ILI9225_POWER_CTRL4=const(0x13)  # Power Control 4
ILI9225_POWER_CTRL5=const(0x14)  # Power Control 5
ILI9225_VCI_RECYCLING=const(0x15)  # VCI Recycling
ILI9225_RAM_ADDR_SET1=const(0x20)  # Horizontal GRAM Address Set
ILI9225_RAM_ADDR_SET2=const(0x21)  # Vertical GRAM Address Set
ILI9225_GRAM_DATA_REG=const(0x22)  # GRAM Data Register
ILI9225_GATE_SCAN_CTRL=const(0x30)  # Gate Scan Control Register
ILI9225_VERTICAL_SCROLL_CTRL1=const(0x31)  # Vertical Scroll Control 1 Register
ILI9225_VERTICAL_SCROLL_CTRL2=const(0x32)  # Vertical Scroll Control 2 Register
ILI9225_VERTICAL_SCROLL_CTRL3=const(0x33)  # Vertical Scroll Control 3 Register
ILI9225_PARTIAL_DRIVING_POS1=const(0x34)  # Partial Driving Position 1 Register
ILI9225_PARTIAL_DRIVING_POS2=const(0x35)  # Partial Driving Position 2 Register
ILI9225_HORIZONTAL_WINDOW_ADDR1=const(0x36)  # Horizontal Address Start Position (Window-HStart)
ILI9225_HORIZONTAL_WINDOW_ADDR2=const(0x37)  # Horizontal Address End Position   (Window-HEnd)
ILI9225_VERTICAL_WINDOW_ADDR1=const(0x38)  # Vertical Address Start Position	  (Window-VStart)
ILI9225_VERTICAL_WINDOW_ADDR2=const(0x39)  # Vertical Address End Position	  (Window-VEnd)
ILI9225_GAMMA_CTRL1=const(0x50)  # Gamma Control 1
ILI9225_GAMMA_CTRL2=const(0x51)  # Gamma Control 2
ILI9225_GAMMA_CTRL3=const(0x52)  # Gamma Control 3
ILI9225_GAMMA_CTRL4=const(0x53)  # Gamma Control 4
ILI9225_GAMMA_CTRL5=const(0x54)  # Gamma Control 5
ILI9225_GAMMA_CTRL6=const(0x55)  # Gamma Control 6
ILI9225_GAMMA_CTRL7=const(0x56)  # Gamma Control 7
ILI9225_GAMMA_CTRL8=const(0x57)  # Gamma Control 8
ILI9225_GAMMA_CTRL9=const(0x58)  # Gamma Control 9
ILI9225_GAMMA_CTRL10=const(0x59)  # Gamma Control 10

ILI9225_WIDTH=const(176)
ILI9225_HEIGHT=const(220)

COLOR_BLACK = const(0x000000)
COLOR_WHITE = const(0xFFFFFF)

ALIGN_LEFT = const(0)
ALIGN_CENTER = const(1)
ALIGN_RIGHT = const(2)

def short_delay():
    utime.sleep_ms(50)

def convert_rgb(rgb16):
    r = (rgb16 >> 16) & 0xFF
    g = (rgb16 >> 8) & 0xFF
    b = rgb16 & 0xFF
    return ((r & 0xF8) | (g >> 5), ((g & 0x1C) << 3) | (b >> 3))

class ILI9225:

    def __init__(self, spi, ss_pin, rs_pin, rst_pin, rotation=0):

        self.buffer = None

        self.rotation = rotation

        if rotation == 0 or rotation == 2:
            self.width = ILI9225_WIDTH
            self.height = ILI9225_HEIGHT
        else:
            self.width = ILI9225_HEIGHT
            self.height = ILI9225_WIDTH

        self.spi = spi

        self.ss = Pin(ss_pin, Pin.OUT)
        self.rs = Pin(rs_pin, Pin.OUT)
        self.rst = Pin(rst_pin, Pin.OUT)

        self.ss.value(1)

        self.rst.value(1)
        short_delay()
        self.rst.value(0)
        short_delay()
        self.rst.value(1)
        short_delay()

        self.tx_begin()

	    # Power-on sequence
        self.set_register(ILI9225_POWER_CTRL1, 0x0000)
        self.set_register(ILI9225_POWER_CTRL2, 0x0000)
        self.set_register(ILI9225_POWER_CTRL3, 0x0000)
        self.set_register(ILI9225_POWER_CTRL4, 0x0000)
        self.set_register(ILI9225_POWER_CTRL5, 0x0000)
        short_delay()
        # Power-on sequence
        self.set_register(ILI9225_POWER_CTRL2, 0x0018)
        self.set_register(ILI9225_POWER_CTRL3, 0x6121)
        self.set_register(ILI9225_POWER_CTRL4, 0x006F)
        self.set_register(ILI9225_POWER_CTRL5, 0x495F)
        self.set_register(ILI9225_POWER_CTRL1, 0x0F00)
        short_delay()
        self.set_register(ILI9225_POWER_CTRL2, 0x103B)
        short_delay()
        self.set_register(ILI9225_DRIVER_OUTPUT_CTRL, 0x011C)
        self.set_register(ILI9225_LCD_AC_DRIVING_CTRL, 0x0100)
        self.set_register(ILI9225_ENTRY_MODE, [0x1030, 0x1028, 0x1000, 0x1018][self.rotation])
        self.set_register(ILI9225_DISP_CTRL1, 0x0000)
        self.set_register(ILI9225_DISP_CTRL2, 0x0808)
        self.set_register(ILI9225_FRAME_CYCLE_CTRL, 0x1100)
        self.set_register(ILI9225_INTERFACE_CTRL, 0x0000)
        self.set_register(ILI9225_OSC_CTRL, 0x0D01)
        self.set_register(ILI9225_VCI_RECYCLING, 0x0020)
        short_delay()
        self.set_register(ILI9225_DISP_CTRL1, 0x1017)

        self.tx_end()


    def set_register(self, register, value):
        self.rs.value(0)
        self.spi.write(bytes([register]))
        self.rs.value(1)
        self.spi.write(bytes([value >> 8, value & 0xFF]))
        return self

    def tx_begin(self):
        self.ss.value(0)

    def tx_end(self):
        self.ss.value(1)

    # returns address as (hi, lo) tuple
    def address(self, x, y):
        if self.rotation == 0:
            return (y, x)
        elif self.rotation == 1:
            return (x, ILI9225_WIDTH - y - 1)
        elif self.rotation == 2:
            return (ILI9225_HEIGHT - y - 1, ILI9225_WIDTH - x - 1)
        elif self.rotation == 3:
            return (ILI9225_HEIGHT - x - 1, y)

    def window_begin(self, x, y, width, height):
        self.tx_begin()

        (startAddrHi, startAddrLo) = self.address(x, y)
        (endAddrHi, endAddrLo) = self.address(x + width -1, y + height - 1)

        self.set_register(ILI9225_RAM_ADDR_SET1, startAddrLo)
        self.set_register(ILI9225_RAM_ADDR_SET2, startAddrHi)

        if self.rotation == 0:
            self.set_register(ILI9225_HORIZONTAL_WINDOW_ADDR2, startAddrLo)
            self.set_register(ILI9225_VERTICAL_WINDOW_ADDR2, startAddrHi)
            self.set_register(ILI9225_HORIZONTAL_WINDOW_ADDR1, endAddrLo)
            self.set_register(ILI9225_VERTICAL_WINDOW_ADDR1, endAddrHi)
        elif self.rotation == 1:
            self.set_register(ILI9225_HORIZONTAL_WINDOW_ADDR2, endAddrLo)
            self.set_register(ILI9225_VERTICAL_WINDOW_ADDR2, startAddrHi)
            self.set_register(ILI9225_HORIZONTAL_WINDOW_ADDR1, startAddrLo)
            self.set_register(ILI9225_VERTICAL_WINDOW_ADDR1, endAddrHi)
        if self.rotation == 2:
            self.set_register(ILI9225_HORIZONTAL_WINDOW_ADDR2, endAddrLo)
            self.set_register(ILI9225_VERTICAL_WINDOW_ADDR2, endAddrHi)
            self.set_register(ILI9225_HORIZONTAL_WINDOW_ADDR1, startAddrLo)
            self.set_register(ILI9225_VERTICAL_WINDOW_ADDR1, startAddrHi)
        elif self.rotation == 3:
            self.set_register(ILI9225_HORIZONTAL_WINDOW_ADDR2, startAddrLo)
            self.set_register(ILI9225_VERTICAL_WINDOW_ADDR2, endAddrHi)
            self.set_register(ILI9225_HORIZONTAL_WINDOW_ADDR1, endAddrLo)
            self.set_register(ILI9225_VERTICAL_WINDOW_ADDR1, startAddrHi)

        self.rs.value(0)
        self.spi.write(bytes([ILI9225_GRAM_DATA_REG]))
        self.rs.value(1)

    def window_end(self):
        self.tx_end()

    def get_buffer(self, size):
        if self.buffer == None or len(self.buffer) < size:
            print("Allocating buffer of size", size)
            self.buffer = bytearray(size)
        return memoryview(self.buffer)[:size]

    def bitmap(self, bitmap, x, y, width, height, fg_color = COLOR_WHITE, bg_color = COLOR_BLACK):

        self.window_begin(x, y, width, height)

        buffer = self.get_buffer(2 * width * height)

        (fg_color0, fg_color1) = convert_rgb(fg_color)
        (bg_color0, bg_color1) = convert_rgb(bg_color)

        bit_offset = 0
        for y in range(height):
            for x in range(width):
                buffer_index = 2 * (y * width + x)
                pixel = (bitmap[bit_offset // 8] >> (7-(bit_offset % 8))) & 1
                if pixel == 0:
                    buffer[buffer_index] = bg_color0
                    buffer[buffer_index + 1] = bg_color1
                else:
                    buffer[buffer_index] = fg_color0
                    buffer[buffer_index + 1] = fg_color1
                bit_offset += 1
            if bit_offset % 8 != 0:
                bit_offset += 8 - (bit_offset % 8)

        self.spi.write(buffer)

        self.window_end()

    def print(self, text, x, y, font, fg_color = COLOR_WHITE, bg_color = COLOR_BLACK, align = ALIGN_LEFT, x2 = None):

        text_width = 0
        text_height = 0
        for char in text:
            (char_bitmap, char_height, char_width) = font.get_ch(char)
            text_width += char_width
            text_height = max(text_height, char_height)

        if x2 is None:
            x2 = text_width

        pad_left = 0 if align == ALIGN_LEFT else (x2 - x - text_width) if align == ALIGN_RIGHT else (x2 - x - text_width) // 2

        if pad_left > 0:
            self.fill_rect(x, y, pad_left, text_height, bg_color)
            x += pad_left

        for char in text:
            (char_bitmap, char_height, char_width) = font.get_ch(char)
            self.bitmap(char_bitmap, x, y, char_width, char_height, fg_color, bg_color)
            x += char_width

        if x2 > x:
            self.fill_rect(x, y, x2 - x, char_height, bg_color)
            x = x2

        return x

    def fill_rect(self, x, y, width, height, color = COLOR_WHITE):

        self.window_begin(x, y, width, height)

        (color0, color1) = convert_rgb(color)

        count = 2 * width * height
        buffer_size = min(count, 4096)
        buffer = self.get_buffer(buffer_size)

        for i in range(buffer_size // 2):
            buffer[2*i] = color0
            buffer[2*i + 1] = color1

        while count > 0:
            if count < buffer_size:
                buffer = memoryview(buffer)[:count]
            self.spi.write(buffer)
            count -= buffer_size
            self.spi.write(buffer)

        self.window_end()

    def hline(self, x, y, width, color = COLOR_WHITE):
        self.fill_rect(x, y, width, 1, color)

    def vline(self, x, y, height, color = COLOR_WHITE):
        self.fill_rect(x, y, 1, height, color)

    def clear(self, color = COLOR_BLACK):
        self.fill_rect(0, 0, self.width, self.height, color)


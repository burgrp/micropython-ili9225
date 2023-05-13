import machine, ili9225, font

spi = machine.SPI(1, baudrate=40000000, sck=machine.Pin(6), mosi=machine.Pin(7))
display = ili9225.ILI9225(spi, ss_pin=10, rs_pin=8, rst_pin=9, rotation=1)

display.clear()
display.print('ILI9225', 0, 50, font, align=ili9225.ALIGN_CENTER, x2=display.width, fg_color=0x00FF99)
display.hline(20, 90, display.width - 40, color=0xFFFFFF)
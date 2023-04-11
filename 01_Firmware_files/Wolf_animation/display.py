"""
Mt Choc KMK Display Extension

Note: This is a specific module, not a generic one.
"""

import board
import time
import random
import gc
import busio
import displayio
import adafruit_imageload

from kmk.extensions import Extension


class Display(Extension):
    # REF: https://github.com/todbot/CircuitPython_GC9A01_demos
    # REF: https://github.com/KMKfw/kmk_firmware/tree/master/kmk/extensions

    # GC9A01 display initialization sequence
    _INIT_SEQUENCE = bytearray(
        b"\xFE\x00"  # Inter Register Enable1 (FEh)
        b"\xEF\x00"  # Inter Register Enable2 (EFh)
        b"\xB6\x02\x00\x00"  # Display Function Control (B6h) [S1→S360 source, G1→G32 gate]
        b"\x36\x01\x88"  # Memory Access Control(36h) [Invert Row order, BGR color]
        b"\x3a\x01\x05"  # COLMOD: Pixel Format Set (3Ah) [16 bits / pixel]
        b"\xC3\x01\x13"  # Power Control 2 (C3h) [VREG1A = 5.06, VREG1B = 0.68]
        b"\xC4\x01\x13"  # Power Control 3 (C4h) [VREG2A = -3.7, VREG2B = 0.68]
        b"\xC9\x01\x22"  # Power Control 4 (C9h)
        b"\xF0\x06\x45\x09\x08\x08\x26\x2a"  # SET_GAMMA1 (F0h)
        b"\xF1\x06\x43\x70\x72\x36\x37\x6f"  # SET_GAMMA2 (F1h)
        b"\xF2\x06\x45\x09\x08\x08\x26\x2a"  # SET_GAMMA3 (F2h)
        b"\xF3\x06\x43\x70\x72\x36\x37\x6f"  # SET_GAMMA4 (F3h)
        b"\x66\x0a\x3c\x00\xcd\x67\x45\x45\x10\x00\x00\x00"
        b"\x67\x0a\x00\x3c\x00\x00\x00\x01\x54\x10\x32\x98"
        b"\x74\x07\x10\x85\x80\x00\x00\x4e\x00"
        b"\x98\x02\x3e\x07"
        b"\x35\x00"  # Tearing Effect Line ON (35h) [both V-blanking and H-blanking]
        b"\x21\x00"  # Display Inversion ON (21h)
        b"\x11\x80\x78"  # Sleep Out Mode (11h) and delay(120)
        b"\x29\x80\x14"  # Display ON (29h) and delay(20)
        b"\x2a\x04\x00\x00\x00\xef"  # Column Address Set (2Ah) [Start col = 0, end col = 239]
        b"\x2b\x04\x00\x00\x00\xef"  # Row Address Set (2Bh) [Start row = 0, end row = 239]
    )

    def __init__(self, imgfile):

        # Init display hardware with manual refresh control
        displayio.release_displays()

        self.display_spi = busio.SPI(clock=board.LCD_CLK, MOSI=board.LCD_DIN)

        self.display_bus = displayio.FourWire(
            self.display_spi,
            baudrate=62500000,
            command=board.LCD_DC,
            chip_select= board.LCD_CS,
            reset=board.LCD_RST)

        self.display = displayio.Display(
            self.display_bus,
            Display._INIT_SEQUENCE,
             width=240, height=240,
             backlight_pin=board.LCD_BL,
             auto_refresh=False)

        # Load up bitmap and setup tilegrid
        # The bitmap is sliced into a grid described by `grid_rows` and `grid_columns`
        # The displayio.tilegrid covers the first column of the bitmap, and the glitch/animation
        # effect procedurally swaps out the row instances from the other columns.
        # Example:
        #       A reel of 160x180px frames can be collated into a 800x180px bitmap
        #       This can be sliced into a grid of 5 columns (160px each) and 10 rows (18px each)!
        gc.collect()

        self.img, self.palette = adafruit_imageload.load(imgfile, bitmap=displayio.Bitmap, palette=displayio.Palette)

        self.wolf = displayio.TileGrid(self.img, pixel_shader=self.palette, width=12, height=10, tile_height=24, tile_width=24)

        self.wolf_group = displayio.Group()
        self.wolf_group.append(self.wolf)

        val = 0
        for loop_x, x in enumerate(range(10)):

            for loop_y, y in enumerate(range(12)):
                self.wolf[y,x] = val
                val+=1


        self.wolf_group.x = -0
        self.wolf_group.y = -0


        self.display.show(self.wolf_group)

        self.eye_level = 2
        self.eye_glow = +1
        self.animation_pause = 2

        self._toogle_animation = True


        self.old_time = time.monotonic()

        # Manual refresh
        self.display.refresh()
        gc.collect()


    def on_runtime_enable(self, sandbox):
        return

    def on_runtime_disable(self, sandbox):
        return

    def during_bootup(self, sandbox):
        return

    def before_matrix_scan(self, sandbox):
        return

    def after_matrix_scan(self, sandbox):
        return

    def before_hid_send(self, sandbox):
        return

    def after_hid_send(self, sandbox):
        self.animate_eye()


    def on_powersave_enable(self, sandbox):
        return

    def on_powersave_disable(self, sandbox):
       return


    def test(self):

        print("test succseful")
        self._toogle_animation = not self._toogle_animation

        self.wolf[3,2] = 27
        self.wolf[6,2] = 30
        self.display.refresh()

    def animate_eye(self):

        if not self._toogle_animation:
            return

        current_time = time.monotonic()

        if current_time - self.old_time < 0.1:
            return
        else:

            self.wolf[3,2] = self.eye_level*12-2
            self.wolf[6,2] = self.eye_level*12-1

            if self.eye_level == 10:
                self.eye_level = 9
                self.eye_glow *= -1
                #print(f"level has reached 10 : eye level = {self.eye_level}, eye glow = {self.eye_glow}")
                self.old_time = time.monotonic() + self.animation_pause

            elif self.eye_level == 1:

                self.wolf[3,2] = 27
                self.wolf[6,2] = 30
                self.display.refresh()

                self.old_time = time.monotonic() + self.animation_pause

                self.eye_level = 2
                self.eye_glow *= -1
                #print(f"level has reached 0 : eye level = {self.eye_level}, eye glow = {self.eye_glow}")

            else:
                self.eye_level += self.eye_glow
                #print(self.eye_level)
                self.old_time = time.monotonic()


            self.display.refresh()










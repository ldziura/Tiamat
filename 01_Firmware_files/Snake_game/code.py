"""
Mt Choc v1.0 KMK Build
"""

import board
import busio
import displayio
import adafruit_imageload

from kmk.kmk_keyboard import KMKKeyboard
from kmk.keys import KC, make_key
from kmk.scanners import DiodeOrientation
from kmk.modules.layers import Layers
from kmk.modules.combos import Combos, Chord, Sequence
from kmk.handlers.sequences import send_string
from display import Display



class MtChoc(KMKKeyboard):
    def __init__(self):
        # =============================================================
        # Scanner
        self.diode_orientation = DiodeOrientation.COL2ROW

        self.col_pins = (
            board.GP28,     # col-1 (left)
            board.GP27,
            board.GP26,
            board.GP16,
            board.GP17,
            board.GP19,
            board.GP18,     # col-16 (right)

        )

        self.row_pins = (
            board.GP0,      # row-1 (top)
            board.GP1,
            board.GP15,
            board.GP14,
            board.GP13,     # row-5 (bottom)
        )

        # =============================================================
        # Physical Layout
        self.coord_mapping = [
            0,  1,  2,  3,  4,  5, 6,
            7,  8,  9, 10, 11, 12, 13,
            14, 15, 16, 17, 18, 19, 20,
            21, 22, 23, 24, 25, 26, 27,
            28, 29, 30, 31, 32, 33, 34,
        ]

        # =============================================================
        # Extensions
        layer_ext = Layers()
        display_ext = Display()

        # Combos
        combos = Combos()

        make_key(names=('MOVEUP',),on_press=lambda *args: display_ext.move_up(),)
        make_key(names=('MOVEDOWN',),on_press=lambda *args: display_ext.move_down(),)
        make_key(names=('MOVELEFT',),on_press=lambda *args: display_ext.move_left(),)
        make_key(names=('MOVERIGHT',),on_press=lambda *args: display_ext.move_right(),)
        make_key(names=('SELECT',),on_press=lambda *args: display_ext.select(),)
        make_key(names=('SCREENSHOT',),on_press=lambda *args: display_ext.screenshot(),)
        make_key(names=('TEST',),on_press=lambda *args: display_ext.create_body(),)


        combos.combos = [
        Chord((KC.N2, KC.W), KC.MOVEUP),
        Chord((KC.S, KC.W), KC.MOVEDOWN),
        Chord((KC.Q, KC.W), KC.MOVELEFT),
        Chord((KC.E, KC.W), KC.MOVERIGHT),
        Chord((KC.ENT, KC.SPC), KC.SELECT),
        Chord((KC.C, KC.V), KC.SCREENSHOT),
        Chord((KC.N7, KC.N8), KC.TEST),
        ]

        self.modules = [layer_ext, display_ext, combos]
        # =============================================================
        # Keymap
        _______ = KC.TRNS
        XXXXXXX = KC.NO

        # Layers
        LOWER = KC.MO(1)
        RAISE = KC.MO(2)

        self.keymap = [
            [   # Base
                KC.ESC,     KC.N7,    KC.N8,    KC.N9,    KC.N0,    KC.ENT,   XXXXXXX,
                KC.LCTRL,   KC.N1,    KC.N2,    KC.N3,    KC.N4,    KC.N5,    KC.N6,
                KC.TAB,     KC.Q,     KC.W,     KC.E,     KC.R,     KC.T,     KC.Y,
                KC.LSFT,    KC.A,     KC.S,     KC.D,     KC.F,     KC.G,     KC.H,
                XXXXXXX,    XXXXXXX,  XXXXXXX,   KC.C,     KC.V,     KC.SPC,   KC.M
            ],
            [   # Lower
                KC.GRV,   _______, _______,   _______,  _______,  _______,
                _______,  _______, _______,   _______,  _______,  _______,  _______,
                _______,  _______, _______,   _______,  _______,  _______,  _______,
                _______,  _______, _______,   _______,  _______,  _______,  _______,
                _______,  _______, _______,   _______,
            ],
            [   # Raise
                KC.TILD,  _______, _______,   _______,  _______,  _______,
                _______,  _______, _______,   _______,  _______,  _______,  _______,
                _______,  _______, _______,   _______,  _______,  _______,  _______,
                _______,  _______, _______,   _______,  _______,  _______,  _______,
                _______,  _______, _______,   _______,
            ],
        ]


if __name__ == '__main__':

    print("loading kmk and badge display")

    keyboard = MtChoc()
    keyboard.go()


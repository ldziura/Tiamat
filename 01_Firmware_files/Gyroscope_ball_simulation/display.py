import board
import time
import random
import gc
import busio
import displayio
import adafruit_imageload
import random
import math

from adafruit_display_shapes.circle import Circle

from kmk.extensions import Extension

big_circle_pos = [120, 120]  # Position of the bigger circle (center of the screen)
big_circle_radius = 125


def distance(point1, point2):
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)


class PhysicManager():

    def __init__(self, G, bounce):

        self.G = G
        self.bounce = bounce

        self.balls = []

    def add_ball(self, ball):
        self.balls.append(ball)

    def remove_ball(self, ball):
        self.balls.remove(ball)

    def apply_velocity(self, ball):

        # update ball position
        ball.pos[0] += math.ceil(ball.vel[0])
        ball.pos[1] += math.ceil(ball.vel[1])

        # if position is outside the screen size, stop the ball and set position to the edge of the screen
        if ball.pos[0] < 0:
            ball.pos[0] = 0
            ball.vel[0] = 0
        elif ball.pos[0] > 240:
            ball.pos[0] = 240
            ball.vel[0] = 0

        if ball.pos[1] < 0:
            ball.pos[1] = 0
            ball.vel[1] = 0
        elif ball.pos[1] > 240:
            ball.pos[1] = 240
            ball.vel[1] = 0

        # update shape position
        ball.update_position()

    def add_gyro_velocity(self, tilt, gyro):

        max_velocity = 4

        velocity_dir = {"up": [0, 1],
                        "down": [0, -1],
                        "left": [-1, 0],
                        "right": [1, 0],
                        "center": [0, 0]}

        gyro_valx = gyro["x"]
        gyro_valy = gyro["y"]

        magnitude_x = (abs(gyro_valx) * max_velocity)/ 180
        magnitude_y = (abs(gyro_valy) * max_velocity)/ 180

        tilt_dir_x = velocity_dir[tilt["y"]]
        tilt_dir_y = velocity_dir[tilt["x"]]

        new_dir = [tilt_dir_x[0] + tilt_dir_y[0], tilt_dir_x[1] + tilt_dir_y[1]]
        new_vel = [new_dir[0] * magnitude_x, new_dir[1] * magnitude_y]

        #print(f"new_dir: {new_dir}, new_vel: {new_vel}")

        for ball in self.balls:
            ball.vel[0] += new_vel[0]
            ball.vel[1] += new_vel[1]

    def check_collisions_with_boundaries(self, ball):

        # check if ball has collided with circle boundaries
        ball.vel[1] += self.G

        self.apply_velocity(ball)

        # check if ball has collided with circle boundaries
        distance_to_center = distance(ball.pos, big_circle_pos)

        if distance_to_center + ball.radius >= big_circle_radius:
            # adjust ball velocity
            normal_vector = [(ball.pos[0] - big_circle_pos[0]) / distance_to_center,
                             (ball.pos[1] - big_circle_pos[1]) / distance_to_center]

            dot_product = ball.vel[0] * normal_vector[0] + ball.vel[1] * normal_vector[1]

            tangent_vector = [ball.vel[0] - dot_product * normal_vector[0],
                              ball.vel[1] - dot_product * normal_vector[1]]

            ball.vel = [(tangent_vector[0] - normal_vector[0]) * self.bounce,
                        (tangent_vector[1] - normal_vector[1]) * self.bounce]

            # adjust ball position to be on the circle boundary ( with int )
            ball.pos[0] = math.ceil(big_circle_pos[0] + (big_circle_radius - ball.radius) *
                                    (ball.pos[0] - big_circle_pos[0]) / distance_to_center)

            ball.pos[1] = math.ceil(big_circle_pos[1] + (big_circle_radius - ball.radius) *
                                    (ball.pos[1] - big_circle_pos[1]) / distance_to_center)

    def check_collision_between_balls(self, ball1, ball2):

        distance_to_ball = distance(ball1.pos, ball2.pos)

        # print(f"dist: {distance_to_ball}, math_dist: {math_dist}")
        # print(f"ball1 radius: {ball1.radius}, ball2 radius: {ball2.radius}")

        if distance_to_ball <= ball1.radius/2 + ball2.radius/2:
            # print(f"COLLISION : ball pos: {ball2.pos}, self pos: {ball1.pos} with dist : {distance_to_ball}")
            # print("COLLISION")
            # calculate the collision normal vector
            collision_normal = [(ball2.pos[0] - ball1.pos[0]) / distance_to_ball,
                                (ball2.pos[1] - ball1.pos[1]) / distance_to_ball]

            #normalise the collision normal vector
            collision_normal = [collision_normal[0]/math.sqrt(collision_normal[0]**2 + collision_normal[1]**2),
                                collision_normal[1]/math.sqrt(collision_normal[0]**2 + collision_normal[1]**2)]

            # calculate the relative velocity
            relative_velocity = [ball2.vel[0] - ball1.vel[0], ball2.vel[1] - ball1.vel[1]]

            # # calculate the impulse of the collision
            # impulse = [(1 + self.bounce) * relative_velocity[0] * collision_normal[0],
            #            (1 + self.bounce) * relative_velocity[1] * collision_normal[1]]

            # update the velocities of both balls based on the impulse and the collision normal vector
            # ball1.vel[0] += impulse[0]
            # ball1.vel[1] += impulse[1]
            # ball2.vel[0] -= impulse[0]
            # ball2.vel[1] -= impulse[1]

            # # adjust the positions of both balls to ensure they are no longer overlapping
            overlap = (distance_to_ball - (ball1.radius/2 + ball2.radius/2) )/2
            ball1.pos[0] -= math.ceil(overlap * -collision_normal[0])
            ball1.pos[1] -= math.ceil(overlap * -collision_normal[1])
            ball2.pos[0] += math.ceil(overlap * -collision_normal[0])
            ball2.pos[1] += math.ceil(overlap * -collision_normal[1])

            #multiply velocity by 0.9 to simulate friction
            # ball1.vel[0] *= 0.99
            # ball1.vel[1] *= 0.99
            # ball2.vel[0] *= 0.99
            # ball2.vel[1] *= 0.99

            # ball1.pos[0] -= overlap
            # ball1.pos[1] -= overlap
            # ball2.pos[0] += overlap
            # ball2.pos[1] += overlap

            # update the shapes position
            ball1.update_position()

    def update(self):



        for ball in self.balls:

            self.check_collisions_with_boundaries(ball)


        for ball1 in self.balls:
            for ball2 in self.balls:
                if ball1 != ball2:
                    self.check_collision_between_balls(ball1, ball2)




class Ball:

    def __init__(self, x, y, vel_x, vel_y, radius, color):
        self.pos = [x, y]
        self.vel = [vel_x, vel_y]

        self.radius = radius
        self.color = color

        self.shape = Circle(self.pos[0], self.pos[1], math.ceil(self.radius / 2), fill=self.color, outline=self.color)

        self.group = displayio.Group()
        self.group.append(self.shape)

    def update_velocity(self, vel_x, vel_y):
        self.vel = [vel_x, vel_y]

    def update_position(self):


        self.shape.x = self.pos[0]
        self.shape.y = self.pos[1]

        #print(f"ball pos: {self.pos}, shape pos: {self.shape.x}, {self.shape.y}")

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

    def __init__(self):

        # Init display hardware with manual refresh control
        displayio.release_displays()

        self.display_spi = busio.SPI(clock=board.LCD_CLK, MOSI=board.LCD_DIN)

        self.display_bus = displayio.FourWire(
            self.display_spi,
            baudrate=62500000,
            command=board.LCD_DC,
            chip_select=board.LCD_CS,
            reset=board.LCD_RST)

        self.display = displayio.Display(
            self.display_bus,
            Display._INIT_SEQUENCE,
            width=240, height=240,
            backlight_pin=board.LCD_BL,
            auto_refresh=False)

        # ================================

        gc.collect()

        self.physic_manager = PhysicManager(G=0, bounce=0.8)

        self.init_accel()

        # create 10 balls of random color
        self.balls = []
        for i in range(10):
            self.balls.append(
                Ball(random.randint(20, 220), random.randint(20, 220),
                     random.randint(-5, 5), random.randint(-5, 5),
                     20,
                     random.randint(0, 0xFFFFFF)))
            # add to physic manager
            self.physic_manager.add_ball(self.balls[i])

        self.global_group = displayio.Group()
        self.global_group.x = -10
        self.global_group.y = -10
        for ball in self.balls:
            self.global_group.append(ball.group)

        self.display.show(self.global_group)

        self.physic_manager.update()

        # Manual refresh
        self.display.refresh()
        gc.collect()

    def init_accel(self):

        self._qmi8658 = QMI8658_Accelerometer()
        # The accelerometer revision
        self.qmi8658rev = self._qmi8658.rev
        # Accelerometer data
        self.accel = {
            'x': 0,
            'y': 0,
            'z': 0,

        }
        # This is a multiplier based on how long
        # the device has been in motion so you can
        # ramp motion up instead of using linear.
        self.momentum = {
            'x': 0,
            'y': 0,
            'z': 0,
            'max': 10
        }
        # Gyroscope data
        self.gyro = {
            'x': 0,
            'y': 0,
            'z': 0
        }
        # These are current tilt values.  Possible
        # values are 'none', 'up' & 'down' for 'y',
        # 'none', 'left' & 'right' for 'twist'
        # and 'none', 'left' & 'right' for 'x'
        self.tilt = {
            'x': 'none',
            'y': 'none',
            'twist': 'none'
        }

        # Value of the current active tilt state
        # as well as when it was recorded. Possible values are
        # 'tilt up', 'tilt down', 'twist left', 'twist right'
        # and 'resting' for the state.  The time is the time
        # in seconds since the device was powered on.
        self.tilt_state = {'state': 'resting', 'time': time.monotonic()}
        # This is a list of the previous three tilt states
        # and when they occurred.  This is used to determine
        # if the user is shaking the device.
        self.tilt_history = [
            {'state': 'resting', 'time': time.monotonic()},
            {'state': 'resting', 'time': time.monotonic()},
            {'state': 'resting', 'time': time.monotonic()}
        ]
        self.cur_tilt_command = {'command': 'none', 'time': time.monotonic()}
        self.tilt_command_history = [
            {'command': 'none', 'time': time.monotonic()},
            {'command': 'none', 'time': time.monotonic()},
            {'command': 'none', 'time': time.monotonic()}
        ]
        # And this is the flag for activating a "combination" aka LRL
        self.combination = ''

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

    def on_powersave_enable(self, sandbox):
        return

    def on_powersave_disable(self, sandbox):
        return

    def after_hid_send(self, sandbox):
        self.move_ball()


    def move_ball(self):

        self._update_accelerometer()
        # print(f"x: xyz = {xyz}:")

        #print(f"tilt = {self.tilt}")
        #print(f"accel = {self.accel}")
        #print(f"gyro = {self.gyro}")


        # add random velocity to the ball
        #ball.vel = [new_x + random.randint(-4, 4), new_y + random.randint(-4, 4)]

        # update all the balls position with physic manager
        self.physic_manager.add_gyro_velocity(tilt=self.tilt, gyro=self.gyro)
        self.physic_manager.update()

        # print("tick")

        self.display.refresh()
        gc.collect()

    def bounce_ball(self):

        # loop over all the balls
        for ball in self.balls:
            # add random velocity to the ball
            ball.vel = [random.randint(-15, 15), random.randint(-15, 15)]

        print("Bounce!")

        # Update the accelerometer data
        # returns: nothing

    # Update the accelerometer data
    # returns: nothing
    def _update_accelerometer(self):
        xyz = self._qmi8658.read_xyz()
        accel = {}
        gyro = {}

        accel['x'] = xyz[1]
        accel['y'] = xyz[0]
        accel['z'] = xyz[2]
        gyro['x'] = xyz[3]
        gyro['y'] = xyz[4]
        gyro['z'] = xyz[5]

        # Note: my device seems to have some calibration
        #       issues.  The values are not zeroed out
        #       when the board is not moving.  I'm going
        #       to try to compensate for this by subtracting
        #       a calibration value.  Manual for now but
        #       I'll try to make this automatic in the future.
        accel['x'] += 0.01
        accel['y'] += 0.04
        accel['z'] += 1.11
        gyro['x'] -= 4.58
        gyro['y'] += 3.55
        gyro['z'] -= 0.20

        # And now we'll convert everything to integers to make math
        # easier.
        accel['x'] = int(accel['x'] * 10)
        accel['y'] = int(accel['y'] * -10)
        accel['z'] = int(accel['z'] * 10)
        gyro['x'] = int(gyro['x'])
        gyro['y'] = int(gyro['y'])
        gyro['z'] = int(gyro['z'])

        # And now we'll update the momentum values
        self.momentum['x'] += accel['x']
        self.momentum['y'] += accel['y']
        self.momentum['z'] += accel['z']
        if (self.momentum['x'] > self.momentum['max']):
            self.momentum['x'] = self.momentum['max']
        if (self.momentum['x'] < self.momentum['max'] * -1):
            self.momentum['x'] = self.momentum['max'] * -1
        if (self.momentum['y'] > self.momentum['max']):
            self.momentum['y'] = self.momentum['max']
        if (self.momentum['y'] < self.momentum['max'] * -1):
            self.momentum['y'] = self.momentum['max'] * -1
        if (self.momentum['z'] > self.momentum['max']):
            self.momentum['z'] = self.momentum['max']
        if (self.momentum['z'] < self.momentum['max'] * -1):
            self.momentum['z'] = self.momentum['max'] * -1

        # Then we'll update tilt status
        if (gyro['x'] > 0):
            self.tilt['x'] = 'right'
        elif (gyro['x'] < 0):
            self.tilt['x'] = 'left'
        else:
            self.tilt['x'] = 'center'
        if (gyro['y'] > 0):
            self.tilt['y'] = 'up'
        elif (gyro['y'] < 0):
            self.tilt['y'] = 'down'
        else:
            self.tilt['y'] = 'center'
        if (gyro['z'] > 0):
            self.tilt['twist'] = 'left'
        elif (gyro['z'] < 0):
            self.tilt['twist'] = 'right'
        else:
            self.tilt['twist'] = 'center'

        # Now we need to update the tilt_state and
        # tilt_history values based on which axis is
        # currently being tilted the strongest.
        new_tilt_state = ''
        if (abs(gyro['x']) > abs(gyro['y']) and abs(gyro['x']) > abs(gyro['z'])):
            tilt_state = 'tilt ' + self.tilt['x']
        elif (abs(gyro['y']) > abs(gyro['x']) and abs(gyro['y']) > abs(gyro['z'])):
            tilt_state = 'tilt ' + self.tilt['y']
        elif (abs(gyro['z']) > abs(gyro['x']) and abs(gyro['z']) > abs(gyro['y'])):
            tilt_state = 'twist ' + self.tilt['twist']
        else:
            tilt_state = 'resting'
        if (tilt_state != self.tilt_state):
            self.tilt_state = tilt_state
            self.tilt_history.append(tilt_state)
            if (len(self.tilt_history) > 3):
                self.tilt_history.pop(0)

                # And finally we'll check for command status
        cur_tilt_command = {'command': 'none'}
        # if the last 3 readings are the same, we'll assume
        # that the user is holding the board in that position
        if self.tilt_history[0] == 'tilt left' and self.tilt_history[1] == 'tilt right':
            cur_tilt_command = {'command': 'tilt left', 'time': time.monotonic()}
        elif self.tilt_history[0] == 'tilt right' and self.tilt_history[1] == 'tilt left':
            cur_tilt_command = {'command': 'tilt right', 'time': time.monotonic()}
        elif self.tilt_history[0] == 'tilt up' and self.tilt_history[1] == 'tilt down':
            cur_tilt_command = {'command': 'tilt up', 'time': time.monotonic()}
        elif self.tilt_history[0] == 'tilt down' and self.tilt_history[1] == 'tilt up':
            cur_tilt_command = {'command': 'tilt down', 'time': time.monotonic()}
        elif self.tilt_history[0] == 'twist left' and self.tilt_history[1] == 'twist right':
            cur_tilt_command = {'command': 'twist left', 'time': time.monotonic()}
        elif self.tilt_history[0] == 'twist right' and self.tilt_history[1] == 'twist left':
            cur_tilt_command = {'command': 'twist right', 'time': time.monotonic()}
        else:
            # self.cur_tilt_command = 'resting'
            pass

        if cur_tilt_command['command'] != 'none':
            if cur_tilt_command['command'] != self.cur_tilt_command['command']:
                self.cur_tilt_command = cur_tilt_command
                self.tilt_command_history.append(cur_tilt_command)
                if (len(self.tilt_command_history) > 3):
                    self.tilt_command_history.pop(0)

                    # Look for combinations that have occurred in the last 2 seconds
        if (
                self.tilt_command_history[0]['command'] == 'twist left' and
                self.tilt_command_history[1]['command'] == 'twist right' and
                self.tilt_command_history[2]['command'] == 'twist left' and
                time.monotonic() - self.tilt_command_history[0]['time'] < 2
        ):
            self.combination = 'LRL'

        if (
                self.tilt_command_history[0]['command'] == 'twist right' and
                self.tilt_command_history[1]['command'] == 'twist left' and
                self.tilt_command_history[2]['command'] == 'twist right' and
                time.monotonic() - self.tilt_command_history[0]['time'] < 2
        ):
            self.combination = 'RLR'

        if (
                self.tilt_command_history[0]['command'] == 'tilt up' and
                self.tilt_command_history[1]['command'] == 'tilt down' and
                self.tilt_command_history[2]['command'] == 'tilt up' and
                time.monotonic() - self.tilt_command_history[0]['time'] < 2
        ):
            self.combination = 'UDU'
        if (
                self.tilt_command_history[0]['command'] == 'tilt up' and
                self.tilt_command_history[1]['command'] == 'tilt down' and
                self.tilt_command_history[2]['command'] == 'tilt up' and
                time.monotonic() - self.tilt_command_history[0]['time'] < 2
        ):
            self.combination = 'DUD'

        if self.combination != '':
            print('combination: {}'.format(self.combination))
            self.tilt_command_history = [
                {'command': 'none', 'time': time.monotonic()},
                {'command': 'none', 'time': time.monotonic()},
                {'command': 'none', 'time': time.monotonic()}
            ]

        self.accel = accel
        self.gyro = gyro


# micro.py for the original code)
class QMI8658_Accelerometer(object):
    # Initialize the hardware
    # address: the I2C address of the device
    # returns: nothing
    def __init__(self, address=0X6B, scl=board.GP7, sda=board.GP6):
        self._address = address
        self._bus = busio.I2C(scl, sda)
        if self.who_am_i():
            self.rev = self.read_revision()
        else:
            raise Exception("QMI8658 not found")
        self.config_apply()

    # Read a byte from the specified register
    # register: the register to read from
    # returns: the byte read
    def _read_byte(self, register):
        return self._read_block(register, 1)[0]

    # Read a block of bytes from the specified register
    # register: the register to begin the read from
    # length: the number of bytes to read
    # returns: a list of bytes read
    def _read_block(self, register, length=1):
        while not self._bus.try_lock():
            pass
        try:
            rx = bytearray(length)
            self._bus.writeto(self._address, bytes([register]))
            self._bus.readfrom_into(self._address, rx)
        finally:
            self._bus.unlock()
        return rx

    # Read a 16-bit unsigned integer from the specified register
    # register: the register to begin the read from
    # returns: the 16-bit unsigned integer read
    def _read_u16(self, register):
        return (self._read_byte(register) << 8) + self._read_byte(register + 1)

    # Write a byte to the specified register
    # register: the register to write to
    # value: the byte to write
    # returns: nothing
    def _write_byte(self, register, value):
        while not self._bus.try_lock():
            pass
        try:
            self._bus.writeto(self._address, bytes([register, value]))
            # self._bus.writeto(self._address, bytes([value]))
        finally:
            self._bus.unlock()

    # Make sure this device is what it thinks it is
    # returns: True if the device is what it thinks it is, False otherwise
    def who_am_i(self):
        bRet = False
        rec = self._read_byte(0x00)
        if (0x05) == rec:
            bRet = True
        return bRet

    # Read the revision of the device
    # returns: the revision of the device
    def read_revision(self):
        return self._read_byte(0x01)

    # Apply the configuration to the device by writing to
    # the appropriate registers.  See device datasheet for
    # details on the configuration.
    # returns: nothing
    def config_apply(self):
        # REG CTRL1
        self._write_byte(0x02, 0x60)
        # REG CTRL2 : QMI8658AccRange_8g  and QMI8658AccOdr_1000Hz
        self._write_byte(0x03, 0x23)
        # REG CTRL3 : QMI8658GyrRange_512dps and QMI8658GyrOdr_1000Hz
        self._write_byte(0x04, 0x53)
        # REG CTRL4 : No
        self._write_byte(0x05, 0x00)
        # REG CTRL5 : Enable Gyroscope And Accelerometer Low-Pass Filter
        self._write_byte(0x06, 0x11)
        # REG CTRL6 : Disables Motion on Demand.
        self._write_byte(0x07, 0x00)
        # REG CTRL7 : Enable Gyroscope And Accelerometer
        self._write_byte(0x08, 0x03)

    # Read the raw accelerometer and gyroscope data from the device
    # returns: a list of 6 integers, the first 3 are the accelerometer
    #          data, the last 3 are the gyroscope data
    def read_raw_xyz(self):
        xyz = [0, 0, 0, 0, 0, 0]
        raw_timestamp = self._read_block(0x30, 3)
        raw_acc_xyz = self._read_block(0x35, 6)
        raw_gyro_xyz = self._read_block(0x3b, 6)
        raw_xyz = self._read_block(0x35, 12)
        timestamp = (raw_timestamp[2] << 16) | (raw_timestamp[1] << 8) | (raw_timestamp[0])
        for i in range(6):
            # xyz[i]=(raw_acc_xyz[(i*2)+1]<<8)|(raw_acc_xyz[i*2])
            # xyz[i+3]=(raw_gyro_xyz[((i+3)*2)+1]<<8)|(raw_gyro_xyz[(i+3)*2])
            xyz[i] = (raw_xyz[(i * 2) + 1] << 8) | (raw_xyz[i * 2])
            if xyz[i] >= 32767:
                xyz[i] = xyz[i] - 65535
        return xyz

    # Read the accelerometer and gyroscope data from the device and return
    # in human-readable format.
    # returns: a list of 6 floats, the first 3 are the accelerometer
    #         data, the last 3 are the gyroscope data
    def read_xyz(self):
        xyz = [0, 0, 0, 0, 0, 0]
        raw_xyz = self.read_raw_xyz()
        # QMI8658AccRange_8g
        acc_lsb_div = (1 << 12)
        # QMI8658GyrRange_512dps
        gyro_lsb_div = 64
        for i in range(3):
            xyz[i] = raw_xyz[i] / acc_lsb_div  # (acc_lsb_div/1000.0)
            xyz[i + 3] = raw_xyz[i + 3] * 1.0 / gyro_lsb_div
        return xyz



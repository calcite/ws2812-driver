from __future__ import print_function

import alsaaudio
import struct
import numpy as np
import time


class Ws2812Driver:

    _CONV_TABLE = None

    def __init__(self, leds, device='hw:CARD=snddaudio'):
        """

        :param leds: number of leds for driver
        :param device: refers to sound card
        Initialized control over sound card with fixed parametes
        Sample rate 88,2 kHz provides 0,3543us period of logic level.

        """

        self.num_leds = leds
        self._device = alsaaudio.PCM(device=device)
        self._device.setformat(alsaaudio.PCM_FORMAT_U16_BE)
        ch = 2
        sr = 88200
        period_size = 2048
        self._device.setchannels(ch)
        self._device.setrate(sr)
        self._device.setperiodsize(period_size)
        zeros = bytes(period_size * ch * 2 * [0])
        self._device.write(zeros)
        self._segments = []
        self.data = np.zeros((self.num_leds,3))
        self.overlay_matrix = np.ones((self.num_leds, 1))

        if not self._CONV_TABLE:
            self.__class__._CONV_TABLE = self._conv_table()

    def close(self):
        self._device.close()

    @classmethod
    def _conv_table(cls):
        """
        WS2812 works with period 1,23us±600ns
        Driver use 3x0,3543us long period to define logical value.
        Conversion table provides convert to hardware requirements:
        T0H --> 0 code, high voltage time   0,4us±150ns    --> 0 code
        T1H --> 1 code, high voltage time   0,8us±150ns    --> 11 code
        T0L --> 0 code, low voltage time    0.85us±150ns   --> 00 code
        T1L --> 0 code, low voltage time    0.45us±150ns   --> 0 code
        e.g. log. 1 --> T1H + T1L is coded as 110.
        """

        table = 256 * ['']

        for i in range(256):

            bin_string = ''
            for num in '{0:08b}'.format(i):
                add_string = '100' if num == '0' else '110'
                bin_string = bin_string + add_string
                new_string = bin_string[16:] + bin_string[8:16] + bin_string[:8]
            table[i] = struct.pack('L', int(new_string, 2))[:-1]

        return table

    @classmethod
    def _print_nice(cls, bts):
        """
        It shows sent bits to device.
        """
        temp = ":".join(["{0:08b}".format(x) for x in bts])
        print(temp)

    @classmethod
    def _convert(cls, byte_val):
        """
        Select 24bit for one colour from convertion table
        """
        assert byte_val <= 256
        sel = cls._CONV_TABLE[byte_val]

        return sel

    @classmethod
    def _set_rgb(cls, red, green, blue):
        """
        Create GRB string of 72 bits for one led segment
        """
        r = cls._convert(int(red))
        g = cls._convert(int(green))
        b = cls._convert(int(blue))
        grb = g + r + b

        return grb

    def reset_data(self):

        data = bytes(((250 // 8) + 1) * [0])
        self._device.write(data)

    def frame_data(self, frame_buffer):
        """
        Data from frame_buffer is transformed to readable frame for sending to device.
        Each frame starts with RES low voltage time, which lasts above 50us.
        """

        data = bytes(((250 // 8) + 1) * [0])

        for item in range(len(frame_buffer)):
            row = frame_buffer[item]
            data = data + self._set_rgb(*row)

        end = self.num_leds - len(frame_buffer)
        data = data + end * self._set_rgb(0, 0, 0)
        periodsize = 2048
        prev_lenght = len(data)

        if prev_lenght % 2 != 0:
            data = data + bytes(1*[0])

        data = bytes([c for t in zip(data[1::2], data[::2]) for c in t])

        lenght = len(data)
        diff = periodsize * 4 - lenght
        data = data + bytes(diff * [0])

        self._device.write(data)

        return data

    def show_raw(self, pixels):
        """
        In case of any change is callng to redraw function.
        """

        self.data = pixels
        self.redraw()

    def show_scale(self, min_temp, max_temp, temp, bright= 100, heatmap=None,
                   reverse=None):

        """
        This function shows thermometer or any scale-based measurement
        Colour for each LED is calculated from defined heatmap for any number
        of LEDS and origin.
        In case of reversal mode is final data frame reversed.


        :param min_temp: Minimum temperature
        :param max_temp: Maximum temperature
        :param temp: Actual temperature(in range of previous parameters)
        :param bright: Allow to set brightness (0-100)
        :param heatmap: Used just in case own-defined heatmap
        :param reverse: Parameter 1 sets reverse scale
        :return:
        """
        num = self.num_leds
        frame_buffer = np.array([[0, 0, 0]])

        if heatmap is None:
            heatmap = [(0, 100, (0, 0, 255)),
                       (400, 500, (0, 255, 0)),
                       (900, 1000, (255, 0, 0))]

        br = bright / 100
        i = 0
        leds = (num / 1000)
        range_rel = max_temp - min_temp
        show_rel = temp - min_temp
        temp_abs = 1000 * (show_rel / range_rel)

        for area in heatmap:

            if i < (len(heatmap) - 1):
                next_heatmap = heatmap[i + 1]
                i = i + 1

            l_min = area[0]
            l_max = area[1]
            r1, g1, b1 = area[2]
            r1, g1, b1 = r1 * br, g1 * br, b1 * br
            step_size = next_heatmap[0] - l_max
            r2, g2, b2 = next_heatmap[2]
            r2, g2, b2 = r2 * br, g2 * br, b2 * br
            next_min = l_max + step_size
            step_leds = (next_min - l_max) * leds
            gap_r = (r2 - r1) / step_leds
            gap_g = (g2 - g1) / step_leds
            gap_b = (b2 - b1) / step_leds

            for led in range(int((l_min * leds)), int(l_max * leds)):

                if led < temp_abs * leds:
                    frame_buffer = np.concatenate((frame_buffer, [[r1, g1, b1]]))

                else:
                    frame_buffer = np.concatenate((frame_buffer, [[0, 0, 0]]))

            for led in range((int(l_max * leds)), (int(next_min * leds))):

                if led < temp_abs * leds:
                    r1, g1, b1 = r1 + gap_r, g1 + gap_g, b1 + gap_b
                    frame_buffer = np.concatenate((frame_buffer, [[r1, g1, b1]]))

                else:
                    frame_buffer = np.concatenate((frame_buffer, [[0, 0, 0]]))

        if reverse == 1:
            frame_buffer = frame_buffer[::-1]
        frame_buffer = np.delete(frame_buffer, 0, 0)
        frame_buffer = frame_buffer[:num, :]
        self.show_raw(frame_buffer)

    def add_segment(self, origin, num_leds, alfa):

        """
        Add a new segment
        :param origin: Set first LED on strip.
        :param num_leds: Set number of used LEDs
        :param alfa: Set transparency
        :return:
        """

        last_layer = self._segments[-1].layer if self._segments else 0
        temp = LineSegment(origin, num_leds, alfa, last_layer+1, self)
        self._segments.append(temp)
        self._update_overlay_matrix()

        return temp

    def _update_overlay_matrix(self):
        """
        Overlay matrix is used for set number of layer.
        """

        temp_matrix = np.ones((self.num_leds, 1))

        for segment in self._segments:

            overlay = temp_matrix[segment.origin:segment.origin + segment.num_leds]
            overlay += 1

        self.overlay_matrix = temp_matrix

    def redraw(self):
        """
        Redraw function provides for each pixels right drawing.
        In case of multiple layers are pixels averaging.
        """

        add_matrix = self.overlay_matrix
        temp = np.copy(self.data)

        for segment in self._segments:
            overlapped = temp[segment.origin:segment.origin + segment.num_leds]
            overlapped += segment.data * (1 - (segment.alfa / 255))

        for color in temp.T:
            color = temp/add_matrix

        temp = np.where(temp > 255, 255, temp)
        self.frame_data(temp)

    def show_animation(self, speed):
        """
        Show a fast trail on LED strip.
        Number of leds is parameter for how long will trail be.
        """
        speed = (1.1 - (speed/100))/10
        num = self.num_leds
        step_size = 255/num
        frame = np.zeros((num, 3))

        for m in range(num):
            frame[m, :] = 255, 255, 255
            pos = 255
            for o in range(m):
                pos -= step_size
                frame[m-o-1, :] = pos, pos, pos
        for p in range(num+1):
            zer = np.zeros((num-p, 3))
            frame1 = np.insert(zer, 0, frame, axis=0)
            frame2 = np.delete(frame1, range(0, num-p), axis=0)
            self.show_raw(frame2)
            time.sleep(speed)
        for n in range(116-num):
            self.origin += 1
            self.show_raw(frame)
            time.sleep(speed)
        for o in range(0, num-1):
            del_row = num-o-1
            self.origin += 1
            frame = np.delete(frame, del_row, axis=0)
            self.show_raw(frame)
            time.sleep(speed)

        frame = np.zeros((num, 3))
        self.origin = 1
        self.show_raw(frame)
        time.sleep(speed)


class LineSegment(Ws2812Driver):

    def __init__(self, origin, num_leds, alfa, layer, driver):
        """

        :param origin: Set first LED on strip
        :param num_leds: Set number of LEDs
        :param alfa: Set transparency
        :param layer: Set number of layers
        :param driver: Set used driver
        """
        self._num_leds = num_leds
        self._origin = origin
        self.alfa = alfa
        self.layer = layer
        self._driver = driver
        self.data = np.zeros(0)

    @property
    def num_leds(self):
        return self._num_leds

    @num_leds.setter
    def num_leds(self, value):
        self._num_leds = value
        self._driver._update_overlay_matrix()

    @property
    def origin(self):
        return self._origin

    @origin.setter
    def origin(self, value):
        self._origin = value
        self._driver._update_overlay_matrix()

    def show_raw(self, frame_data):
        self.data = frame_data
        self._driver.redraw()

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `ws2812_driver` package."""


import unittest
import numpy as np
import time


from ws2812_driver import Ws2812Driver

class TestWs2812_driver(unittest.TestCase):
    """Tests for `ws2812_driver` package."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures, if any."""
        cls.pasek = Ws2812Driver(116)

    @classmethod
    def tearDownClass(cls):
        """Tear down test fixtures, if any."""
        cls.pasek.close()

    def test_01_line_segment(self):


        self.pasek.reset_data()

        layer1 = self.pasek.add_segment(0,116,0)
        layer1.show_scale(10,110,70,100)

        layer2 = self.pasek.add_segment(0, 5, 100)
        layer2.show_animation(100)

















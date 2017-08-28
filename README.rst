=============
WS2812_driver
=============


.. image:: https://img.shields.io/pypi/v/ws2812_driver.svg
        :target: https://pypi.python.org/pypi/ws2812_driver

.. image:: https://img.shields.io/travis/phephik/ws2812_driver.svg
        :target: https://travis-ci.org/phephik/ws2812_driver

.. image:: https://readthedocs.org/projects/ws2812-driver/badge/?version=latest
        :target: https://ws2812-driver.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://pyup.io/repos/github/phephik/ws2812_driver/shield.svg
     :target: https://pyup.io/repos/github/phephik/ws2812_driver/
     :alt: Updates

Python driver for controlling  WS2812(B) or any comparable RGB adressable LED strip over I2S bus.


* Free software: BSD license
* Documentation: https://ws2812-driver.readthedocs.io.

Overview
========
The repository includes a python code needed to build an LED strip scale thermometer:

This code for visualization includes functions:

* scale thermometer
* demo trail


Prerequisites
=============

This project is based on I2S bus, so use DOUT pin of I2S bus on your device.
Before you run code, you should make sure that you work with:

* Linux embedded platform (recommended Armbian 5.30 stable Ubuntu 16.04.2)
* ws2812b addressable led strip (of any size)
* 5V power supply (recommended)

Python Dependencies
===================

Compatible with Python 3.5 (including pyalsaaudio package)

* Tested on Debian-based Armbian (Armbian 5.30 stable Ubuntu 16.04.2).
* Linux kernel version at least 3.4.113

Installing dependencies
-----------------------

You will need to set up a I2S device with following commands:

.. code-block:: bash

    cd /boot
    sudo bin2fex script.bin script.fex
    sudo nano script.fex

In next step change following attributes in script:

.. code-block:: bash

    [twi1]
    twi_used = 0

    [pcm0]
    daudio_used = 1
    sample_resolution = 16
    slot_width_select = 16
    pcm_lrck_period = 16
    slot_width = 16

Save your changes and convert file again:

.. code-block:: bash

    sudo fex2bin script.fex script.bin

Reboot your device. After reboot try command:

.. code-block:: bash

    aplay -l

It looks like:

.. code-block:: bash

    **** List of PLAYBACK Hardware Devices ****
    card 0: audiocodec [audiocodec], device 0: SUNXI-CODEC sndcodec-0 []
    Subdevices: 1/1
    Subdevice #0: subdevice #0
    card 1: snddaudio [snddaudio], device 0: SUNXI-TDM0 snddaudio-0 []
    Subdevices: 1/1
    Subdevice #0: subdevice #0
    card 2: sndhdmi [sndhdmi], device 0: SUNXI-HDMIAUDIO sndhdmi-0 []
    Subdevices: 1/1
    Subdevice #0: subdevice #0

"card 1" is the one we want.

Demo trail
==========
* Function show_animation will display fast moving trail.
* You can change speed of trail (0-100)



Scale thermometer
=================

* Function meas_temperature sets up led string as a thermometer or scale display.
* As arguments you have to define number of leds, minimum, maximum, temperature.


.. code-block:: bash

    def meas_temperature(num_leds, min_temp, max_temp, temp, bright=100, heatmap=None, reverse=None)

* Optional arguments are brightness, your own-defined heatmap and reverse mode


.. code-block:: bash

        heatmap = [(0,   100,  (0, 0, 256)),
                   (400, 500,  (0, 256, 0)),
                   (900, 1000, (256, 0, 0))]

* You can define heatmap with fixed limits for each color e.g. (0, 150, (10, 256, 20). Coulours among are set transiently.


Credits
=======

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage

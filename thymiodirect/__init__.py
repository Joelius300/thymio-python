# This file is part of thymiodirect.
# Copyright 2020 ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE,
# Miniature Mobile Robots group, Switzerland
# Author: Yves Piguet
#
# SPDX-License-Identifier: BSD-3-Clause

"""
Communication with Thymio II robot
==================================

This module provides support to connect to a Thymio II robot with its native
binary protocol via a serial port (virtual port over a wired USB or wireless
USB dongle) or a TCP port (asebaswitch or Thymio simulator).

High level example
-------

from thymiodirect import ThymioObserver, SingleSerialThymioRunner
from thymiodirect.thymio_constants import PROXIMITY_FRONT_BACK, MOTOR_LEFT, MOTOR_RIGHT, BUTTON_CENTER, LEDS_TOP


class HandAvoider(ThymioObserver):
    def __init__(self):
        super().__init__()
        self.prox_prev = None

    def _update(self):
        prox = (self.th[PROXIMITY_FRONT_BACK][5] - self.th[PROXIMITY_FRONT_BACK][2]) // 10

        if prox != self.prox_prev:
            self.th[MOTOR_LEFT] = prox
            self.th[MOTOR_RIGHT] = prox
            print(prox)
            if prox > 5:
                self.th[LEDS_TOP] = [0, 32, 0]
            elif prox < -5:
                self.th[LEDS_TOP] = [32, 32, 0]
            elif abs(prox) < 3:
                self.th[LEDS_TOP] = [0, 0, 32]
            self.prox_prev = prox
        if self.th[BUTTON_CENTER]:
            print("Center button pressed")
            self.stop()


if __name__ == "__main__":
    SingleSerialThymioRunner({BUTTON_CENTER, PROXIMITY_FRONT_BACK, MOTOR_LEFT, MOTOR_RIGHT}, HandAvoider(), 0.1).run()


Low level example
-------

# import the required classes
from thymiodirect.thymio_serial_ports import ThymioSerialPort
from thymiodirect import Thymio

# get the serial port the Thymio is connected to
# (depending on your configuration, the default port is not what you want)
port = ThymioSerialPort.default_device()

# create a Thymio connection object with a callback to be notified when
# the robot is ready and start the connection (or just wait a few seconds)
th = Thymio(serial_port=port,
            on_connect=lambda node_id:print(f"{node_id} is connected"))
th.connect()

# get id of the first (or only) Thymio
id = th.first_node()

# get a variable
th[id]["prox.horizontal"]

# set a variable (scalar or array)
th[id]["leds.top"] = [0, 0, 32]

# define a function called after new variable values have been fetched
prox_prev = 0
def obs(node_id):
    global prox_prev
    prox = (th[node_id]["prox.horizontal"][5]
            - th[node_id]["prox.horizontal"][2]) // 10
    if prox != prox_prev:
        th[node_id]["motor.left.target"] = prox
        th[node_id]["motor.right.target"] = prox
        print(prox)
        if prox > 5:
            th[id]["leds.top"] = [0, 32, 0]
        elif prox < -5:
            th[id]["leds.top"] = [32, 32, 0]
        elif abs(prox) < 3:
            th[id]["leds.top"] = [0, 0, 32]
        prox_prev = prox
    if th[node_id]["button.center"]:
        print("button.center")
        os._exit(0) # forced exit despite coroutines

# install this function
th.set_variable_observer(id, obs)
"""

from .connection import Connection
from .thymio import Thymio
from .thymio_observer import ThymioObserver
from .single_serial_thymio_runner import SingleSerialThymioRunner

import time
from abc import ABC, abstractmethod

from .thymio import Thymio


class ThymioObserver(ABC):
    """
    Abstract observer to execute code in an update loop after the newest values are fetched.
    Only one observer can run per node; you have to implement a combined observer to run multiple observers per thymio node.

    Example
    -------

    from thymiodirect import ThymioObserver
    from thymiodirect.thymio_constants import PROXIMITY_FRONT_BACK, MOTOR_LEFT, MOTOR_RIGHT, BUTTON_CENTER


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
                    self.th["leds.top"] = [0, 32, 0]
                elif prox < -5:
                    self.th["leds.top"] = [32, 32, 0]
                elif abs(prox) < 3:
                    self.th["leds.top"] = [0, 0, 32]
                self.prox_prev = prox
            if self.th[BUTTON_CENTER]:
                print("Center button pressed")
                self.stop()
    """

    def __init__(self):
        self.thymio: Thymio = None
        self.th: Thymio.Node = None
        self._node_id: int = None
        self._done = False

    @property
    def done(self) -> bool:
        """
        Gets whether the observer is done observing.
        """
        return self._done

    def set_thymio_node(self, thymio: Thymio, node_id: int):
        """
        Sets the thymio node this observer runs on
        """
        self.thymio = thymio
        self.th = thymio[node_id]
        self._node_id = node_id

    def run(self):
        """
        Run the observer until it is stopped or interrupted (blocking).
        Before running the observer, you need to set the thymio node (set_thymio_node)!
        """
        self.start()
        self.block_until_done()

    def _observe(self, node_id):
        if self.done:
            return

        if node_id != self._node_id:
            print("Observe called by a node that is not the registered thymio node of this observer!")

        self._update()

    @abstractmethod
    def _update(self):
        """
        Called everytime the values are fetched from the thymio (refreshing_rate configurable on the thymio itself).
        """
        pass

    def _reset(self):
        self._done = False

    def start(self):
        """
        Registers and enables the observer without blocking (returns immediately).
        Before starting the observer, you need to set the thymio node (set_thymio_node)!
        """
        self._reset()
        self.thymio.set_variable_observer(self._node_id, self._observe)

    def block_until_done(self):
        """
        Blocks until the observer is done (stopped) or interrupted.
        """
        while not self.done:
            try:
                time.sleep(.05)
            except KeyboardInterrupt:
                self.stop()

    def stop(self):
        """
        Stop operation and prevent _update from being called again.
        This also stops run() and block_until_done() from blocking and makes them return.
        """
        self._done = True
        self.thymio.set_variable_observer(self._node_id, lambda n: None)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

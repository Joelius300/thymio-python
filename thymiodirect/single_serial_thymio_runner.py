import time
from typing import Optional

from .thymio import Thymio
from .thymio_observer import ThymioObserver


class SingleSerialThymioRunner:
    """
    A runner that takes a ThymioObserver and runs it on a single thymio node connected via serial (USB dongle or cable).

    ----------

    Example:

    SingleSerialThymioRunner({BUTTON_CENTER, PROXIMITY_FRONT_BACK, MOTOR_LEFT, MOTOR_RIGHT}, HandAvoider(), 0.1).run()
    """

    def __init__(self,
                 refreshing_coverage: set,
                 observer: ThymioObserver,
                 refreshing_rate=0.1,
                 serial_port: Optional[str] = None,
                 connection_delay=1.5
                 ):
        self.thymio = Thymio(refreshing_coverage=refreshing_coverage,
                             refreshing_rate=refreshing_rate,
                             serial_port=serial_port,
                             on_comm_error=lambda e: self._on_error(e),
                             discover_rate=1)
        self.observer = observer
        self._connection_delay = connection_delay

    def _on_error(self, error):
        print(error)
        self.observer.stop()

    def run(self):
        """
        Runs the specified observer on the first (and only) thymio node connected via serial until the observer is
        stopped or interrupted. Designed to run only once per thymio and observer even though it might work multiple times.
        """
        with self.thymio, self.observer:
            self.thymio.connect()

            time.sleep(self._connection_delay)

            id = self.thymio.first_node()
            print_thymio_functions_events(self.thymio, id)
            self.observer.set_thymio_node(self.thymio, id)

            self.observer.run()  # blocks until done


def print_thymio_functions_events(th: Thymio, node_id: int):
    print(f"id: {node_id}")
    print(f"variables: {th.variables(node_id)}")
    print(f"events: {th.events(node_id)}")
    print(f"native functions: {th.native_functions(node_id)[0]}")

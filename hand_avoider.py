from thymiodirect import ThymioObserver, SingleSerialThymioRunner
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


if __name__ == "__main__":
    SingleSerialThymioRunner({BUTTON_CENTER, PROXIMITY_FRONT_BACK, MOTOR_LEFT, MOTOR_RIGHT}, HandAvoider(), 0.1).run()

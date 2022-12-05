import YB_Pcb_Car
import time

car = YB_Pcb_Car.YB_Pcb_Car()

car.Ctrl_Servo(1, 33)
time.sleep(0.5)

car.Ctrl_Servo(2, 110)
time.sleep(0.5)

del car
import YB_Pcb_Car
import time

# adsfa
car = YB_Pcb_Car.YB_Pcb_Car()

car.Ctrl_Servo(1, 90)
time.sleep(0.5)

car.Ctrl_Servo(2, 90)
time.sleep(0.5)

car.Ctrl_Servo(1, 0)
time.sleep(0.5)

car.Ctrl_Servo(2, 0)
time.sleep(0.5)

car.Ctrl_Servo(1, 180)
time.sleep(0.5)

car.Ctrl_Servo(2, 180)
time.sleep(0.5)

del car
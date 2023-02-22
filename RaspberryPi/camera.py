import YB_Pcb_Car
import time

# 주행 시작 전에 카메라 위치 설정

car = YB_Pcb_Car.YB_Pcb_Car()

car.Ctrl_Servo(1, 33)
time.sleep(0.5)

car.Ctrl_Servo(2, 120)
time.sleep(0.5)

del car
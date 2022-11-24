import YB_Pcb_Car
import time

car = YB_Pcb_Car.YB_Pcb_Car()

# car.Control_Car(30, 60)     # 완만
# time.sleep(2)
#
# # car.Control_Car(10, 60)   #
# # time.sleep(2)
#
# car.Control_Car(10, 100)    #거의 유턴
# time.sleep(2)
#
# car.Control_Car(30, 60)
# time.sleep(2)

car.Car_Run(30, 30)
time.sleep(2)


car.Car_Stop()

del car
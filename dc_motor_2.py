import YB_Pcb_Car
import time

car = YB_Pcb_Car.YB_Pcb_Car()


car.Car_Run(61, 30)
time.sleep(5)

car.Car_Stop()
# car.Car_Run(50, 50)
# time.sleep(2)
# car.Car_Stop()

# car.Car_Back(50, 50)
# time.sleep(2)
# car.Car_Stop()

del car

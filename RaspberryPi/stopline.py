import RPi.GPIO as GPIO
import time
import YB_Pcb_Car

Tracking_Right1 = 11
Tracking_Right2 = 7
Tracking_Left1 = 13
Tracking_Left2 = 15

GPIO.setmode(GPIO.BOARD)

GPIO.setwarnings(False)

GPIO.setup(Tracking_Left1, GPIO.IN)
GPIO.setup(Tracking_Left2, GPIO.IN)
GPIO.setup(Tracking_Right1, GPIO.IN)
GPIO.setup(Tracking_Right2, GPIO.IN)


def restricting():
    Tracking_Left1Value = GPIO.input(Tracking_Left1)
    Tracking_Left2Value = GPIO.input(Tracking_Left2)
    Tracking_Right1Value = GPIO.input(Tracking_Right1)
    Tracking_Right2Value = GPIO.input(Tracking_Right2)
    count = Tracking_Left1Value + Tracking_Left2Value + Tracking_Right1Value + Tracking_Right2Value
    print("values: ", Tracking_Left1Value, Tracking_Left2Value, Tracking_Right1Value, Tracking_Right2Value)

    # 0000
    if count >= 3:
        return 1
    elif Tracking_Left1Value:
        return 2
    elif Tracking_Left2Value:
        return 3
    elif Tracking_Right1Value:
        return 4
    elif Tracking_Right2Value:
        return 5
    else:
        return 0


if __name__ == "__main__":
    car = YB_Pcb_Car.YB_Pcb_Car()
    while True:
        try:
            isStopLine = restricting()
            if isStopLine:
                pass
                car.Car_Stop()
                print("stop*******")
                time.sleep(1)
                car.Car_Run(40, 40)
                time.sleep(1)
            else:
                pass
                car.Car_Run(40, 40)
                time.sleep(0.05)
                print("Run---")
        except KeyboardInterrupt:
            car.Car_Stop()
            del car
            GPIO.cleanup()
            print("terminated...")
            exit(0)

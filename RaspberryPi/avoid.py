import RPi.GPIO as GPIO
import time
import YB_Pcb_Car

GPIO.setmode(GPIO.BOARD)

GPIO.setwarnings(False)

EchoPin = 18
TrigPin = 16

GPIO.setup(EchoPin, GPIO.IN)
GPIO.setup(TrigPin, GPIO.OUT)


# Ultrasonic function
def Distance():
    GPIO.output(TrigPin, GPIO.LOW)
    time.sleep(0.000002)
    GPIO.output(TrigPin, GPIO.HIGH)
    time.sleep(0.000015)
    GPIO.output(TrigPin, GPIO.LOW)

    t3 = time.time()

    while not GPIO.input(EchoPin):
        t4 = time.time()
        if (t4 - t3) > 0.03:
            return -1
    t1 = time.time()
    while GPIO.input(EchoPin):
        t5 = time.time()
        if (t5 - t1) > 0.03:
            return -1

    t2 = time.time()
    return ((t2 - t1) * 340 / 2) * 100


def Distance_test():
    num = 0
    ultrasonic = []
    while num < 5:
        distance = Distance()
        while int(distance) == -1:
            distance = Distance()
        while int(distance) >= 500 or int(distance) == 0:
            distance = Distance()
        ultrasonic.append(distance)
        num = num + 1
    distance = (ultrasonic[1] + ultrasonic[2] + ultrasonic[3]) / 3
    return distance


def avoid():
    distance = Distance_test()
    if distance < 15:
        return True


if __name__ == '__main__':
    try:
        car = YB_Pcb_Car.YB_Pcb_Car()
        while True:
            isAvoid = avoid()
            if isAvoid:
                car.Car_Stop()
            else:
                car.Car_Run(40, 40)
    except KeyboardInterrupt:
        car.Car_Stop()
        del car
        print("Ending")
        GPIO.cleanup()

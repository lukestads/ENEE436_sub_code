# ...existing code...
import RPi.GPIO as GPIO
import time

# --- Pin Definitions (using BCM numbering) ---
IN1 = 17  # Motor 1 Input A (BCM)
IN2 = 27  # Motor 1 Input B (BCM)
IN3 = 22  # Motor 2 Input A (BCM)
IN4 = 23  # Motor 2 Input B (BCM)

EN = 24   # Enable for motor pair 1 (BCM)

IN1_2 = 5   # Motor 3 Input A (BCM)
IN2_2 = 6   # Motor 3 Input B (BCM)
IN3_2 = 13  # Motor 4 Input A (BCM)
IN4_2 = 26  # Motor 4 Input B (BCM)
EN_2 = 16   # Enable for motor pair 2 (BCM)

# --- GPIO Setup ---
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)  # Use BCM numbering (matches the pin constants above)

ALL_PINS = [IN1, IN2, IN3, IN4, EN, IN1_2, IN2_2, IN3_2, IN4_2, EN_2]

for p in ALL_PINS:
    GPIO.setup(p, GPIO.OUT)
    GPIO.output(p, GPIO.LOW)  # initialize outputs low

MOTOR1_PINS = [IN1, IN2, IN3, IN4, EN]
MOTOR2_PINS = [IN1_2, IN2_2, IN3_2, IN4_2, EN_2]

def Forward():
    print("-> Moving Forward")
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)
    GPIO.output(EN, GPIO.HIGH)

def Reverse():
    print("-> Moving Backward")
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)
    GPIO.output(EN, GPIO.HIGH)

def TurnLeft():
    print("-> Turning Left")
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH) # Left motor backward
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH) # Right motor forward
    GPIO.output(EN, GPIO.HIGH)

def TurnRight():
    print("-> Turning Right")
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)  # Left motor forward
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)  # Right motor backward
    GPIO.output(EN, GPIO.HIGH)

def StopMotors():
    print("-> Stopping motor pair 1 (setting all pins LOW)")
    for p in MOTOR1_PINS:
        GPIO.output(p, GPIO.LOW)

def StopMotors_2():
    print("-> Stopping motor pair 2 (setting all pins LOW)")
    for p in MOTOR2_PINS:
        GPIO.output(p, GPIO.LOW)

def Up():
    print("-> Moving Up")
    GPIO.output(IN1_2, GPIO.HIGH)
    GPIO.output(IN2_2, GPIO.LOW)
    GPIO.output(IN3_2, GPIO.LOW)
    GPIO.output(IN4_2, GPIO.HIGH)
    GPIO.output(EN_2, GPIO.HIGH)

def Down():
    print("-> Moving Down")
    GPIO.output(IN1_2, GPIO.LOW)
    GPIO.output(IN2_2, GPIO.HIGH)
    GPIO.output(IN3_2, GPIO.HIGH)
    GPIO.output(IN4_2, GPIO.LOW)
    GPIO.output(EN_2, GPIO.HIGH)

def print_menu():
    print("\n=== Motor Control Menu ===")
    print("w: Forward")
    print("s: Backward")
    print("a: Turn Left")
    print("d: Turn Right")
    print("u: Up (second motor pair)")
    print("h: Down (second motor pair)")
    print("q: Quit")
    print("==========================")

# --- Main Loop (Corrected Logic) ---
try:
    while True:
        print_menu()
        choice = input("Enter your choice: ").lower()

        if choice == 'w':
            Forward()
            time.sleep(2)
            StopMotors()

        elif choice == 's':
            Reverse()
            time.sleep(2)
            StopMotors()

        elif choice == 'a':
            TurnLeft()
            time.sleep(2) 
            StopMotors()

        elif choice == 'd':
            TurnRight()
            time.sleep(2)
            StopMotors()

        elif choice == 'u':
            Up()
            time.sleep(2)
            StopMotors_2()

        elif choice == 'h':
            Down()
            time.sleep(2)
            StopMotors_2()

        elif choice == 'q':
            StopMotors()
            StopMotors_2()
            print("Exiting program.")
            break
            
        else:
            print("Invalid input!")

except KeyboardInterrupt:
    print("\nExiting due to user interrupt.")

finally:
    print("Cleaning up GPIO pins.")
    GPIO.cleanup()


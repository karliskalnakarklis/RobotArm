import wiringpi as wp
import time
import sys
import termios
import tty

# Setup
wp.wiringPiSetup()
LR_SERVO_PIN = 2  # Left-Right
UD_SERVO_PIN = 3  # Up-Down

wp.softPwmCreate(LR_SERVO_PIN, 0, 200)
wp.softPwmCreate(UD_SERVO_PIN, 0, 200)

def set_angle(pin, angle):
    pulse = int(5 + (angle / 180.0) * 20)
    wp.softPwmWrite(pin, pulse)

def get_key():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        return sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

try:
    while True:
        key = get_key()
        if key == '1':  # Nod
            for a in (90, 150, 90, 30, 90):
                set_angle(UD_SERVO_PIN, a)
                time.sleep(0.2)
        elif key == '2':  # Shake
            for a in (90, 150, 90, 30, 90):
                set_angle(LR_SERVO_PIN, a)
                time.sleep(0.2)

except KeyboardInterrupt:
    print("Stopped")

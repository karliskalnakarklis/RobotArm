import wiringpi as wp
import time

# Setup
wp.wiringPiSetup()
LR_SERVO_PIN = 2  # Left-Right (physical pin 7)
UD_SERVO_PIN = 3  # Up-Down (physical pin 8)

# Initialize soft PWM with range 0–200
if wp.softPwmCreate(LR_SERVO_PIN, 0, 200) != 0:
    print("Failed to create softPwm for Left-Right servo")
    exit()

if wp.softPwmCreate(UD_SERVO_PIN, 0, 200) != 0:
    print("Failed to create softPwm for Up-Down servo")
    exit()

def set_angle(pin, angle):
    # Convert angle (0–180) to pulse width (5–25)
    pulse = int(5 + (angle / 180.0) * 20)
    wp.softPwmWrite(pin, pulse)

try:
    while True:
        # Sweep both servos from 0° to 180°
        for angle in range(0, 181, 1):
            set_angle(LR_SERVO_PIN, angle)
            set_angle(UD_SERVO_PIN, angle)
            time.sleep(0.01)

        time.sleep(0.5)

        # Sweep both servos from 180° to 0°
        for angle in range(180, -1, -1):
            set_angle(LR_SERVO_PIN, angle)
            set_angle(UD_SERVO_PIN, angle)
            time.sleep(0.01)

        time.sleep(0.5)

except KeyboardInterrupt:
    print("Stopped by user")

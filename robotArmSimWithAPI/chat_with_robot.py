import time
from api_chatbox import converse
import wiringpi as wp

# Servo pin configuration
LR_SERVO_PIN = 2  # Left-Right
UD_SERVO_PIN = 3  # Up-Down

# Setup
wp.wiringPiSetup()
wp.softPwmCreate(LR_SERVO_PIN, 0, 200)
wp.softPwmCreate(UD_SERVO_PIN, 0, 200)

def set_angle(pin, angle):
    pulse = int(5 + (angle / 180.0) * 20)
    wp.softPwmWrite(pin, pulse)

def wait_motion(duration=5):
    print("⏳ Waiting...")
    end_time = time.time() + duration
    while time.time() < end_time:
        set_angle(LR_SERVO_PIN, 70)
        set_angle(UD_SERVO_PIN, 110)
        time.sleep(0.2)
        set_angle(LR_SERVO_PIN, 110)
        set_angle(UD_SERVO_PIN, 70)
        time.sleep(0.2)

def nod(duration=5):
    print("✅ Nodding Yes")
    end_time = time.time() + duration
    while time.time() < end_time:
        for a in (90, 150, 90, 30, 90):
            set_angle(UD_SERVO_PIN, a)
            time.sleep(0.2)

def shake(duration=5):
    print("❌ Shaking No")
    end_time = time.time() + duration
    while time.time() < end_time:
        for a in (90, 150, 90, 30, 90):
            set_angle(LR_SERVO_PIN, a)
            time.sleep(0.2)

if __name__ == "__main__":
    print("🤖 Robot AI Assistant ready. Type 'exit' to quit.")
    conv_id = None

    while True:
        user_input = input("You: ")
        if user_input.strip().lower() in ("exit", "quit"):
            print("👋 Exiting.")
            break

        wait_motion(duration=3)  # visually show "thinking"
        
        try:
            result = converse(user_input, conversation_id=conv_id)
            conv_id = result.get("conversation_id", conv_id)
            reply = result.get("speech", {}).get("plain", {}).get("speech", "<no reply>")
            print(f"Assistant: {reply}")
            nod(duration=5)
        except Exception as e:
            print("⚠️ Error communicating with AI:", e)
            shake(duration=5)

import time
from api_chatbox import converse
import wiringpi as wp

# Servo pin configuration
LR_SERVO_PIN = 2  # Left-Right
UD_SERVO_PIN = 3  # Up-Down

# WiringPi setup
wp.wiringPiSetup()
wp.softPwmCreate(LR_SERVO_PIN, 0, 200)
wp.softPwmCreate(UD_SERVO_PIN, 0, 200)

def set_angle(pin, angle):
    pulse = int(5 + (angle / 180.0) * 20)
    wp.softPwmWrite(pin, pulse)

def nod():
    for a in (90, 150, 90, 30, 90):
        set_angle(UD_SERVO_PIN, a)
        time.sleep(0.2)

def shake():
    for a in (90, 150, 90, 30, 90):
        set_angle(LR_SERVO_PIN, a)
        time.sleep(0.2)

if __name__ == "__main__":
    print("🤖 Chatbot-controlled robot arm ready. Type 'exit' to quit.")
    conv_id = None
    while True:
        user_input = input("You: ")
        if user_input.strip().lower() in ("exit", "quit"):
            print("👋 Exiting.")
            break
        try:
            result = converse(user_input, conversation_id=conv_id)
            conv_id = result.get("conversation_id", conv_id)
            reply = result.get("speech", {}).get("plain", {}).get("speech", "<no reply>")
            print(f"Assistant: {reply}")
            nod()
        except Exception as e:
            print("⚠️ Error communicating with AI:", e)
            shake()

import time
from bmp280 import BMP280
from smbus2 import SMBus
import paho.mqtt.client as mqtt

# Create an I2C bus object
bus = SMBus(0)
address = 0x77

# Setup BMP280
bmp280 = BMP280(i2c_addr= address, i2c_dev=bus)
interval = 15 # Sample period in seconds

# MQTT settings
MQTT_HOST ="192.168.1.42"
MQTT_PORT = 1883
MQTT_KEEPALIVE_INTERVAL =60
MQTT_TOPIC = "home/orangepi/temperature"
MQTT_CLIENT_ID = "******"
MQTT_USER = "orangepi"
MQTT_PWD = "orangepi"


def on_connect(client, userdata, flags, rc, properties):
    if rc==0:
        print("Connected OK with result code "+str(rc))
    else:
        print("Bad connection with result code "+str(rc))

def on_disconnect(client, userdata, flags, rc=0):
    print("Disconnected result code "+str(rc))

def on_message(client,userdata,msg):
    print("Received a message on topic: " + msg.topic + "; message: " + msg.payload)


# Set up a MQTT Client
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, MQTT_CLIENT_ID)
client.username_pw_set(MQTT_USER, MQTT_PWD)

# Connect callback handlers to client
client.on_connect= on_connect
client.on_disconnect= on_disconnect
client.on_message= on_message

print("Attempting to connect to %s" % MQTT_HOST)
client.connect(MQTT_HOST, MQTT_PORT)
client.loop_start() #start the loop

while True:
    # Measure data
    bmp280_temperature = bmp280.get_temperature()
    print("Temperature: %4.1f," % (bmp280_temperature))
    # Create the JSON data structure
    r_temp = round(bmp280_temperature , 1)
    MQTT_DATA = r_temp
    print(MQTT_DATA)
    try:
        client.publish(topic=MQTT_TOPIC, payload=MQTT_DATA, qos=0, retain=False, properties=None)
        time.sleep(interval)
    except OSError:
        client.reconnect()

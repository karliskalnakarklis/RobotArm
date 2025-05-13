import json
from paho.mqtt.client import Client, CallbackAPIVersion

# MQTT settings
MQTT_HOST = "192.168.1.42"
MQTT_PORT = 1883
MQTT_CLIENT_ID = "orangepi-temp-config"
MQTT_USER = "orangepi"
MQTT_PWD = "orangepi"

# Home Assistant MQTT Discovery
DISCOVERY_PREFIX = "homeassistant"
SENSOR_NAME = "OrangePi Temperature"
DEVICE_ID = "orangepi_temp_sensor"
STATE_TOPIC = "home/orangepi/temperature"
CONFIG_TOPIC = f"{DISCOVERY_PREFIX}/sensor/{DEVICE_ID}/config"

# Create sensor config payload
config_payload = {
    "name": SENSOR_NAME,
    "state_topic": STATE_TOPIC,
    "unit_of_measurement": "°C",
    "device_class": "temperature",
    "unique_id": DEVICE_ID,
    "value_template": "{{ value | float }}",
    "device": {
        "identifiers": [DEVICE_ID],
        "name": "Orange Pi Sensor",
        "manufacturer": "OrangePi",
        "model": "BMP280",
        "sw_version": "1.0"
    }
}

# Set up MQTT client
client = Client(client_id=MQTT_CLIENT_ID, callback_api_version=CallbackAPIVersion.VERSION2)
client.username_pw_set(MQTT_USER, MQTT_PWD)
client.connect(MQTT_HOST, MQTT_PORT)
client.loop_start()

# Publish discovery configuration
client.publish(CONFIG_TOPIC, json.dumps(config_payload), retain=True)
print(f"Published discovery config to {CONFIG_TOPIC}")

client.loop_stop()
client.disconnect()
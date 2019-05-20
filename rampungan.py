# Instruksi
# 1. install bluepy (untuk python3)
#     a. pip bluepy sudo pip3 install bluepy
#     b. sudo apt-get install bluez
# 2. jalankan aplikasi
#     a. sesuaikan mac address pada Peripheral dengan mac esp32 sensor
#     b. sesuaikan service uuid dan characteristic uuid
#     c. sudo hciconfig hci0 up
#     d. sudo python3 bleGateway.py
#     selesai

import bluepy
import binascii
import struct
import time
from bluepy.btle import UUID, Peripheral
import os
import time
import sys
import paho.mqtt.client as mqtt
import json

button_service_uuid = UUID("4fafc201-1fb5-459e-8fcc-c5c9c331914b")
button_char_uuid    = UUID("beb5483e-36e1-4688-b7f5-ea07361b26a8")

# Mengakses ESP32 dari MAC Address
p = Peripheral("30:AE:A4:1F:F1:82","public")

ButtonService=p.getServiceByUUID(button_service_uuid)
THINGSBOARD_HOST = 'demo.thingsboard.io'
ACCESS_TOKEN = '8qEdT0y82RRSQsyhKlJe'

# Data capture and upload interval in seconds. Less interval will eventually hang the DHT22.
INTERVAL=5

sensor_data = {"light_intensity": 0, "active": True}

next_reading = time.time() 

client = mqtt.Client()

# Set access token
client.username_pw_set(ACCESS_TOKEN)

# Connect to ThingsBoard using default MQTT port and 60 seconds keepalive interval
client.connect(THINGSBOARD_HOST, 1883, 60)

client.loop_start()
global data1
try:
    ch = ButtonService.getCharacteristics(button_char_uuid)[0]
    if (ch.supportsRead()):
        while 1:
            val = binascii.b2a_hex(ch.read())
            val = binascii.unhexlify(val)
            # print ("Data : " + str(val))
            b = val
            raw_data = b.decode("utf-8")
            data1 = int(raw_data)
            # Mengirim data ke Thingsboard
            light = data1
            light = round(light, 2)
            print("Intensits Cahaya: {:g} lux meter".format(light))
            sensor_data["light_intensity"] = light

            # Sending light data to ThingsBoard
            client.publish('v1/devices/me/telemetry', json.dumps(sensor_data), 2)
            print(json.dumps(sensor_data))
            if True:
                print("data sent!")
            next_reading += INTERVAL
            sleep_time = next_reading-time.time()
            print("sleeping...")
            if sleep_time > 0:
                time.sleep(sleep_time)
            # output -> b'-14, 166'
            # b menunjukkan datanya adalah bytes yg diconvert ke string
            # you need to decode the bytes of you want a string:
            # b = b'1234'
            # print(b.decode('utf-8'))  # '1234'
        
except KeyboardInterrupt:
        pass

finally:
    p.disconnect()

client.loop_stop()
client.disconnect()
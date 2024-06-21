from time import sleep
import adafruit_dht

import board 
import neopixel

import paho.mqtt.client as mqtt 
import json

import random

from gpiozero import Button

pixel_pin = board.D10
num_pixels = 4

pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.2, auto_write=False, pixel_order=neopixel.GRB)

pixels.fill((0, 0, 0))
pixels.show()

dht_device = adafruit_dht.DHT22(board.D4)

button = Button(24, pull_up=False)

MY_ID = "08"
MQTT_HOST = "mqtt-dashboard.com"
MQTT_PORT = 1883
MQTT_KEEPALIVE_INTERVAL = 60
MQTT_COLOR_TOPIC = f"mobile/{MY_ID}/color"
MQTT_TEMP_TOPIC = f"mobile/{MY_ID}/temp"
MQTT_HUM_TOPIC = f"mobile/{MY_ID}/hum"
MQTT_MODE_TOPIC = f"mobile/{MY_ID}/mode"

current_mode = 0
current_color = [0, 0, 0]


def color_temperature(temperature):
    if temperature < 20:
        return [0, 0, 255]  # 파란색
    elif 20 <= temperature < 30:
        return [0, 255, 0]  # 초록색
    else:
        return [255, 0, 0]  # 빨간색


def color_humidity(humidity):
    if humidity < 30:
        return [255, 255, 0]  # 노란색
    elif 30 <= humidity < 60:
        return [0, 255, 255]  # 하늘색
    else:
        return [255, 0, 255]  # 보라색


def random_color():
    red = random.randint(0, 255)
    green = random.randint(0, 255)
    blue = random.randint(0, 255)
    
    return [red, green, blue]


def set_moodlight(mode):
    global current_color
    if mode == 0:
        pixels.fill((0, 0, 0))

    elif mode == 1:
        current_color = random_color()
        pixels.fill(current_color)

    elif mode == 2:
        try:
            temperature = dht_device.temperature
            current_color = color_temperature(temperature)
        
        except RuntimeError:
            sleep(0.2)
            return
        
    elif mode == 3:
        try:
            humidity = dht_device.humidity
            current_color = color_humidity(humidity)
        
        except RuntimeError:
            sleep(0.2)
            return
        
    pixels.show()
    print(f"Mode change: {mode}, Color: {current_color}")


def button_pressed():
    global current_mode
    current_mode = (current_mode + 1) % 4
    set_moodlight(current_mode)

button.when_pressed = button_pressed


def on_message(client, userdata, message):
    global current_mode, current_color
    try:
        result = str(message.payload.decode("utf-8"))
        value = json.loads(result)

        if message.topic == MQTT_COLOR_TOPIC:
            color_list = value.get("color", [255, 255, 255])
            current_color = color_list
            
            if current_mode == 1:
                pixels.fill(current_color)
                pixels.show()
                print(f"Received color = {current_color}")

        elif message.topic == MQTT_TEMP_TOPIC:
            temperature = value.get("temperature", 0)
            print(f"Received Temperature = {temperature}*C")
            
            if current_mode == 2:
                current_color = color_temperature(temperature)
                pixels.fill(current_color)
                pixels.show()

        elif message.topic == MQTT_HUM_TOPIC:
            humidity = value.get("humidity", 0)
            print(f"Received Humidity = {humidity}%")

            if current_mode == 3:
                current_color = color_humidity(humidity)
                pixels.fill(current_color)
                pixels.show()

        elif message.topic == MQTT_MODE_TOPIC:
            current_mode = value.get("mode", 0)
            print(f"Mode changed to {current_mode}")
            set_moodlight(current_mode)

    except:
        sleep(1.0)

client = mqtt.Client()
client.on_message = on_message

client.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE_INTERVAL)
client.subscribe(MQTT_COLOR_TOPIC)
client.subscribe(MQTT_TEMP_TOPIC)
client.subscribe(MQTT_HUM_TOPIC)
client.subscribe(MQTT_MODE_TOPIC)
client.loop_start()

try:
    while True:
        if current_mode in [2, 3]:
            try:
                if current_mode == 2:
                    temperature = dht_device.temperature
                    current_color = color_temperature(temperature)
                
                elif current_mode == 3:
                    humidity = dht_device.humidity
                    current_color = color_humidity(humidity)
                
                pixels.fill(current_color)
                pixels.show()
            
            except RuntimeError as error:
                sleep(1.0)
                continue
        sleep(1)
except KeyboardInterrupt:
    print("프로그램을 종료합니다.")
    
finally:
    client.loop_stop()
    client.disconnect()
    pixels.fill((0, 0, 0))
    pixels.show()
    dht_device.exit()

from time import sleep
from gpiozero import Button
import board
import neopixel

pixel_pin = board.D10
num_pixel = 4

button = Button(24, pull_up=False, bounce_time = 0.1)

pixels = neopixel.NeoPixel(pixel_pin, num_pixel, brightness=0,auto_write=False, pixel_order=neopixel.GRB)

bright_level_now = 0

pixels.fill((0, 0, 0))
pixels.show()

def set_brightness(level):
    if level == 0:
        pixels.fill((255, 255, 255))
        pixels.brightness = 0
        
    if level == 1:
        pixels.brightness = 0.09
       
    if level == 2:
        pixels.brightness = 0.25
    
    if level == 3:
        pixels.brightness = 0.45

    pixels.show()

def button_pressed():
    global bright_level_now
    bright_level_now = bright_level_now + 1
    if bright_level_now == 0:
        bright_level_now = 0
    if bright_level_now > 3:
        bright_level_now = 0
    
    set_brightness(bright_level_now)
    print(f"Button Pressed! Bright Level: {bright_level_now}")

button.when_pressed = button_pressed

try:
    while True:
        sleep(1)

except KeyboardInterrupt:
    set_brightness(0)
    print("I'm done!")
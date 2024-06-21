# led-strip1.py

from time import sleep
import board

import neopixel

pixel_pin = board.D10
num_pixel = 4

pixels = neopixel.NeoPixel(pixel_pin, num_pixel, brightness=0.05, auto_write=False, pixel_order=neopixel.GRB)

try:
    while True:
        pixels.fill((0, 0, 0))
        pixels.show()
        sleep(1)

        pixels[0] = (0, 0, 155)
        pixels[1] = (255, 255, 255)
        pixels[2] = (255, 0, 0)
        pixels[3] = (0, 255, 0)
        pixels.show()
        sleep(1)
except:
    print("I'm Done!")
    pixels.show()


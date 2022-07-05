# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)

from machine import SoftI2C, Pin
import machine
from lis2hh12 import LIS2HH12, SF_G
from neopixel import NeoPixel
import buttons
import uasyncio

i2c = SoftI2C(scl=Pin(22), sda=Pin(21), freq=100000)
imu = LIS2HH12(i2c, address=0x18, sf=SF_G)
# enable the ACC interrupt to turn on backlight
imu.enable_act_int()

neopixel_pin = Pin(2, Pin.OUT)
neopixels = NeoPixel(neopixel_pin, 5)
neopixels[0] = (0,0,0)
neopixels[1] = (0,0,0)
neopixels[2] = (0,0,0)
neopixels[3] = (0,0,0)
neopixels[4] = (0,0,0)
neopixels.write()

import settings

def recover_menu():
    print("Recovering menu!")
    try:
        settings.remove('apps.autorun')
    except KeyError:
        # can happen when no apps.autorun is set
        pass
    settings.store()
    machine.reset()

def execute_repl():
    print("Executing REPL!")
    settings.set('apps.autorun', 'REPL')
    settings.store()
    machine.reset()

if settings.get('BLE-beacon_enabled'):
    import BLE_beacon

app = settings.get('apps.autorun')
if app == None:
    app = "frozen_apps.menu"


async def check_recover_button(pin):
    countdown = 5
    while pin.value() == 0:
        print('Hold for {} seconds to recover main menu.'.format(countdown))
        countdown -= 1
        if (countdown == 0):
            recover_menu()
        await uasyncio.sleep_ms(1000)


# Callback for the boot pin IRQ
def hold_to_recover(pin):
    if pin.value() == 0:
        print("Boot button pressed.")
        # start check task
        uasyncio.run(check_recover_button(pin))
        

buttons.boot_pin.irq(hold_to_recover)

if app and not app == "REPL":
    try:
		print("Starting app '{}'...".format(app))
		if app:
			__import__(app)
    except BaseException as e:
        print("Exception happened in app:",  e)
        settings.remove('apps.autorun')
        settings.store()
        
else:
    print("REPL is running.")
    print("Press Boot button after power-on to run main menu.")

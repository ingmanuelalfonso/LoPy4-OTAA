#LoPy4 + Pytrack2 hardware - PCB antenna
import gc
gc.collect()

from machine import Timer, RTC,
from network import LoRa, WLAN,
import binascii
import network
import machine
import socket
import struct
import pycom
import time
import os
import ubinascii

from pytrack import Pytrack
from L76GNSS import L76GNSS
from LIS2HH12 import LIS2HH12

LORA_FREQUENCY = const(916800000)
LORA_SF = const(9)
LORA_BW = LoRa.BW_125KHZ
LORA_CR = LoRa.CODING_4_5
LORAWAN_DR = 4
DEEPSLEEP_TIME = const(10)
START_COLOUR = const(0xFF0000)

gc.collect()
pycom.heartbeat(False)
pycom.rgbled(START_COLOUR)

lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.AU915)
lora.nvram_restore()

if(not lora.has_joined()):
    print("LoRaWan Join in manual mode...")

    app_eui = ubinascii.unhexlify('70B3D57ED003A63C')
    app_key = ubinascii.unhexlify('1D971BD6B05E9E219BCF71D5FA27F752')
    dev_eui = ubinascii.unhexlify('70B3D5499C9DED9F')
    # app_key = ubinascii.unhexlify('XXXXXXXXXXXXXXXXXXXXXXXXXXX')
    # dev_eui = ubinascii.unhexlify('XXXXXXXXXXXXX')
    # app_eui = ubinascii.unhexlify('XXXXXXXXXXXXXXC')

lora.join(activation=LoRa.OTAA, auth=(dev_eui, app_eui, app_key), timeout=0)

for i in range(8, 16):
    fq = LORA_FREQUENCY + ((i-8) * 200000)
    lora.add_channel(i, frequency=fq, dr_min=0, dr_max=LORAWAN_DR)

lora.add_channel(65, frequency=917500000, dr_min=6, dr_max=6)

while not lora.has_joined():
    time.sleep(2.5)
    print('Lora has not joined')

if lora.has_joined():

    lora_sock = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
    lora_sock.setsockopt(socket.SOL_LORA, socket.SO_DR, 3)
    lora_sock.setsockopt(socket.SOL_LORA, socket.SO_CONFIRMED, True)
    lora_sock.setblocking(False)

    gc.collect()

    lpp = cayenneLPP.CayenneLPP(size = 100, sock = lora_sock)

    py = Pytrack()
    L76 = L76GNSS(pytrack=py)

    pycom.rgbled(0xFF7F00)
    gps = L76GNSS(py, timeout=10)
    coord = gps.coordinates()

    if (coord == (None,None)):
        pycom.rgbled(0xCC3299)
        print("Without GPS")
        coord = (-20.27262, -40.3068, 9.6)
        time.sleep(1)

    lpp.add_gps(coord[0], coord[1], 0, channel=2)

    LoRaWan_pkg = lpp.get_payload()
    gc.collect()

    lpp.send()
    seconds = DEEPSLEEP_TIME + (os.urandom(1)[0] & 0x0F)
    machine.deepsleep(seconds*1000)

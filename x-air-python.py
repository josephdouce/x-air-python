# import
import socket
import sys
import time
import random
from functools import partial
from collections import namedtuple

# kivy
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label 
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.slider import Slider
from kivy.properties import *
from kivy.graphics import Rectangle, Color
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.config import Config
from kivy.logger import Logger

# import needed modules from osc4py3
from osc4py3.oscbuildparse import *

XInfo = namedtuple("XInfo", ["host", "port", "name", "model", "version"])

# sockets
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# server
selected_xinfo = None

# ui size
Config.set('graphics', 'width', '1200')
Config.set('graphics', 'height', '768')
Config.write()

# builder class
class XAirPython(BoxLayout):
    # start all meter values at 0
    meters = ListProperty([0] * 100)
    sends = ListProperty([[0.1] * 10,[0.2] * 10,[0.3] * 10,[0.4] * 10,[0.5] * 10,[0.6] * 10,[0.7] * 10,[0.8] * 10,[0.9] * 10,[1] * 10,[0.9] * 10,[0.8] * 10,[0.7] * 10,[0.6] * 10,[0.5] * 10,[0.4] * 10,[0.3] * 10,[0.2] * 10])
    
    def send_test(self, *args):
        sends = self.sends
        sends += [sends.pop(0)]

    # decode meters 
    def decode_meters(self, data):

        # byte positions for meters
        meter_positions = {
           b'meters/0' : -16,
           b'meters/1' : -80,
           b'meters/2' : -72,
           b'meters/3' : -112,
           b'meters/4' : -200,
           b'meters/5' : -88,
           b'meters/6' : -78,
           b'meters/7' : -32,
           b'meters/8' : -8,
           b'meters/9' : -8,
        }

        # get byte position
        num = meter_positions[data[0:8]]

        # convert meters to 0-1 range 
        meters = [(int.from_bytes(data[num:][i:i+2], byteorder='little', signed = True) + 32768) * 1/65536 for i in range(0, 100, 2)]

        return meters

    # subscribe to meters
    def subscribe(self, num, *args):
        msg = OSCMessage("/batchsubscribe",",ssiii",["meters/" + num, "/meters/" + num, 0,0,1])
        # send
        sent = sock.sendto(encode_packet(msg), (selected_xinfo.host, selected_xinfo.port))
    
    # recieve data
    def recieve(self, *args):
        # connect
        sent = sock.connect((selected_xinfo.host, selected_xinfo.port))

        # recieve
        data, server = sock.recvfrom(512)
        try:
            print(decode_packet(data))
        except:
            if (data[0:7] == b'meters/'):
                self.meters = self.decode_meters(data)

# dummy class see kv file
class BoxBorder(BoxLayout):
    pass

class MeterPanel(BoxLayout):
    meter_value = NumericProperty()

class BusesPanel(BoxLayout):
    send_values = ListProperty([0,0,0,0,0,0,0,0,0,0,0])


# main class
class Main(App):
    def build(self):
        self.title = "Connected to {} at {}:{} [{} v{}]".format(selected_xinfo.name, selected_xinfo.host, selected_xinfo.port, selected_xinfo.model, selected_xinfo.version)

        # new instance of XAirPython
        xair = XAirPython()
        # subscribe to meters
        xair.subscribe('2')
        # schedule refresh meter subscription
        Clock.schedule_interval(partial(xair.subscribe, '2'), 9)
        # schedule check for incoming data
        Clock.schedule_interval(xair.recieve, 1/20)

        # schedule sends test event
        # Clock.schedule_interval(xair.send_test, 1/20)

        # return UI
        return xair


def auto_detect_xair():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, True)
    s.settimeout(3.0)

    msg = OSCMessage("/xinfo", ",", [])
    s.sendto(encode_packet(msg), ("<broadcast>", 10024))

    # Currently, this only supports one XAir on the network and will return 
    # whichever replies first.
    try:
        data, server = s.recvfrom(512)
    except:
        return None
    finally:
        s.close()

    xinfo = decode_packet(data)
    ip,name,model,version = xinfo.arguments
    return XInfo(server[0], server[1], name, model, version)


# run app
if __name__ == "__main__":
    selected_xinfo = auto_detect_xair()
    if not selected_xinfo:
        Logger.error("XAir Detect: Failed to detect an XAir on network.")
        exit(1)

    Logger.info("XAir Detect: Found {} at {}:{} [{} v{}]".format(selected_xinfo.name, selected_xinfo.host, selected_xinfo.port, selected_xinfo.model, selected_xinfo.version))

    Main().run()


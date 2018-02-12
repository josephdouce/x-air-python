# Import
import socket
import sys
import time
import random
from functools import partial

#Kivy
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label 
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty, StringProperty, ListProperty, NumericProperty

# Import needed modules from osc4py3
from osc4py3.oscbuildparse import *

# Sockets
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Server
server_address = ('192.168.1.101', 10024)

# Build Message
msg2 = OSCMessage("/info","",[])

def remap( x, oMin, oMax, nMin, nMax ):

    #range check
    if oMin == oMax:
        print("Warning: Zero input range")
        return None

    if nMin == nMax:
        print("Warning: Zero output range")
        return None

    #check reversed input range
    reverseInput = False
    oldMin = min( oMin, oMax )
    oldMax = max( oMin, oMax )
    if not oldMin == oMin:
        reverseInput = True

    #check reversed output range
    reverseOutput = False   
    newMin = min( nMin, nMax )
    newMax = max( nMin, nMax )
    if not newMin == nMin :
        reverseOutput = True

    portion = (x-oldMin)*(newMax-newMin)/(oldMax-oldMin)
    if reverseInput:
        portion = (oldMax-x)*(newMax-newMin)/(oldMax-oldMin)

    result = portion + newMin
    if reverseOutput:
        result = newMax - portion

    return result

class XAirPython(FloatLayout):
    meters = ListProperty([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])

    def decode_meters(self, data):
        def meters_0(data):
            meters = [int.from_bytes(data[-16:][i:i+2], byteorder='little', signed = True) for i in range(0, 100, 2)]
            return meters
        def meters_1(data):
            meters = [int.from_bytes(data[-80:][i:i+2], byteorder='little', signed = True) for i in range(0, 100, 2)]
            return meters
        def meters_2(data):
            meters = [int.from_bytes(data[-72:][i:i+2], byteorder='little', signed = True) for i in range(0, 100, 2)]
            return meters
        def meters_3(data):
            meters = [int.from_bytes(data[-112:][i:i+2], byteorder='little', signed = True) for i in range(0, 100, 2)]
            return meters
        def meters_4(data):
            meters = [int.from_bytes(data[-200:][i:i+2], byteorder='little', signed = True) for i in range(0, 100, 2)]
            return meters
        def meters_5(data):
            meters = [int.from_bytes(data[-88:][i:i+2], byteorder='little', signed = True) for i in range(0, 100, 2)]
            return meters
        def meters_6(data):
            meters = [int.from_bytes(data[-78:][i:i+2], byteorder='little', signed = True) for i in range(0, 100, 2)]
            return meters
        def meters_7(data):
            meters = [int.from_bytes(data[-32:][i:i+2], byteorder='little', signed = True) for i in range(0, 100, 2)]
            return meters
        def meters_8(data):
            meters = [int.from_bytes(data[-8:][i:i+2], byteorder='little', signed = True) for i in range(0, 100, 2)]
            return meters
        def meters_9(data):
            meters = [int.from_bytes(data[-8:][i:i+2], byteorder='little', signed = True) for i in range(0, 100, 2)]
            return meters
        
        options = {
           b'0' : meters_0,
           b'1' : meters_1,
           b'2' : meters_2,
           b'3' : meters_3,
           b'4' : meters_4,
           b'5' : meters_5,
           b'6' : meters_6,
           b'7' : meters_7,
           b'8' : meters_8,
           b'9' : meters_9,
        }

        num = data[7:8]
        meters = options[num](data)
        return meters

    def subscribe(self, num, *args):
        msg = OSCMessage("/batchsubscribe",",ssiii",["meters/" + num, "/meters/" + num, 0,0,1])
        # Send
        sent = sock.sendto(encode_packet(msg), server_address)
    
    def recieve(self, *args):
        # Send
        sent = sock.connect(server_address)

        # Recieve
        data, server = sock.recvfrom(512)
        try:
            print(decode_packet(data))
        except:
            if (data[0:7] == b'meters/'):
                self.meters = self.decode_meters(data)

class Main(App):
    def build(self):
        xair = XAirPython()
        xair.subscribe('2')
        Clock.schedule_interval(partial(xair.subscribe, '2'), 10)
        Clock.schedule_interval(xair.recieve, 1/60)
        return xair

if __name__ == "__main__":
    Main().run()
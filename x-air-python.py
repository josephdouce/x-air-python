# Import
import socket
import sys
import time
import random 

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
msg = OSCMessage("/batchsubscribe",",ssiii",["meters/2", "/meters/2", 0,0,1])
msg2 = OSCMessage("/info","",[])

class XAirPython(FloatLayout):
    meters2 = ListProperty([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
    def decode_meters_2(self, data):
        meters = [int.from_bytes(data[-64:][i:i+2], byteorder='big') for i in range(0, len(data[-64:]), 2)]
        return(meters)

    def send(self, *args):
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
            if (data[0:8] == b'meters/2'):
                self.meters2 = self.decode_meters_2(data)
                print(self.meters2)

class Main(App):
    def build(self):
        xair = XAirPython()
        xair.send()
        Clock.schedule_interval(xair.send, 10)
        Clock.schedule_interval(xair.recieve, 1/60)
        return xair

if __name__ == "__main__":
    Main().run()
#!/usr/bin/env python3

import logging
import signal
import socket
import pickle

logging.basicConfig (level = logging.DEBUG)
logger = logging.getLogger (__name__)

HOST = '127.0.0.1'
PORT = 1901

class Home (object):
    def __init__ (self, *args, **kwargs):
        self.HOST = kwargs.get ('HOST', HOST)
        self.PORT = kwargs.get ('PORT', PORT)

    def request (self, data):
        with socket.socket (socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect ((self.HOST, self.PORT))
                s.sendall (str.encode(data))
                return pickle.loads (s.recv (50))
            except socket.error as msg:
                logging.info ("Could not connect to service center: %s" %(msg))
                return [0x01]

    def toggle_light (self, value):
        ret = self.request ('toggle') 

    def turn_light (self, value):
        ret = self.request ('light_on') if value else self.request ('light_off')

    def toggle_ac (self, value):
        ret = self.request ('ac_on') if value else self.request ('ac_off')

    def get_light (self):
        result = self.request ('light')
        if result [0] == 0x00:
            return result [1]
        else:
            return 0 

    def get_climate (self, index):
        result = self.request ('climate')
        if result [0] == 0x00:
            return result [index]
        else:
            return 0 


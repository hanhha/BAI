#!/usr/bin/env python3

import signal
import logging
from .MyMqttRoom import *
from .MyMqttWrap import wdt_wait

logging.basicConfig (level = logging.DEBUG)
logger = logging.getLogger (__name__)

class Home (MyMqttRoom):
    def __init__ (self, *args, **kwargs):
        super().__init__ ("Egome_bot", kwargs.get ('HOST'), 
                                       kwargs.get ('PORT'), 
                                       kwargs.get ('TRNS_TOPIC'),
                                       kwargs.get ('RECV_TOPIC'),
                                       kwargs.get ('COMM_TOPIC'))

        signal.signal (signal.SIGINT, self.onKillEvent)
        signal.signal (signal.SIGTERM, self.onKillEvent)

    def request (self, data):
        self.publish (data)
        logging.info ("Published command: %s" %(data))
        result = wdt_wait (lambda : self.IDLE, 10)
        if result:
            return ([0x00] + list(self.Climate)) if data == "climate" else [0x00] 
        else:
            logging.info ("Timeout.")
            return [0x01]

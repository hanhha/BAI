#!/usr/bin/env python3

import sys
import time
from BrixAIUtils.MyMqttRoom import * 

HOST = '127.0.0.1'
PORT = 1901
TRNS_TOPIC = 'ReqRoomClimate'
RECV_TOPIC = 'RcvRoomClimate'
COMM_TOPIC = 'RoomClimate'

rsp_func = {}
client = MyMqttRoom ("Egome_cli", HOST, PORT, TRNS_TOPIC, RECV_TOPIC, COMM_TOPIC, rsp_func_dict=rsp_func)

def printClimate ():
    global client

    print (client.Climate)
    print ("Light: ",       client.Climate [0])
    print ("Temperature: ", client.Climate [1])
    print ("Humidity: ",    client.Climate [2])

def check (result):
    print ("Done.")

rsp_func [MSG_BYTE_CLIMATE] = check 
rsp_func [MSG_BYTE_LTOGGLE] = check
rsp_func [MSG_BYTE_AC]      = check

if len (sys.argv) > 1:
    client.start ()
    for cmd in sys.argv [1:]:
        if (cmd == "light_off"):
            client.publish ('toggle')
            while client.IDLE == 0:
                pass
            time.sleep (1)
            client.publish ("toggle")
        elif (cmd == "light_on"):
            client.publish ('toggle')
        elif not client.publish (cmd):
            print ("Unsupported command ", cmd, ".")
            continue

        print ("Command",cmd,"sent.")
        while client.IDLE == 0:
            pass
        client.publish_common (cmd)
        time.sleep (1)
        if (cmd == "climate"):
            printClimate ()
        print ("-----------------------------------------")

    client.stop ()
else:
    print ("No command.")

#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import datetime
import time
import sys
import simplejson as json
import array
import binascii
import struct
import redis
import zmq

import logging
import os

from libs.dash import *
from libs.rediscommon import *
from libs.config import r_IX_LIST, r_BK_LIST

import pprint

log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../logs/' + os.path.basename(__file__) + '.log')
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s %(message)s')

# redis
POOL = redis.ConnectionPool(host='localhost', port=6379, db=0)
r = redis.StrictRedis(connection_pool=POOL)

# zmq
zmqContext = zmq.Context()
zmqSubSocket = zmqContext.socket(zmq.SUB)
zmqSubSocket.setsockopt(zmq.SUBSCRIBE, b"hashblock")
zmqSubSocket.setsockopt(zmq.SUBSCRIBE, b"rawtx")
zmqSubSocket.setsockopt(zmq.SUBSCRIBE, b"rawtxlock")
zmqSubSocket.setsockopt(zmq.SUBSCRIBE, b"hashtx")
zmqSubSocket.connect("tcp://127.0.0.1:28332")

pp = pprint.PrettyPrinter(indent=4)

# check redis
logging.info('[ix_bl_queue] started')
try:
    r.ping()

except Exception as e:
    logging.info(e.args[0])
    sys.exit()


# main
try:
    while True:
        msg = zmqSubSocket.recv_multipart()
        topic = str(msg[0].decode("utf-8"))
        body  = str(binascii.hexlify(msg[1]).decode("utf-8"))
        sequence = "Unknown"

        if len(msg[-1]) == 4:
          msgSequence = struct.unpack('<I', msg[-1])[-1]
          sequence = str(msgSequence)

        if topic == 'rawtxlock':
            logging.info('[ix_bl_queue] rawtx : [' + sequence + '] ' + body)
            addrval = decoderawtx(body)

            if len(addrval) > 0:
                for key in addrval.keys():
                    key_to_queue = { 'addr': key, 'val': addrval[key]['val'], 'txid': addrval[key]['txid'] }
                    ix_to_queue  = r_lpush_key(r, r_IX_LIST, json.dumps(key_to_queue))

        elif topic == "hashblock":
            bk_to_queue = r_lpush_key(r, r_BK_LIST, body)

        elif topic == 'hashtx':
            logging.info('[ix_bl_queue] tx : [' + sequence + '] ' + body)

#        elif topic == 'rawtxlock':
#            logging.info('[ix_bl_queue] rawtxlock : [' + sequence + '] ' + body)

except Exception as e:
    print(e.args[0])
    sys.exit()

except KeyboardInterrupt:
    zmqContext.destroy()
    logging.info('[ix_bl_queue] intterupted by keyboard')
    sys.exit()



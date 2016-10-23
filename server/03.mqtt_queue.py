#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import datetime
import time
import sys
import simplejson as json
import redis
import paho.mqtt.client as mqtt

from libs.printlogs import *
from libs.dash import *
from libs.rediscommon import *
from libs.config import r_MQ_LIST, m_SALE_REQ_SUBSCRIBE
from libs.config import r_CLIENT_LIST_SET, r_CLIENT_CMD_HASH

import pprint

def on_connect(client, userdata, flags, rc):
    global m_SALE_REQ_SUBSCRIBE
    logging.info('[mqtt_queue] mqtt : Connected with result code ' + str(rc))
    client.subscribe(m_SALE_REQ_SUBSCRIBE, 0)

def on_message(client, userdata, msg):
    global r, r_MQ_LIST
    idcheck = msg.topic.replace('s/req/', '')
    req = json.loads(msg.payload)
    if idcheck == req['clientid']:
        # 1) add client to client list set
        # 2) add payload to client hash
        # 3) add clientd and namotime to r_MQ_LIST

        epochnano = get_nanotime()
        pipe = r.pipeline()
        pipe.sadd(r_CLIENT_LIST_SET, idcheck)
        pipe.hset(r_CLIENT_CMD_HASH + idcheck, epochnano, msg.payload)
        pipe.lpush(r_MQ_LIST, {"clientid": idcheck, "tstamp": epochnano})
        response = pipe.execute() 
        logging.info('[mqtt_queue] mqtt : type - ' + req['cmd'] + ' : clientid - ' + req['clientid'] + ' ---> queued')

    else:
        logging.info('[mqtt_queue] mqtt : topic - ' + msg.topic + ' payload - ' + str(msg.payload) + ' ---> discard')


# redis
POOL = redis.ConnectionPool(host='localhost', port=6379, db=0)
r = redis.StrictRedis(connection_pool=POOL)

pp = pprint.PrettyPrinter(indent=4)

# check redis
logging.info('[mqtt_queue] started')
try:
    r.ping()

except Exception as e:
    logging.info(e.args[0])
    sys.exit()


# mqtt
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

try:
    client.connect('127.0.0.1', 1883, 10)
    #client.loop_start()
    client.loop_forever()

except Exception as e:
    print(e.args[0])
    sys.exit()

except KeyboardInterrupt:
    logging.info('[mqtt_queue] intterupted by keyboard')
    sys.exit(1)

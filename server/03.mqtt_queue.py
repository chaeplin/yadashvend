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

import pprint

def on_connect(client, userdata, flags, rc):
    global m_SALE_REQ_SUBSCRIBE
    print_log('mqtt : Connected with result code ' + str(rc))
    client.subscribe(m_SALE_REQ_SUBSCRIBE, 0)

def on_message(client, userdata, msg):
    global r, r_MQ_LIST
    idcheck = msg.topic.replace('s/req/', '')
    req = json.loads(msg.payload)
    if idcheck == req['clientid']:
        mq_result = r_rpush_key(r, r_MQ_LIST, str(msg.payload))
        print_log('mqtt : type - ' + req['type'] + ' : clientid - ' + req['clientid'] + ' ---> queued')
    else:
        print_log('mqtt : topic - ' + msg.topic + ' payload - ' + str(msg.payload) + ' ---> discard')


# redis
POOL = redis.ConnectionPool(host='localhost', port=6379, db=0)
r = redis.StrictRedis(connection_pool=POOL)

pp = pprint.PrettyPrinter(indent=4)

# check redis
try:
    r.ping()

except Exception as e:
    print_log(e.args[0])
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
    sys.exit(1)

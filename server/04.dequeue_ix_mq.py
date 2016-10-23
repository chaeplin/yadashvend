#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import datetime
import time
import sys
import simplejson as json
import redis

from libs.printlogs import *
from libs.dash import *
from libs.rediscommon import *
from libs.config import r_IX_LIST, r_MQ_LIST 

import pprint

# redis
POOL = redis.ConnectionPool(host='localhost', port=6379, db=0)
r = redis.StrictRedis(connection_pool=POOL)

pp = pprint.PrettyPrinter(indent=4)

def process_mq(val):
    logging.info('process_mq called')
    # 1) move a new address to sale set and used set


def process_ix():
    pass


# check redis
logging.info('[dequeue_ix_mq] started')
try:
    r.ping()

except Exception as e:
    logging.info(e.args[0])
    sys.exit()

#
try:

    while 1:
        quelist = (r_IX_LIST, r_MQ_LIST)
        jobque = r_redis_blpop(r, quelist)
        
        if jobque:
            pp.pprint(jobque)
            redis_key = jobque[0]
            redis_val = jobque[1]

            if redis_key == r_MQ_LIST:
                process_mq(redis_val)


#(   'testnet:MQ_RECEIVED',
#    '{"clientid":"client1","cmd":"order","item":10,"msgid":11}') 

#client1
#    publish to    --> s/req/client1 
#                      {"clientid": "client1", "cmd": "order",   "item": xxx, "msgid": xxx}
#                      {"clientid": "client1", "cmd": "change",  "item": xxx, "msgid": xxx} 
#                      {"clientid": "client1", "cmd": "discard", "item": xxx, "msgid": xxx}
#    subscribe to  --> s/resp/client1 
#                      {"addr": "yyyyy", "val": "ffff", "cmd": "order", "msgid": xxx}
#                      {"addr": "yyyyy", "val": "ffff", "cmd": "paid",  "msgid": xxx}
#                      {"addr": "yyyyy", "val": "ffff", "cmd": "dscrd", "msgid": xxx}

except Exception as e:
    print(e.args[0])
    sys.exit()

except KeyboardInterrupt:
    logging.info('[dequeue_ix_mq] intterupted by keyboard')
    sys.exit()


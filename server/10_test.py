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
from libs.config import r_MQ_LIST, r_IX_LIST, r_BK_LIST, m_SALE_REQ_SUBSCRIBE
from libs.config import r_CLIENT_LIST_SET, r_CLIENT_CMD_HASH
from libs.config import r_NEW_ADDR_SET, r_USED_ADDR_SET, r_SALE_ADDR_SET
from libs.config import r_ADDR_CMD_HASH

import pprint

# redis
POOL = redis.ConnectionPool(host='localhost', port=6379, db=0)
r = redis.StrictRedis(connection_pool=POOL)

pp = pprint.PrettyPrinter(indent=4)

try:
    r.ping()

except Exception as e:
    logging.info(e.args[0])
    sys.exit()

#
#
r.flushdb()
#sys.exit()
#
#

# -------- #
CLIENT_NAME = 'ihavenonameyet2'

try:
    print('r_MQ_LIST') 
    pp.pprint(r.lrange(r_MQ_LIST, 0, -1))    
    print('r_IX_LIST') 
    pp.pprint(r.lrange(r_IX_LIST, 0, -1))    
    print('r_BK_LIST') 
    pp.pprint(r.lrange(r_BK_LIST, 0, -1))    
    print('r_CLIENT_LIST_SET')
    pp.pprint(r.smembers(r_CLIENT_LIST_SET))
    print('r_CLIENT_CMD_HASH + CLIENT_NAME')
    pp.pprint(r.hgetall(r_CLIENT_CMD_HASH + CLIENT_NAME))
#    pp.pprint(r.hkeys(r_CLIENT_CMD_HASH + CLIENT_NAME))
#    print('r_CLIENT_CMD_HASH + CLIENT_NAME + tstamp')
#    pp.pprint(r.hget(r_CLIENT_CMD_HASH + CLIENT_NAME, '1477213542890563072'))
    print('r_NEW_ADDR_SET')
    pp.pprint(r.smembers(r_NEW_ADDR_SET))
    print('r_USED_ADDR_SET')
    pp.pprint(r.smembers(r_USED_ADDR_SET))
    print('r_SALE_ADDR_SET')
    pp.pprint(r.smembers(r_SALE_ADDR_SET))
#    pp.pprint(r.hgetall(r_ADDR_CMD_HASH + 'yg57u9ueXY5RVGPGmRzQBRNz3HDeK3Nw7G'))


except Exception as e:
    print(e.args[0])
    sys.exit()

except KeyboardInterrupt:
    sys.exit(1)


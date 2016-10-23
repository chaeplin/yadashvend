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

# redis
POOL = redis.ConnectionPool(host='localhost', port=6379, db=0)
r = redis.StrictRedis(connection_pool=POOL)

pp = pprint.PrettyPrinter(indent=4)

try:
    r.ping()

except Exception as e:
    logging.info(e.args[0])
    sys.exit()

CLIENT_NAME = 'client1'

try:
    pp.pprint(r.lrange(r_MQ_LIST, 0, -1))    
    pp.pprint(r.smembers(r_CLIENT_LIST_SET))
    pp.pprint(r.hkeys(r_CLIENT_CMD_HASH + CLIENT_NAME))
    pp.pprint(r.hget(r_CLIENT_CMD_HASH + CLIENT_NAME, '1477205192623347968'))


except Exception as e:
    print(e.args[0])
    sys.exit()

except KeyboardInterrupt:
    sys.exit(1)


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
from libs.config import r_IX_LIST, r_BK_LIST, r_MQ_LIST 

import pprint

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


def dequeue(r, quelist):
    response = r.blpop(quelist, 10)
    if response != None:
        print_log('dequeue : ' + str(response))
        return response

try:

    while 1:
        quelist = (r_IX_LIST, r_BK_LIST, r_MQ_LIST)
        jobque = dequeue(r, quelist)

        if jobque:
                #pp.pprint(jobque[1])
                pp.pprint(jobque)

        else:
                pass

except KeyboardInterrupt:
    sys.exit()



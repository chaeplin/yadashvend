#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import datetime
import time
import sys
import simplejson as json
import redis

import logging
import os

from libs.dash import *
from libs.rediscommon import *
from libs.config import BIP32_TESTNET_SEED, r_ADDR_GEN_INDEX, r_NEW_ADDR_SET, max_keys_in_r_NEW_ADDR_SET

import pprint

log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../logs/' + os.path.basename(__file__) + '.log')
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s %(message)s')

# redis
POOL = redis.ConnectionPool(host='localhost', port=6379, db=0)
r = redis.StrictRedis(connection_pool=POOL)

pp = pprint.PrettyPrinter(indent=4)

# check redis
logging.info('[addr_manager] started')
try:
    r.ping()
    
except Exception as e:
    logging.info(e.args[0])
    sys.exit()

#
key = Key.from_text(BIP32_TESTNET_SEED)


# check current index
get_r_ADDR_GEN_INDEX = r_get_key(r, r_ADDR_GEN_INDEX)

if get_r_ADDR_GEN_INDEX == None:
    current_index = 0

else:
    current_index = int(get_r_ADDR_GEN_INDEX)


#
try:

    while 1:
        if r.scard(r_NEW_ADDR_SET) < max_keys_in_r_NEW_ADDR_SET:
            logging.info('[addr_manager] adding keys to key pool')
            while 1:
                addr = get_bip32_address_info(key, current_index)['addr']
                logging.info('[addr_manager] gened addr: [' + str(current_index) + '] : ' + addr)
                r_redis_sadd(r, r_NEW_ADDR_SET, addr)
                current_index = r.incr(r_ADDR_GEN_INDEX)

                if r.scard(r_NEW_ADDR_SET) > (max_keys_in_r_NEW_ADDR_SET * 2):
                    break
        
        else:
            logging.info('[addr_manager] enough keys, sleep 60 secs')
            time.sleep(10)
        
except Exception as e:
    print(e.args[0])
    sys.exit()

except KeyboardInterrupt:
    logging.info('[addr_manager] intterupted by keyboard')
    sys.exit()



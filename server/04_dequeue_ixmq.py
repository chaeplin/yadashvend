#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import datetime
import time
import sys
import simplejson as json
import redis
import paho.mqtt.publish as mqtt
import nanotime

import logging
import os

from libs.dash import *
from libs.rediscommon import *
from libs.config import r_IX_LIST, r_MQ_LIST 
from libs.config import r_NEW_ADDR_SET, r_USED_ADDR_SET, r_SALE_ADDR_SET
from libs.config import r_ADDR_CMD_HASH, r_CLIENT_CMD_HASH
from libs.config import r_SALE_PRICE
from libs.config import m_SALE_DIS_PUBLISH

import pprint

log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../logs/' + os.path.basename(__file__) + '.log')
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s %(message)s')

# redis
POOL = redis.ConnectionPool(host='localhost', port=6379, db=0)
r = redis.StrictRedis(connection_pool=POOL)

pp = pprint.PrettyPrinter(indent=4)

def get_nanotime():
    return int(nanotime.now().unixtime() * 1000000000)

def mqtt_publish(topic, payload):
    mqtt.single(topic, payload, qos=0, retain=0, hostname='127.0.0.1', port=1883)

def process_mq(r_val):
    # 1) pop an address fro NEW save it to USED and SALE(set)
    # 2) make ADDR:yxxxx hash
    # 3) send mqtt msg

    clientid = r_val['clientid']
    tstamp   = r_val['tstamp']
    item     = r_val['item']
    cmd      = r_val['cmd']
    msgid    = r_val['msgid']

    logging.info('[dequeue_ix_mq] process_mq called client: ' + str(clientid) + ' tstamp: ' + str(tstamp))

    if cmd == 'order':
        # 1)
        while 1:
            newaddr = r_spop_key(r, r_NEW_ADDR_SET)
            if newaddr != None:
                logging.info('[dequeue_ix_mq] poped : ' + newaddr)

            else:
                logging.info('[dequeue_ix_mq] no new addr in key pool')
                sys.exit()
            
            if not r.sismember(r_USED_ADDR_SET, newaddr):
                break
    
            else:
                logging.info('[dequeue_ix_mq] addr is in used pool :' + newaddr)
                

        #
#        addrdict = {
#                    'clientid': clientid,
#                    'tstamp:issued': tstamp,
#                    'item': item,
#                    'val': r_SALE_PRICE,
#                    'cmd': cmd,
#                    'msgid': msgid,
#                    'status': 'onsale'
#        }

        r_random_price = get_sale_price()

        addrdict = {
                    'clientid': clientid,
                    'tstamp:issued': tstamp,
                    'item': item,
                    'val': r_random_price,
                    'cmd': cmd,
                    'msgid': msgid,
                    'status': 'onsale'
        }

        topic = m_SALE_DIS_PUBLISH + clientid
#        payload = {
#                'addr': newaddr,
#                'val': r_SALE_PRICE,
#                'cmd': cmd,
#                'msgid': msgid
#        }

        payload = {
                'addr': newaddr,
                'val': r_random_price,
                'cmd': cmd,
                'msgid': msgid
        }

        pipe = r.pipeline()
        pipe.sadd(r_USED_ADDR_SET, newaddr)
        pipe.sadd(r_SALE_ADDR_SET, newaddr)
        pipe.hmset(r_ADDR_CMD_HASH + newaddr, addrdict)
        response = pipe.execute()
        mqtt_publish(topic, json.dumps(payload))

    elif cmd == 'change':
        pass

    elif cmd == 'discard':
        pass


def process_ix(r_val):
    # 1) check if addr is in USED(set)
    # 2) check if addr is in SALE(set)
    # 3) check r_ADDR_CMD_HASH + addr
    # 4) update r_ADDR_CMD_HASH + addr
    # 5) remove addr in sale
    # 6) updaet r_CLIENT_CMD_HASH + idcheck
    # 7) send mqtt msg


    addr = r_val['addr']
    val  = r_val['val']
    txid = r_val['txid']

    epochnano = get_nanotime()

    if r.sismember(r_USED_ADDR_SET, addr):
        if r.sismember(r_SALE_ADDR_SET, addr):
            order = r_hgetall(r, r_ADDR_CMD_HASH + addr)
            if order:     
                order_clientid = order['clientid']
                order_cmd      = order['cmd']
                order_item     = order['item']
                order_msgid    = order['msgid']
                order_status   = order['status']
                order_tstamp   = order['tstamp:issued']
                order_val      = order['val']
    
                if float(val) == float(order_val) and order_cmd == 'order' and order_status == 'onsale':
                    addrdict = {
                        'tstamp:received': epochnano,
                        'status': 'received'
                    }

                    topic = m_SALE_DIS_PUBLISH + order_clientid
                    payload = { 
                        'addr': addr,
                        'val': order_val,
                        'cmd': 'received',
                        'msgid': order_msgid
                    } 

                    pipe = r.pipeline()
                    pipe.hmset(r_ADDR_CMD_HASH + addr, addrdict)
                    pipe.srem(r_SALE_ADDR_SET, addr)
                    pipe.hset(r_CLIENT_CMD_HASH + order_clientid, 'lasttstamp', str(epochnano))
                    pipe.hset(r_CLIENT_CMD_HASH + order_clientid, 'resp:'+str(epochnano), payload) 
                    response = pipe.execute()
                    mqtt_publish(topic, json.dumps(payload))

                    #r_hgetall(r, r_ADDR_CMD_HASH + addr)
                    #r_hgetall(r, r_CLIENT_CMD_HASH + order_clientid)

        else:
            pass

    else:
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
            redis_key = jobque[0]
            redis_val = jobque[1]

            if redis_key == r_MQ_LIST:
                process_mq(json.loads(redis_val))

            if redis_key == r_IX_LIST:
                process_ix(json.loads(redis_val))

except Exception as e:
    print(e.args[0])
    sys.exit()

except KeyboardInterrupt:
    logging.info('[dequeue_ix_mq] intterupted by keyboard')
    sys.exit()


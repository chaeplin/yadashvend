import redis
from libs.printlogs import *

def r_chk_key(r, key):
    response = r.exists(key)
    logging.info('[r_chk_key] ' + key + ' : ' + str(response))
    return response

def r_get_key(r, key):
    response = r.get(key)
    logging.info('[r_get_key] ' + key + ' : ' + str(response))
    return response

def r_set_key(r, key, value):
    response = r.set(key, value)
    logging.info('[r_set_key] ' + key + ' : ' + str(response))
    return response

def r_del_key(r, key):
    response = r.delete(key)
    logging.info('[r_del_key] ' + key + ' : ' + str(response))
    return response

def r_lpush_key(r, listname, key):
    response = r.lpush(listname, key)
    logging.info('[r_lpush_key] ' + listname + ' : ' + str(key) + ' : ' + str(response))
    return response

def r_spop_key(r, key):
    response = r.spop(key)
    logging.info('[r_spop_key] ' + str(key) + ' : ' + str(response))
    return response

def r_redis_sadd(r, setname, key):
    response = r.sadd(setname, str(key))
    logging.info('[r_redis_sadd] ' +  setname + ' : ' +  key + ' : ' + str(response))
    return response

def r_redis_srem(r, key, val):
    response = r.srem(key, val)
    logging.info('[r_redis_srem key: ' + key + ' val: ' + str(val) + ' --> ' + str(response))
    return response

def r_redis_blpop(r, quelist):
    response = r.blpop(quelist, 1)
    if response != None:
        logging.info('[r_redis_blpop] ' + str(response))
        return response

def r_rpoplpush(r, src, dst):
    response = r.rpoplpush(src, dst)
    logging.info('[r_rpoplpush] src: ' + src + ' dst: ' + dst + ' ' + str(response))
    return response
 
def r_hmset(r, key, val):
    response = r.hmset(key, val)
    logging.info('[r_hmset] key: ' + key + ' val: ' + str(val) + ' --> ' + str(response))
    return response

def r_hgetall(r, key):
    response = r.hgetall(key)
    logging.info('[r_hgetall] key: ' + key + ' --> ' + str(response))
    return response


import redis
from libs.printlogs import *

def r_chk_key(r, key):
    pipe = r.pipeline()
    response = pipe.exists(key).execute()
    logging.info('[r_chk_key] ' + key + ' : ' + str(response))
    return response

def r_get_key(r, key):
    pipe = r.pipeline()
    response = pipe.get(key).execute()
    logging.info('[r_get_key] ' + key + ' : ' + str(response))
    return response

def r_set_key(r, key, value):
    pipe = r.pipeline()
    response = pipe.set(key, value).execute()
    logging.info('[r_set_key] ' + key + ' : ' + str(response))
    return response

def r_del_key(r, key):
    pipe = r.pipeline()
    response = pipe.delete(key).execute()
    logging.info('[r_del_key] ' + key + ' : ' + str(response))
    return response

def r_lpush_key(r, listname, key):
    pipe = r.pipeline()
    response = pipe.lpush(listname, key).execute()
    logging.info('[r_lpush_key] ' + listname + ' : ' + str(key) + ' : ' + str(response))
    return response

def r_spop_key(r, key):
    pipe = r.pipeline()
    response = pipe.spop(key).execute()
    logging.info('[r_spop_key] ' + str(key) + ' : ' + str(response))
    return response

def r_redis_sadd(r, setname, key):
    pipe = r.pipeline()
    response = pipe.sadd(setname, str(key)).execute()
    logging.info('[r_redis_sadd] ' +  setname + ' : ' +  key + ' : ' + str(response))
    return response

def r_redis_blpop(r, quelist):
    response = r.blpop(quelist, 10)
    if response != None:
        logging.info('[r_redis_blpop] ' + str(response))
        return response

def r_rpoplpush(r, src, dst):
    pipe = r.pipeline()
    response = pipe.rpoplpush(src, dst).execute()
    logging.info('[r_rpoplpush] ' + str(response))
    return response
 

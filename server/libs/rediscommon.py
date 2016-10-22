#!/usr/bin/env python2
import redis
from libs.printlogs import *

def r_chk_key(r, key):
    pipe = r.pipeline()
    response = pipe.exists(key).execute()
    print_log('r_chk_key : ' + key + ' : ' + str(response))
    return response

def r_get_key(r, key):
    pipe = r.pipeline()
    response = pipe.get(key).execute()
    print_log('r_get_key : ' + key + ' : ' + str(response))
    return response

def r_set_key(r, key, value):
    pipe = r.pipeline()
    response = pipe.set(key, value).execute()
    print_log('r_set_key : ' + key + ' : ' + str(response))
    return response

def r_del_key(r, key):
    pipe = r.pipeline()
    response = pipe.delete(key).execute()
    print_log('r_del_key : ' + key + ' : ' + str(response))
    return response

def r_rpush_key(r, listname, key):
    pipe = r.pipeline()
    response = pipe.rpush(listname, key).execute()
    print_log('r_rpush_key : list : ' + listname + ' : key : ' + str(key) + ' : ' + str(response))
    return response

def r_spop_key(r, key):
    pipe = r.pipeline()
    response = pipe.spop(key).execute()
    print_log('r_spop_key : ' + str(key) + ' : ' + str(response))
    return response

def r_redis_sadd(r, setname, key):
    pipe = r.pipeline()
    response = pipe.sadd(setname, str(key)).execute()
    print_log('r_redis_sadd : ' +  setname + ' : ' +  key + ' : ' + str(response))
    return response


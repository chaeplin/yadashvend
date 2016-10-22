#!/usr/bin/env python2

# seed for generate address
BIP32_TESTNET_SEED = 'DRKPuUb97UQHNUHs5ktawTeAdwMsBaHCsLA1JW8iYpK5orXyiKPba3MyTP4sttpzhWdVKNej2TxkhR3WNrQqWGMg64ood5HaXL5Avi9ad5vaqc8U'

# max keys in r_NEW_ADDR_SET
max_keys_in_r_NEW_ADDR_SET = 100

#key prefix
key_prefix = 'testnet:'

# redis
# key for index of key generation
r_ADDR_GEN_INDEX = key_prefix + 'kusubsetindex'

# SET Unused address pool
r_NEW_ADDR_SET  = key_prefix + 'NEW_ADDRS'
r_USED_ADDR_SET = key_prefix + 'USED_ADDRS'
r_SALE_ADDR_SET = key_prefix + 'SALE_ADDRS'

# hash
r_HASH_PREFIX = 'testnet:'

# list for ix tx and blk hash
r_IX_LIST = key_prefix + 'IX_RECEIVED'
r_BK_LIST = key_prefix + 'BK_RECEIVED'
r_MQ_LIST = key_prefix + 'MQ_RECEIVED'

# 
r_SALE_PRICE = 0.02

#
m_SALE_REQ_SUBSCRIBE = 's/req/#'
m_SALE_DIS_PUBLISH   = 's/resp/'

#client1
#    publish to    --> s/req/client1 
#                      {"clientid":"client1", "type":"req"}
#    subscribe to  --> s/resp/client1 
#                      {"addr":"yyyyy", "val":"ffff", "type":"response"}
#                      {"addr":"yyyyy", "val":"ffff", "type":"received"}
#                      {"addr":"yyyyy", "val":"ffff", "type":"discard"}
#

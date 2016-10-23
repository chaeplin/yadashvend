import logging
import os
import sys
import nanotime

def get_nanotime():
    return int(nanotime.now().unixtime() * 1000000000)

log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../yadashvend.log')
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s %(message)s')


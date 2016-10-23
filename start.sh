#!/bin/sh
# install pm2
pm2 list

pm2 start ~/yadashvend/server/01_addr_manager.py
pm2 start ~/yadashvend/server/02_ixbl_queue.py
pm2 start ~/yadashvend/server/03_mqtt_queue.py
pm2 start ~/yadashvend/server/04_dequeue_ixmq.py

pm2 list


tail -f ~/yadashvend/server/yadashvend.log 

#!/bin/sh
# install pm2
pm2 list

pm2 restart all

tail -f ~/yadashvend/server/yadashvend.log 

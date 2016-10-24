#!/bin/sh
# install pm2
pm2 list

pm2 stop all
pm2 delete all


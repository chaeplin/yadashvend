#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import time
import datetime
import simplejson as json
import paho.mqtt.client as mqtt
import subprocess

def sendto(addr, val):
	try:
		cmd = "/usr/local/bin/dash-cli instantsendtoaddress " + addr + " " + val
        	with subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout as f:
			result = f.read().splitlines()
			print(result)

	except Exception, e:
		raise e	

def on_connect(client, userdata, flags, rc):
	client.subscribe('s/resp/sendto', 0)

def on_message(client, userdata, msg):
	print (msg.topic+" "+str(msg.payload))
	if msg.topic == 's/resp/sendto':
		req = json.loads(msg.payload)
		sendto(req['sendto'], req['value'])

# mqtt
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

try:
    client.connect('127.0.0.1', 1883, 10)
    #client.loop_start()
    client.loop_forever()

except Exception as e:
    print(e.args[0])
    sys.exit()

except KeyboardInterrupt:
    sys.exit(1)
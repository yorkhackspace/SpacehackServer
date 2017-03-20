#!/usr/bin/env python

# This is a test client emulator it just spits out some config
# and buttons for testing....

import paho.mqtt.client as paho
import logging as log

from time import sleep
import json

logger = log.getLogger()
logger.setLevel(log.DEBUG)

client = paho.Client('TestClient')
server = "127.0.0.1"


def on_connect(mosq, obj, rc):
    """Receive MQTT connection notification"""
    if rc == 0:
        log.info("Connected to MQTT")
    else:
        log.error("Failed - return code is " + rc)


def on_message():
    pass


client.on_connect = on_connect
client.on_message = on_message
client.connect(server)

console_config = {
    "ip": "192.168.1.1",
    "controls": [
        {
            "id": "1",
            "gamestart": "1",
            "width": 16,
            "supported": [
                {
                    "type": "button"
                 }
            ]
        }
    ]
}

client.publish('server/register', json.dumps(console_config))
console_config['ip'] = "192.168.1.2"
sleep(1)
client.publish('server/register', json.dumps(console_config))

sleep(1)
client.publish('clients/192.168.1.1/1/value', "1")
client.publish('clients/192.168.1.2/1/value', "1")

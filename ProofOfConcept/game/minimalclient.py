#Console game client - proof of concept demo
#York Hackspace - Bob November 2013
#This runs on a Beaglebone Black
#This is a minimal version with all the hardware interaction taken out.

import mosquitto
import commands

#Who am I?
ipaddress = commands.getoutput("/sbin/ifconfig").split("\n")[1].split()[1][5:]

#MQTT client
client = mosquitto.Mosquitto("Game-" + ipaddress) #client ID
server = "192.168.1.30" #fixed IP address of server

#MQTT message arrived
def on_message(mosq, obj, msg):
    print(msg.topic + " - " + str(msg.payload))


#Setup MQTT
client.on_message = on_message
client.connect(server)

client.subscribe("control1")
client.subscribe("control2")
client.subscribe("instruction")
client.subscribe("digit1")
client.subscribe("digit2")

#Set MQTT listening
client.loop_forever()

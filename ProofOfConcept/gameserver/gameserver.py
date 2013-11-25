#Console game server - proof of concept demo
#York Hackspace - Bob November 2013
#This runs on a Raspberry Pi

import controls
import mosquitto
import time
import random
import PiLiteLib

#MQTT client to allow publishing
client = mosquitto.Mosquitto("PiServer") #ID shown to the broker
lastgenerated = 0
server = "127.0.0.1" #Mosquitto MQTT broker running locally

#PiLite for notifications
pilite = PiLiteLib.PiLiteBoard()

#Show when we've connected
def on_connect(mosq, obj, rc):
    if rc == 0:
        print("Connected to MQTT")
        pilite.write("Ready!")	
    else:
        print("Failed - return code is " + rc)

#Connect to MQTT (final code should make this a retry loop)
client.on_connect = on_connect
client.connect(server)

#Main loop
while(client.loop() == 0): 
    #Every five seconds...
    if time.time()-lastgenerated > 5:
        #Dump another batch of random control names and action
        control1=controls.getControlName()
        control2=controls.getControlName()
        instruction = controls.getRandomAction(random.choice([control1,control2]))
        digit1 = random.choice([str(random.choice(range(11))), random.choice(controls.safewords).upper()])
        digit2 = str(random.choice(range(11)))

        client.publish("control1", control1, 0)
        client.publish("control2", control2, 0)
        client.publish("instruction", instruction, 0)
        client.publish("digit1", digit1, 0)
        client.publish("digit2", digit2, 0)

        print("control 1 = " + control1)
        print("control 2 = " + control2)
        print("instruction = " + instruction)
        print("digit1 = " + digit1)
        print("digit2 = " + digit2)
	
        pilite.write(digit1)

        lastgenerated = time.time()

#If client.loop() returns non-zero, loop drops out to here.
#Final code should try to reconnect to MQTT and/or networking if so.

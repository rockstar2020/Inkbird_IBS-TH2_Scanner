#!/usr/bin/env python3

from time import sleep
import os
import sys
import json
import datetime
import time

from bleson import get_provider, Observer, UUID16
from bleson.logger import log, set_level, ERROR, DEBUG

# Disable warnings
set_level(ERROR)

# # Uncomment for debug log level
#set_level(DEBUG)

MAC = "HERE YOU HAVE TO ADD YOUR MAC ADDRESS"

H5075_UPDATE_UUID16 = UUID16(0xEC88)

inkbird_devices = {}


#MQTT Configuration
import paho.mqtt.client as mqtt
server="IP ADDRESS OF YOUR MQTT SERVER"
port=1883  ###Change this port if your MQTT uses different port
user="USER NAME OF MQTT"
passwd="YOUR PASSWORD"
client=mqtt.Client("INK")
client.username_pw_set(user,passwd)

###########################################################################
###On BLE advertisement callback
def on_advertisement(advertisement):
    log.debug(advertisement)
    if advertisement.address.address == MAC and advertisement.mfg_data is not None:
        mac = advertisement.address.address
        if mac not in inkbird_devices:
            inkbird_devices[mac] = {}
        itemp = int.from_bytes(advertisement.mfg_data[0:2], 'little')/100
        ihum = int.from_bytes(advertisement.mfg_data[2:4], 'little')/100
        ibat = int.from_bytes(advertisement.mfg_data[7:8], 'little')
        inkbird_devices[mac]["address"] = mac
        inkbird_devices[mac]["temp"] = itemp
        inkbird_devices[mac]["hum"] = ihum
        inkbird_devices[mac]["battery"] = ibat
        publish_mqtt(mac)
        #print(inkbird_devices[mac])

########### PUBLISH TO MQTT ################
def publish_mqtt(mac):
    client.connect(server,port)
    t_now = datetime.datetime.now()
    t = time.mktime(t_now.timetuple())
    if mac == MAC:
        stat_dict = {"temp": inkbird_devices[mac]["temp"], "humidity": inkbird_devices[mac]["hum"], "battery": inkbird_devices[mac]["battery"], "time": t}
        stat = json.dumps(stat_dict)
        client.publish("stat/inkbird/stat",stat , qos=0, retain=False)
    client.disconnect()
############################################################################
adapter = get_provider().get_adapter()
observer = Observer(adapter)
observer.on_advertising_data = on_advertisement
observer.start()
sleep(5)
observer.stop()
sys.exit(0)



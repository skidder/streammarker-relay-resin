#!/usr/bin/python

import pprint
import calendar
import httplib
import json
import os
import re
import serial
import sys
import time

from xbee import ZigBee

headers = {"Content-type": "application/json",
           "Accept": "application/json"}
if 'STREAMMARKER_API_KEY' in os.environ:
    headers["X-API-KEY"] = os.environ['STREAMMARKER_API_KEY']

r_unwanted = re.compile("[\n\r]")
pp = pprint.PrettyPrinter(indent=4)

serial_port = serial.Serial('/dev/ttyAMA0', 9600)
xbee = ZigBee(serial_port)

print("xonxoff", serial_port.xonxoff)
print("rtscts", serial_port.rtscts)
print("dsrdtr", serial_port.dsrdtr)

while True:
    try:
        data = xbee.wait_read_frame()

        sensor_mac = ':'.join("{:02X}".format(ord(c))
                              for c in data['source_addr_long'])
        msg = data['rf_data']
        pp.pprint(data)
        msg = r_unwanted.sub("", msg)
        readings = msg.split(',')
        reading_timestamp = int(calendar.timegm(time.gmtime()))
        if len(readings) == 5:
            body = json.dumps({"timestamp": reading_timestamp, "relay_id": "3AC91DEC-B0DD-4DB5-B56D-7682B7C9B28C", "status": "ok", "sensors": [{"id": sensor_mac, "readings": [{"timestamp": reading_timestamp, "measurements": [
                              {"name": "soil_moisture_1", "value": float(readings[1]), "unit":"VWC"}, {"name": "soil_temperature_1", "value": float(readings[2]), "unit":"Celsius"}, {"name": "enclosure_temperature", "value": float(readings[0]), "unit":"Celsius"}, {"name": "external_temperature", "value": float(readings[3]), "unit":"Celsius"}, {"name": "external_humidity", "value": float(readings[4]), "unit":"RH"}]}]}]})
        else:
            body = json.dumps({"timestamp": reading_timestamp, "relay_id": "3AC91DEC-B0DD-4DB5-B56D-7682B7C9B28C", "status": "ok", "sensors": [{"id": sensor_mac, "readings": [{"timestamp": reading_timestamp, "measurements": [
                              {"name": "soil_moisture_1", "value": float(readings[1]), "unit":"VWC"}, {"name": "soil_temperature_1", "value": float(readings[2]), "unit":"Celsius"}, {"name": "enclosure_temperature", "value": float(readings[0]), "unit":"Celsius"}]}]}]})
        print body

        conn = httplib.HTTPConnection("api.streammarker.com", 80)
        conn.request("POST", "/api/v1/sensor_readings", body, headers)
        resp = conn.getresponse()
        print(resp.status, resp.reason)

    except KeyboardInterrupt:
        break
    except:  # catch-all
        e = sys.exc_info()[0]
        print(e)

serial_port.close()

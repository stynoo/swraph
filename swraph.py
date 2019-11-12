#!/bin/env python
"""Weatherdata -> MQTT broker"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import paho.mqtt.publish as publish


def data2dict(data):
    """Wrapping the data into a dict."""
    keys = []
    values = []
    for dat in data:
        somekey = dat.split("=")[0]
        keys.append(somekey)
        somevalue = dat.split("=")[1]
        values.append(somevalue)
    datadict = dict(zip(keys, values))
    return datadict


def far2cel(temp):
    """Farenheit 2 Celcius."""
    return round((float(temp) - 32) * 5 / 9, 1)


def mph2kph(speed):
    """Miles 2 Kilometers."""
    return round(float(speed) * 1.609, 1)


def send2mqtt(topic, data):
    """Send stuff to MQTT"""
    broker = "127.0.0.1"
    try:
        publish.single(topic, data, hostname=broker)
    except:
        print("Sending data to MQTT broker failed...")


def parsedatadict(datadict):
    """Parse the dict for meaningfull info."""
    if datadict["model"] in "WS2900":
        print("Date+Time (UTC):", datadict["dateutc"])
        print("Weather Station Model (str):", datadict["model"])
        print("Weather Station Firmware (string):", datadict["stationtype"])
        print("Absolute Pressure (Hg):", datadict["baromabsin"])
        print("Relative Pressure (Hg):", datadict["baromrelin"])
        print("Daily Rain (in):", datadict["dailyrainin"])
        print("Event Rain (in):", datadict["eventrainin"])
        print("Outdoor Humidity (%):", datadict["humidity"])
        print("Indoor Humidity (%):", datadict["humidityin"])
        print("Monthly Rain (in):", datadict["monthlyrainin"])
        print("Rate of rainfall (inches per hour):", datadict["rainratein"])
        print("Solar Radiation (W/m^2):", datadict["solarradiation"])
        print("Outdoor Temperature (ºF):", datadict["tempf"])
        print("Indoor Temperature (ºF):", datadict["tempinf"])
        print("Total Rain (in, since last factory reset):", datadict["totalrainin"])
        print("Ultra-Violet Radiation Index (int):", datadict["uv"])
        print("Weekly Rain (in):", datadict["weeklyrainin"])
        print("Instantaneous Wind Direction (0-360°):", datadict["winddir"])
        print("Max Wind Speed In The Last 10 Minutes (mph):", datadict["windgustmph"])
        print("Instantaneous Wind Speed (mph):", datadict["windspeedmph"])

        datadict["tempc"] = far2cel(datadict["tempf"])
        datadict["tempinc"] = far2cel(datadict["tempinf"])
        datadict["windgustkph"] = mph2kph(datadict["windgustmph"])
        datadict["windspeedkph"] = mph2kph(datadict["windspeedmph"])

        print("CALC - Outdoor Temperature (ºC):", datadict["tempc"])
        print("CALC - Indoor Temperature (ºC):", datadict["tempinc"])
        print(
            "CALC - Max Wind Speed In The Last 10 Minutes (kph):",
            datadict["windgustkph"],
        )
        print("CALC - Instantaneous Wind Speed (kph):", datadict["windspeedkph"])

        send2mqtt("home-assistant/weather/tempc", datadict["tempc"])
        send2mqtt("home-assistant/weather/humidity", datadict["humidity"])
        send2mqtt("home-assistant/weather/windspeedkph", datadict["windspeedkph"])
    else:
        print(datadict["model"], datadict["stationtype"], "is untested.")
    print("---------------------------------------------------------------")


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    """We need this to capture POST."""

    def do_POST(self):
        """Actually do something on POST."""
        content_length = int(self.headers["Content-Length"])
        data = self.rfile.read(content_length).decode("utf-8").split("&")
        datadict = data2dict(data)
        parsedatadict(datadict)


# Scarlet Weather Rhapsody - the villain is above the clouds - sending stuff to port 10080
HTTPD = HTTPServer(("", 10080), SimpleHTTPRequestHandler)
HTTPD.serve_forever()

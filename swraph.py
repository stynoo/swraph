#!/bin/env python
"""Weatherdata -> MQTT broker"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import paho.mqtt.publish as publish

DESCRIPTIONS = {
    "dateutc": "Date+Time (UTC)",
    "model": "Weather Station Model (str)",
    "stationtype": "Weather Station Firmware (string)",
    "baromabsin": "Absolute Pressure (inHg)",
    "baromrelin": "Relative Pressure (inHg)",
    "dailyrainin": "Daily Rain (in)",
    "eventrainin": "Event Rain (in)",
    "humidity": "Outdoor Humidity (%)",
    "humidityin": "Indoor Humidity (%)",
    "monthlyrainin": "Monthly Rain (in)",
    "rainratein": "Rate of rainfall (inches per hour)",
    "solarradiation": "Solar Radiation (W/m^2)",
    "tempf": "Outdoor Temperature (ºF)",
    "tempinf": "Indoor Temperature (ºF)",
    "totalrainin": "Total Rain (in, since last factory reset)",
    "uv": "Ultra-Violet Radiation Index (int)",
    "weeklyrainin": "Weekly Rain (in)",
    "winddir": "Instantaneous Wind Direction (0-360°)",
    "windgustmph": "Max Wind Speed In The Last 10 Minutes (mph)",
    "windspeedmph": "Instantaneous Wind Speed (mph)",
    "tempc": "CALC - Outdoor Temperature (ºC)",
    "tempinc": "CALC - Indoor Temperature (ºC)",
    "windgustkph": "CALC - Max Wind Speed In The Last 10 Minutes (kph)",
    "windspeedkph": "CALC - Instantaneous Wind Speed (kph)",
    "dailyrainmm": "CALC - Daily Rain (mm)",
    "eventrainmm": "CALC - Event Rain (mm)",
    "monthlyrainmm": "CALC - Monthly Rain (mm)",
    "rainratemm": "CALC - Rate of rainfall (mm per hour)",
    "weeklyrainmm": "CALC - Weekly Rain (mm)",
    "baromabshpa": "CALC - Absolute Pressure (hPa)",
    "baromrelhpa": "CALC - Relative Pressure (hPa)",
}


def far2cel(temp):
    """Farenheit 2 Celcius."""
    return round((float(temp) - 32) * 5 / 9, 1)


def mph2kph(speed):
    """Miles 2 Kilometers."""
    return round(float(speed) * 1.609, 1)


def in2mm(lenght):
    """Inches 2 Millimeters."""
    return round(float(lenght) * 25.4)


def inhg2hpa(pressure):
    """Inch of mercury 2 Hectopascal."""
    return round(float(pressure) * 33.8639)


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


def send2mqtt(topic, value, description):
    """Send stuff to MQTT"""
    broker = "127.0.0.1"
    try:
        publish.single(topic, value, hostname=broker)
        print(description + ":", value)
    except:
        print("Failed sending", value, "to MQTT broker", broker, "on topic", topic)


def parsedatadict(datadict):
    """Parse the dict, elevate with calculated data and forward to mqtt."""
    if datadict["model"] in "WS2900":
        datadict["tempc"] = far2cel(datadict["tempf"])
        datadict["tempinc"] = far2cel(datadict["tempinf"])
        datadict["windgustkph"] = mph2kph(datadict["windgustmph"])
        datadict["windspeedkph"] = mph2kph(datadict["windspeedmph"])
        datadict["dailyrainmm"] = in2mm(datadict["dailyrainin"])
        datadict["eventrainmm"] = in2mm(datadict["eventrainin"])
        datadict["monthlyrainmm"] = in2mm(datadict["monthlyrainin"])
        datadict["rainratemm"] = in2mm(datadict["rainratein"])
        datadict["weeklyrainmm"] = in2mm(datadict["weeklyrainin"])
        datadict["baromabshpa"] = inhg2hpa(datadict["baromabsin"])
        datadict["baromrelhpa"] = inhg2hpa(datadict["baromrelin"])

        for mydata in datadict:
            mykey = mydata
            myval = datadict[mykey]
            mqqttopic = "home-assistant/weather/" + mykey
            try:
                mydes = DESCRIPTIONS[mykey]
            except:
                mydes = "No description found for " + mykey
            send2mqtt(mqqttopic, myval, mydes)
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

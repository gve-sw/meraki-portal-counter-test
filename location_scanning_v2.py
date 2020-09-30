"""
    LICENSE 
    #########################################################################
    Copyright (c) 2020 Cisco and/or its affiliates.

    This software is licensed to you under the terms of the Cisco Sample
    Code License, Version 1.1 (the "License"). You may obtain a copy of the
    License at

                https://developer.cisco.com/docs/licenses

    All use of the material herein must be in accordance with the terms of
    the License. All rights not expressly granted by the License are
    reserved. Unless required by applicable law or agreed to separately in
    writing, software distributed under the License is distributed on an "AS
    IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
    or implied.
    ##########################################################################

    #
    #
    #
    #
    #
    #

    README:

        This script uses Meraki Scanning API to detect wireless devices.
        Scanning API sends scanning information to server.
        Hence, we use Flask to query information sent to the server.
        Detected device information is placed in elasticsearch.

        For more information on what is captured refer to description document.
        On how to set up Meraki API refer to setup document.
"""


from flask import Flask, json, request, render_template
import sys, getopt
import json
import time 
from datetime import datetime
from pprint import pprint
import importlib.util

# Import all sensitive data from config file
from config import SCANNING_INDEX_NAME as INDEX_NAME
from config import VALIDATOR as validator
from config import SECRET as secret
from config import VERSION
from config import LOCATION_DATA as locationdata

# Import elasticserach handler
import elastic_handler as es_handler

app = Flask(__name__)

# Respond to Meraki with validator
@app.route("/", methods=["GET"])
def get_validator():
    print("validator sent to: ", request.environ["REMOTE_ADDR"])
    return validator


# Accept CMX JSON POST
@app.route("/", methods=["POST"])
def get_locationJSON():
    global locationdata

    if not request.json or not "data" in request.json:
        return ("invalid data", 400)

    locationdata = request.json

    device_info = locationdata["data"]["observations"]

    AP_info = {
        "apFloors" : locationdata["data"]["apFloors"],
        "apMac" : locationdata["data"]["apMac"]
        }

    # Connect to elasticsearch database
    es_conn = es_handler.connect_elasticsearch(es_handler.HOST_URL)

    # Get current time and date making sure if follows the correct format.
    now = datetime.now()
    current_date = now.strftime("%Y-%m-%dT%H:%MZ")
    
    # Number of devices detected represented by number of entries in response.
    device_count = len(device_info)

    # For each device get information and write it to elasti index
    for item in device_info:

        client_Mac = item["clientMac"]
        client_manufacturer = item["manufacturer"]
        client_location = item["location"]

        # Elastic index keys and values to be placed for those keys
        keys = ["date", "AP_floor", "AP_mac","averageCount", "client_Mac", "client_manufacturer", "clientLocation_Lat", "clientLocation_lng"]
        data_es = [current_date, AP_info["apFloors"], AP_info["apMac"], int(device_count), client_Mac, client_manufacturer, client_location["lat"], client_location["lng"]]
        
        # Create body for elastic request.
        es_values = es_handler.create_body(keys, data_es)

        # Add this info into elastic index
        es_response = es_handler.add_document(es_conn, INDEX_NAME, None, None, es_values)
        print(es_response)

    print("Received POST from ", request.environ["REMOTE_ADDR"])

    # Return success message
    return "Location Scanning POST Received"


@app.route("/go", methods=["GET"])
def get_go():
    return render_template("index.html", **locals())


@app.route("/clients/", methods=["GET"])
def get_clients():
    global locationdata
    if locationdata != "Location Data Holder":
        return json.dumps(locationdata["data"]["observations"])

    return ""


@app.route("/clients/<clientMac>", methods=["GET"])
def get_individualclients(clientMac):
    global locationdata
    for client in locationdata["data"]["observations"]:
        if client["clientMac"] == clientMac:
            return json.dumps(client)

    return ""


def main(argv):
    global validator
    global secret

    try:
        opts, args = getopt.getopt(argv, "hv:s:", ["validator=", "secret="])
    except getopt.GetoptError:
        print("locationscanningreceiver.py -v <validator> -s <secret>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            print("locationscanningreceiver.py -v <validator> -s <secret>")
            sys.exit()
        elif opt in ("-v", "--validator"):
            validator = arg
        elif opt in ("-s", "--secret"):
            secret = arg

    print("validator: " + validator)
    print("secret: " + secret)
    

if __name__ == "__main__":

    main(sys.argv[1:])
    app.run(host="0.0.0.0", port=5000, debug=False)
      

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

        This script is used to get number of people meraki camera captures.
        Camera frame is split into 2 zones:
            - Left zone = people leaving
            - Right zone = people entering
        Every 5 minutes this information is queried using meraki API.

        Script keeps count of people in the store based on how many people enter and how many people leave the store.

        Information is then pushed to elasticsearch index.

        On how to set up Meraki API refer to setup document.
"""

import time
import requests
import json
from datetime import datetime

# Import Meraki libraries and dependencies
from meraki_sdk.meraki_sdk_client import MerakiSdkClient
from meraki_sdk.models.object_type_enum import ObjectTypeEnum
from meraki_sdk.exceptions.api_exception import APIException

# Import elasticserach handler
import elastic_handler as es_handler

# Import all sensitive data from config file
from config import CAMERA_INDEX_NAME as INDEX_NAME
from config import MERAKI_API_KEY
from config import CAMERA_SERIAL

#Total people in store initially when script begins is zero 
in_store_total = 0

# Specify the field keys for elastic
es_keys = ["date",  "entrances_left", "entrances_right", "in_store_new", "in_store_total"]


# Keep looping until process terminates
while True:
    
    # Connect to elastic database
    es_conn = es_handler.connect_elasticsearch(es_handler.HOST_URL)

    #Find time variables
    epoch_t0 = int(time.time())-300 #time 5 minutes ago
    epoch_t1 = int(time.time())     #time right now

    # Make Connection to camera based on API Key
    client = MerakiSdkClient(MERAKI_API_KEY)
    mv_sense_controller = client.mv_sense
    # Can select between PERSON and VEHICLE. we are counting people
    object_type = ObjectTypeEnum.PERSON 

    # Create collection that has values needed to query camera API
    # serial number of the camera, time frame and what we wish to count (i.e. people)
    collect = {
        'serial' : CAMERA_SERIAL,
        't_0'    : epoch_t0,
        't_1'    : epoch_t1,
        'object_type'   : object_type
    }

    try:
        # Run the API call and get information based on values specified in collect
        result = mv_sense_controller.get_device_camera_analytics_overview(collect)

        # get current time and date making sure if follows the correct format.
        now = datetime.now()
        current_date = now.strftime("%Y-%m-%dT%H:%MZ")

        # Total people exiting store
        entrances_left = result[1]['entrances']
        # Total people entering store
        entrances_right = result[2]['entrances']

        # Calculate how many people are there in the store at this moment.
        in_store_new =  entrances_right - entrances_left
        in_store_total = in_store_new + in_store_total

        # Prepare data that needs to be written to elastic index
        # Match key with value
        data = [current_date, entrances_left,entrances_right,in_store_new,in_store_total]
        es_values = es_handler.create_body(es_keys, data)

        # Add this info into elastic index
        es_response = es_handler.add_document(es_conn, INDEX_NAME, None, None, es_values)
        print(es_response)

    except Exception as exp: 
        print("Process failed!")
        print("Reason: {}".format(str(exp)))

    # Give a 5 minute break before executing again
    time.sleep(300)

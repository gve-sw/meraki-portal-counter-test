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

    Contains sensitive config data.

    We recommend you do NOT share this file on public GitHub.
    This file contains sensitive API and secret keys,and ngrok urls.

    Anyone with these Meraki APIs and secret keys will be able to access AP and Camera used for the project.
    Also ngrok urls are used for elastic search and kibana, and are publuc URL.
    There is no authentication setup for making queries to Elasticsearch or Kibana access.

    RECOMMENDATION:
        This file is part of git ignore and it should stay that way.
        Everyone should have their own copy locally and not distribute this information publicly.

    Information displayed here is just for demo purpose and has been chnaged, hence it is not valid anymore.
"""

# Information for camera count
CAMERA_INDEX_NAME = "camera_count"
MERAKI_API_KEY = 'xxxxxxxxxxff4ba983d1a8d245bfc9xxxxxxxx' 
CAMERA_SERIAL = 'QXXV-XXXX-QXXX' 

# Scanning information
SCANNING_INDEX_NAME = "scanning_count"
VALIDATOR = "XXXXXXX316b9be9567fc8283081e444XXXXXXX"
SECRET = "XXXXXXXXXXXXXXX"
VERSION = "2.0"  
LOCATION_DATA = "Location Data Holder"

# Splash page
SPLASH_INDEX_NAME = "splash_count"

# Elasticsearch - Change this based on your ngrok URL
ES_HOST_URL = ["https://bd3e6a06.ngrok.io"]

# Kibana - Chnage this based on your ngrok URL 
KIBANA_URL = "https://dd5b7acc.ngrok.io"

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

    This script is only run when you want to create new index.
    It runs line by line and tries to create the index, if index already exists,
    it skips to the next one. Not a good coding practice, I know,
    but it is only used once, so don't judge me too much.

    Generally speaking, this script should only be run once,
    when you are setting up your environment for the first time
    and you want to set up elasticsearch.

    For more information on elasticsearch indices refer to documentation.

    Dependencies:
        Python Module   : elasticsearch
        Code            : config.py
"""

from elasticsearch import Elasticsearch
from config import ES_HOST_URL as HOST_URL

from config import CAMERA_INDEX_NAME
from config import SCANNING_INDEX_NAME
from config import SPLASH_INDEX_NAME

es_conn = Elasticsearch(HOST_URL)

# --------------------------------------
# Create index for camera count
try:
    settings = {
        "settings" : {
            "number_of_shards" : 1
        },
        "mappings" : {
            "properties" : {
                "date" : { "type" : "date", "format" : "date_time" },
                "entrances_left" : { "type" : "integer" },
                "entrances_right" : { "type" : "integer" },
                "in_store_new" : { "type" : "integer" },
                "in_store_total" : { "type" : "integer" }
            }
        }
    }

    es_conn.indices.create(index=CAMERA_INDEX_NAME, body=settings)

    print("{} index has been created.".format(SCANNING_INDEX_NAME))
except Exception as exp:
    print(exp)

# ----------------------------------------
# Create index for ssid scanning count
try:
    settings = {
        "settings" : {
            "number_of_shards" : 1
        },
        "mappings" : {
            "properties" : {
                "date" : { "type" : "date" },
                "AP_floor" : { "type" : "text" },
                "AP_mac" : { "type" : "text" },
                "averageCount" : { "type" : "integer" },
                "client_Mac" : { "type" : "text" },
                "client_manufacturer" : { "type" : "text" },
                "clientLocation_Lat" : { "type" : "float" },
                "clientLocation_lng" : { "type" : "float" }
            }
        }
    }
    
    es_conn.indices.create(index=SCANNING_INDEX_NAME, body=settings)

    print("{} index has been created.".format(SCANNING_INDEX_NAME))
except Exception as exp:
    print(exp)

# ----------------------------------------

# Create index for splash page count with extended values
try:
    settings = {
        "settings" : {
            "number_of_shards" : 1
        },
        "mappings" : {
            "properties" : {
                "date" : { "type" : "date", "format" : "date_time" },
                "client_mac" : { "type" : "text" },
                "client_ip" : {"type" : "ip"},
                "user_email" : {"type" : "text"},
                "user_age" : {"type" : "integer"},
                "user_gender" : {"type" : "text"},
                "product_interest" : {"type" : "text"},
                "brand_interest" : {"type" : "text"} 
            }
        }
    }

    es_conn.indices.create(index=SPLASH_INDEX_NAME, body=settings)

    print("{} index has been created.".format(SPLASH_INDEX_NAME))
except Exception as exp:
    print(exp)

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

        This Script is used to as a module with helper functions that can be used by other scripts.
        It contains functions regarding elasticsearch.

        For more details on how elasticsearch is deployed refer to setup documentation.

        Dependencies:
            Python Module   : elasticsearch
            Code            : config.py
"""

from datetime import datetime
import elasticsearch
from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
import json

from config import ES_HOST_URL as HOST_URL


def connect_elasticsearch(host_url):
    """
        Establish Connection to elasticsearch database
    """
    print("Connecting to elasticsearch...")

    es_conn = None
    es_conn = Elasticsearch(host_url)

    if es_conn.ping():
        print('Yay Connected!')
        print("Connection:{}".format(es_conn))
    else:
        print('Unable to connect!')
        print("Connection:{}".format(es_conn))

    return es_conn


def create_body(keys, values):
    """
        Match keys and values to create dictionary object to be placed in elastic index.
    """
    if len(keys) == len(values):
        body_values = dict(zip(keys, values))
        print(body_values)
        return body_values
    else:
        print("Unable to convert to body")
    return None


def add_document(es_conn, index_name, doc_type, doc_id, body_data):
    """
        Add values to elastic index
    """
    print("Adding data to elastic index...")

    try:
        es_response = es_conn.index(index=index_name, doc_type=doc_type, id=doc_id, body=body_data)
        print(es_response)
        return "Success"
    except Exception as ex:
        print("No data will be pushed to elastic index!")
        print("Reason: {}".format(str(ex)))
        return "Fail"


def get_documents(es_conn, index_name, doc_type):
    """
        Display all values in of specific index.
    """
    try:
        # Query all values elastic documents that belong to specified index.
        es_response = scan(
            es_conn,
            index=index_name,
            doc_type=doc_type,
            query={"query": { "match_all" : {}}}
        )

        for item in es_response:
            print(json.dumps(item))

    except Exception as ex:
        print("Unable to query data!")
        print("Reason: {}".format(str(ex))) 


def get_indices(es_conn):
    """
        Get all available indices from elastic database.
    """
    try:
        for index in es_conn.indices.get('*'):
            print(index)
    except Exception as ex:
        print("Unable to query indices!")
        print("Reason: {}".format(str(ex))) 


if __name__ == "__main__":

    # If you run this scrip as it is it will just connect to elasticserach server.
    es_conn = connect_elasticsearch(HOST_URL)
    print(es_conn)
    # And display all available indices.
    get_indices(es_conn)
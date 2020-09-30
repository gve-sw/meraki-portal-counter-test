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

    Get information from splash page.

    When user conects to Meraki AP they are greeted with plash page.
    Meraki then captures this information and send it to server as http request.
    This can then be accessed though browser url.

    This code acts as a server that hosts front-end for captive portal.
    It also captures url that meraki forms and stores information to elastic database.
    It also decides on where to redirect the user after login was successful based on the information they provided in splash page.

    On how to set up Meraki AP Splash Page refer to setup document.

    Dependencies:
        - Python module     : Flask
        - Code              : elastic_handler.py ; config.py
        - External Tools    : Meraki AP
"""


from pprint import pprint
from flask import Flask, request, render_template, redirect, url_for, json
import sys, getopt
import json
import random

from datetime import datetime

# Import elasticserach handler
import elastic_handler as es_handler
# Import all sensitive data from config file
from config import SPLASH_INDEX_NAME as INDEX_NAME

app = Flask(__name__)

global base_grant_url
base_grant_url = ""
global user_continue_url
user_continue_url = ""
global success_url
success_url = ""
global client_ip
client_ip = ""
global client_mac
client_mac = ""
global advert_link
advert_link = "https://www.verizonwireless.com/deals/free-phones/"


@app.route("/click", methods=["GET"])
def get_click():
    global base_grant_url
    global user_continue_url
    global success_url
    global client_ip
    global client_mac

    host = request.host_url
    base_grant_url = request.args.get('base_grant_url')
    user_continue_url = request.args.get('user_continue_url')
    node_mac = request.args.get('node_mac')
    client_ip = request.args.get('client_ip')
    client_mac = request.args.get('client_mac')
    splashclick_time = request.args.get('splashclick_time')
    success_url = host + "success"

    return render_template("click.html", client_ip=client_ip,
    client_mac=client_mac, node_mac=node_mac,
    user_continue_url=user_continue_url,success_url=success_url)


@app.route("/login", methods=["POST"])
def get_login():
    """ 
        For getting information when user gets redirected to splash page.
    """

    global base_grant_url
    global success_url
    global client_ip
    global client_mac
    global advert_link

    # Get information user has provided in the login form.
    user_email = request.form['user_email_address']
    user_gender = request.form['user_gender']
    user_year = request.form['user_age']

    # Convert birth year to age
    user_age = int(datetime.now().year) - int(user_year)

    # Get list of user brand and product interest
    product_interest_list = request.form.getlist('user_interests')
    brand_interest_list = request.form.getlist('user_brand_interests')

    # get link for advertisement
    advert_link = get_advert_link(user_age, user_gender, product_interest_list, brand_interest_list)

    # Convert list of interests to string so it can be stored in elastic
    product_interest = ",".join(product_interest_list)
    brand_interest = ",".join(brand_interest_list)

    # Add all this info to elastic cluster.
    add_data_es(client_mac, client_ip, user_email, user_age, user_gender, product_interest, brand_interest)

    return redirect("{}?continue_url={}".format(success_url,base_grant_url), code=302)


@app.route("/success",methods=["GET"])
def get_success():
    """
        After successful log-in, redirect user to link based on their interest list.
    """
    global user_continue_url
    global advert_link

    print(advert_link)
    return render_template("success.html",user_continue_url=advert_link)


@app.after_request
def add_header(response):
    response.cache_control.max_age = 300
    return response


def add_data_es(client_mac, client_ip, user_email, user_age, user_gender, product_interest, brand_interest):
    """
        Adds data to elasticdatabase
    """

    es_conn = es_handler.connect_elasticsearch(es_handler.HOST_URL)

    # get current time and date making sure if follows the correct format.
    now = datetime.now()
    current_date = now.strftime("%Y-%m-%dT%H:%MZ")

    # Identify the keys and correponding values.
    keys = ["date", "client_mac", "client_ip", "user_email", "user_age", "user_gender", "product_interest", "brand_interest"]
    data = [current_date, client_mac, client_ip, user_email, int(user_age), user_gender, product_interest, brand_interest]

    # Create body for elastic request.
    es_values = es_handler.create_body(keys, data)

    # Add this info into elastic index
    es_response = es_handler.add_document(es_conn, INDEX_NAME, None, None, es_values)
    print(es_response)


def get_advert_link(user_age, user_gender, product_interest_list, brand_interest_list):
    """ Returns the link to verizon website based on arguments provided.

        This is used for demo prupose only.
        Verizon website was used as an example of service provider.

        Algorithm presented here is not intuative at all (very much hard-coded, based on assumptions).
        More intuative data mining model should be implemented instead of this for more accurate
        recommendations on the advert link.

        In a nutshell, this section will look at user interets and return link to Verizon website search.
        Some special intrests (eg. mobile plans or entertainment) are based on age.

    """

    print("Getting Advert...")
    # Define base url (i.e. verizon website)
    base_url = "https://search.verizonwireless.com/"
    search_url = "onesearch/search?q="

    random_brand = ""
    random_product = ""

    # Select random interest from both product and brand
    if product_interest_list != []:
        random_product = random.choice(product_interest_list)
    if brand_interest_list != []:
        random_brand = random.choice(brand_interest_list)

    # If product is internet redirect to one link
    if random_product == "internet":
        return("https://www.verizon.com/home/fios-fastest-internet/")
    # If product is mobile plan for people older than 30 redirect to family bundle.
    # If younger redirect to single plan. (based on assumption that older people are more likely to have family)
    elif random_product == "mobile_plan":
        if(user_age > 30):
            return("{}plans/#shared".format(base_url))
        else:
            return("{}plans/single-device-plan/".format(base_url))
    # Same applies for entertainment, which is also based on age (i.e. family or single plan)
    elif random_product == "entertainment":
        if(user_age > 30):
            return("https://www.verizon.com/home/fiostv/")
        else:
            return("https://tv.verizon.com/watch/pay-per-view/")
    # For accessories redirect everyone to same link
    elif random_product == "acessories":
        return("{}/products/sale/".format(base_url))
    # Otherwise combine product and brand interest and add to search url for verizon website.
    elif random_brand or random_product:
        return("{}{}{}+{}".format(base_url, search_url, random_product, random_brand))
    else:
        return "https://www.verizonwireless.com/deals/"


if __name__ == "__main__":
    # Hosted on localhost port 5004 - Remember to run "ngrok http 5004"
    app.run(host="0.0.0.0", port=5004, debug=False)

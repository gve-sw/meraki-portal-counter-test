# Meraki Portal Counter

This is a software project designed for a retail customer using Meraki. Project is designed to showcase Meraki API capabilities and is based on assumptions. Please refer to detailed "User Guide.pdf" documentation provided in this repo.

Take a look to this video for demo purposes: https://youtu.be/64Xe4bYLc90

### High Level Design

The code will recreate the following scenario: 


![Image of HLD](Meraki_Counter_HLD.png)

### Purpose of the project
* Use Meraki camera to count how many people are in the store.
* Use Meraki AP scanning API to detect how many devices are present it the store.
* Design Meraki AP Captive Portal to capture user interests and redirect them to promotion websites.
* Display all this information so business owner so they can see how many users are in the store, how many devices are there in the store and how many people are logging to WiFi. They owner can use this information to see how can they encourage more customers to use caprive portal so they can capture their interest and send them related promotions.

## Software dependencies
* Python 3
* Elasticsearch
* Kibana
* ngrok
* Meraki AP and Meraki Camera

## Setup
* You would need to install all software dependencies listed above
* Setup ngrok
  * [Install ngrok](https://ngrok.com/download)
  * Replace ```$HOME/.ngrok2/ngrok.yml``` with *ngrok.yml* file from this repo.
  * This will allow you to automatically run 4 tunnels you need for the main applications.
  * Note, you will need to register for ngrok if you want to run multiple tunnels. Don't worry, it's free.
  * You should get one ngrok URL for every python script based on the port that script uses. More on this in Description section.
* Install Elasticsearch
  * [On MAC and Linux](https://www.elastic.co/guide/en/elasticsearch/reference/current/targz.html)
  * [On Windows](https://www.elastic.co/guide/en/elasticsearch/reference/current/zip-windows.html)
* Install Kibana
  * [On Mac and Linux](https://www.elastic.co/guide/en/kibana/current/targz.html)
  * [On Windows](https://www.elastic.co/guide/en/kibana/current/windows.html)
* [Install Python](https://www.python.org/downloads/)
  * 3.x is required
* Install python dependencies
  * Open terminal in root directory of this folder and run following commands.
  * Ensuring you have *requirements.txt* file, run : ```pip3 install -r requirements.txt ```
* Once you have your ngrok URLs you would need to add these to Meraki Dashboard. __For these remaining steps, I would recommend you look at "User Guide.pdf" documentation provided in this repo. It is more comperhensive walkthough with nice pictures__
* You need to get Meraki camera API key and Camera serial number and change the following values in *config.py* file:
  * MERAKI_API_KEY
  * CAMERA_SERIAL
* You need to do similar for location scanning part, for which you need to obtain API Key and "secret" phrase, and update the following values in *config.py* file:
  * VALIDATOR
  * SECRET


## Structure
  * __camera_count_v2.py__
    * Used for capturing how many people enter and exit the frame as seen by Meraki camera.
  * __location_scanning_v2.py__
    * Used to detect nearby devices that use wifi.
  * __meraki_captive_portal.py__
    * Used to capture data from splash page and to host UI for splash page.
  * __elastic_handler.py__
    * Contains functions used by other scripts to query and push data to elasticsearch.
  * __config.py__
    * Contains all sensitive information that should not be shared publicly. Things like Meraki API keys, secret key, ngrok URLs, names for elasticsearch indices, etc...
    * You would need to acquire most of this information from your Meraki dashboard or from your ngrok process.
    * This file is part of __git ignore__ so any changes you make to it will not be pushed to main repo. We recommend you do not remove it from ignore file.
  * __elastic_onetime.py__
    * Contains code to create all indices required for this project. You would need to run this only once, when you setup elasticsearch.
  * __ngrok.yml__
    * Config file for ngrok. You should copy this to your ngrok/config folder (usially placed in ```$HOME/.ngrok/```) so you can run multiple tunnels at once.
  * __requirements.txt__
    * Contains all python moudles used by other scripts. To install these modules run ```pip3 install -r requirements.txt```. You would need to run this only once (i.e. when you are setting up project initially).
  * __static__ and __templates__ directories
    * Contain all front end files for Splash Page. Files like html, css, javascript, images, etc...

## Run Code

### Start ngrok tunnel
Assuming you have copied *ngrok.yml* in previously mentioned directory, you can just run:
  ```
  ngrok start -all 
  ```
If you have not, or you wish to test each script separetrly you can run single ngrok tunnel:
  ```
  ngrok http <port_number>
  ```
For example, to run tunnel for elasticsearch only, you would do:
  ```
  ngrok http 9200
  ```
Assuming you have not changed default port elastic is running on (i.e. 9200).

#### Why do we need ngrok?

* Elasticsearch, Kibana, *meraki_captive_portal.py* and *location_scanning_v2.py* run as servers. 
* Both meraki_captive_portal.py and location_scanning_v2.py need ngrok tunnel because we need to provide this URL to Meraki Camera and AP.
* Elasticsearch and Kibana can be run locally.
* In fact all these servers are running locally (i.e. localhost). What ngrok does, it provides public URL (i.e. domain) that points to your localhost:<port>, that Meraki Dashboard can access. 
* By default (and you will see this when you look at the code) these are default localhost ports these applications are using:
  * meraki_captive_portal   : __5004__
  * location_scanning_v2.py : __5000__
  * Elasticsearch           : __9200__
  * Kibana                  : __5601__
  
  * NOTE: All python scripts use ngrok URL when writing data to Elasticsearch. This is placed under variable named __ES_HOST_URL__ in *__config.py__* file, so if you re-run ngrok you would need to change URL or change it to localhost:9200 (if you do not change elastic default port of course).
  * Oh yea, since we are using free version of ngrok, everytime you re-run it, it will give you a different URL, so you need to update Meraki Dashboard and *__config.py__* file.

### Initiate Elasticsearch and Kibana

* In Terminal, navigate to where you extrcted elasticsearch then type:
```
./bin/elasticsearch
```
* If you want to test it manually, wait for a minute or so, then in your browser go to __localhost:9200__ or __respective ngrok URL__ to see if elastic is up and running. You should get json object displayed. Otherwise if you run your python scripts it will tell you if there is an issue with elastic.

* In a separate terminal, navigate where you extracted kibana then type:
```
./bin/kibana
```
* To test and access your data, in your browser go to __localhost:5601__ or __respective ngrok URL__. Kibana UI should pop up. On how to use Kibana interface refer to our "User Guide.pdf" document included in this repo.

* __NOTE__: If you are running this code for the very first time, once you have elastic up and running, run the following python script:
```
pyhton3 elastic_onetime.py
```
  * You only need to run this once (i.e. when you are setting up elasticsearch for the first time). __This scrip will create all relevant indecies for elasticsearch where you can store your data.__
  
* The following is the mapping of which script uses which elasticsearch index:

Python Script | Elasticsearch Index
------------- | -------------------
camera_count_v2.py | __camera_count__
location_scanning_v2.py | __scanning_count__
meraki_captive_portal.py | __splash_count__

When you run the scripts you can start seeing the captive portal splash page and start getting statistics like these examples:

## Captive Portal 

![Image of Captive Portal](https://wwwin-github.cisco.com/jingenie/meraki-portal-counter/blob/master/Meraki_counter-CaptivePortal.png)

## Kibana Insigths

## In store : 


![Image of Kibana in store](https://wwwin-github.cisco.com/jingenie/meraki-portal-counter/blob/master/Meraki_Counter_Kibana_InStore.png)

## Insights from captive portal 


![Image of Kibana splash page](https://wwwin-github.cisco.com/jingenie/meraki-portal-counter/blob/master/Meraki_Counter_SplashPage.png)

## Insights from people moving around the store 


![Image of location scanning](https://wwwin-github.cisco.com/jingenie/meraki-portal-counter/blob/master/Meraki_Counter_Kibana_Location.png)


### Run Python Scripts
There are 3 main functions: camera_count_v2, location_scanning_v2.py and meraki_captive_portal.py.
Run each one in a separate terminal.
  ```
  python3 camera_count_v2.py
  ```
  ```
  python3 location_scanning_v2.py
  ```
  ```
  python3 meraki_captive_portal.py
  ```
  # Testing
  * You should be all up and running now.
  * You can test by using camera and AP (i.e. walk into the frame or camera, and/or connect to wifi)
  * Then you can go to ngrok URL that is pointing to Kibana (i.e. localhost:5601) and you will see all of the collected data.
  * Refer to "User Guide.pdf" documentation provided in this repo for more information on how to use Kibana to display your information. Alternatively, you can see demo video.

### Authors Note
* We did not really had much time to create unit test (sorry...) but you can kinda test some scripts without needing Meraki AP.
* Most scripts are dependent on Meraki AP and Camera in order to test their functionality.
* You can test elasticsearch without requirement for any ngrok. Simply run it locally and change ES_HOST_URL to localhost:9200. Similarly you can do this for Kibana too.
* You can test splash page without need for Meraki hardware.
  * Run ``` python3 meraki_captive_portal.py``` and ```ngrok htto 5004``` (ngtok is optional here)
  * Then copy the following string:
  > <your_server>/click?base_url = "base_grant_url=https%3A%2F%2Fn143.network-auth.com%2Fsplash%2Fgrant&user_continue_url=http%3A%2F%2Fmeraki.com%2F&node_id=XXX1936&node_mac=11:22:33:44:55:b0&gateway_id=XXX1936&client_ip=256.256.256.256&client_mac=44:55:66:77:88:XX
  * Where <your_server> is either localhost:9200 or ngrok URL.
  * You should then be greeted by splash page where you can follow through.
  * Once you submit your response, you will be redirected based on the interests you selected.
  * Either in your terminal or in Kibana (if you are running elastic) you will be able to see information captured from the captive portal.
  


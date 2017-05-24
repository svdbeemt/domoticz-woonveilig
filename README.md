# Domoticz Woonveilig alarmsystem Plugin

This plugin will connect your Woonveilig Gate01 alarmsystem to Domoticz. This plugin was designed for using Domoticz as an addition on controlling the Woonveilig alarmsystem. No modifications to your Woonveilig configuration will be made.

The following Woonveilig accessories are supported:
* Door contacts
* Keypad

Currently IR sensors are not supported.

#Features
After installing the plugin you will be able to:
* Change the state of your alarm (arm, disarm, arm home)
* Door contact swtiches will be added. You can monitor when a door is open/closed and use this information for event based ruling.

#Installation and setup

If you are use a Raspberry Pi to host your Domoticz, you probably need to install libpython3.4 for plugins to work.

sudo apt install libpython3.4
At the moment of writing you also need to install:

sudo apt install python3-dev
sudo apt install python3-pip
sudo apt-get install python3-urllib3
pip install demjson

In your domoticz/plugins directory do:

cd domoticz/plugins
git clone https://github.com/StuffNL/domoticz-woonveilig.git
Alternatively you can download the latest version from https://github.com/StuffNL/domoticz-woonveilig/archive/master.zip and unzip it. Then create a directory on your Domoticz device in domoticz/plugins named Woonvelig and transfer all the files to your device.

Restart your Domoticz service with:

sudo service domoticz.sh restart
Now go to Setup, Hardware in your Domoticz interface. There you add Woonveilig Gate01.

Make sure you enter all the required fields.

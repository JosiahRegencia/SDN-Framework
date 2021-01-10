#!/bin/bash
sudo pkill -f vlc
ryu-manager ryu.app.ofctl_rest ryu.app.rest_qos ryu.app.rest_conf_switch ryu.app.rest_topology controller.py --config-file controller.conf 

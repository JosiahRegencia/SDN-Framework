#!/bin/bash

python3 scripts/custom/network_configs.py
python2 scripts/custom/nodes_config.py
python3 scripts/custom/serialize_qos.py
python3 scripts/custom/node_connections.py
python3 scripts/custom/ifstat_generator.py
sudo pkill -f python3
sudo pkill -f vlc
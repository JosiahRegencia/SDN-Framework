#!/bin/bash
cd
cd server1
pwd > test.log
# iperf3 -s -p 5566 -i 1 &
sudo python3 -m http.server 80 --bind 10.0.1.101 &
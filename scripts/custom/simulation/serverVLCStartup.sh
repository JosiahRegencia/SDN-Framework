#*************************************************************
# Description: Shell Script for Starting Up VLC telnet server process.
# Filename   : serverVLCStartup.sh
# Author     : O. V. Chato
# Execution  : To be called by executeTest.py.
#*************************************************************
#!/bin/bash

cd /home/ubuntu/thesis/SDNQoS/Load_Generation

# iperf3 -s -p 5566 -i 1 &
sudo -u ubuntu nohup sh /home/ubuntu/thesis/SDNQoS/Load_Generation/run-vlc-server.sh &

pwd

(sleep 10; (sudo -u ubuntu nohup echo "Loading Config VLM $1" >> vlcstart.log; sudo -u ubuntu nohup python /home/ubuntu/thesis/SDNQoS/Load_Generation/telnetStartVLCServer.py $1)) & # ; 

exit 0
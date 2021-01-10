#*************************************************************
# Description: Python Program for initiating test execution.
# Filename   : executeTest.py
# Author     : O. V. Chato
# Execution  : To be run mininet interpreter command prompt.
#*************************************************************
#!/usr/bin/python

# from mininet.log import lg, info
# from mininet.net import Mininet
# import ConfigSetup
import time
import os.path, os, sys
import pwd
import logging
import grp
from datetime import date, datetime, timedelta
import csv
import yaml
import pickle

logging.basicConfig(level=logging.DEBUG,
                    filename='execute.log', 
                    filemode='w',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S')

logging.info("\n\n")

print ("Executing...")
# Global Variables
hosts = net.hosts
datetimestr = time.strftime("%m%d%Y%H%M%S")
usecase = "0"
loadcase = 3
queuecase = "1.0"
secondstorun = 300
startingvlcport = 4313

BASEDIR = os.getcwd() # path.dirname() # abspath(os.pardir)
print ('BASEDIR ', BASEDIR)
for s in sys.path:
    print (s)
print "\n\n"

usecase_yml = "{}/config/class_profile_functionname.yml".format(BASEDIR)
print (usecase_yml)

with open(usecase_yml, 'rb') as yml_file:
    usecases = yaml.load(yml_file)['class_profiles']

# Get Class Profile to be tested via interactive prompt.
cl_input_cp = raw_input("Please enter a Class Profile Use Case Code: ") 

if cl_input_cp.strip() in usecases:
    usecase =  cl_input_cp.strip()
    
    print("Class Profile is %s (Load Configuration is %s, QoS Configuration is %s)." % (usecase, loadcase, queuecase))

    config_pkl = "{}/pkl/algo/usecase_{}_exec.pkl".format(BASEDIR, usecase)
    print ('config_pkl: ', config_pkl)
    # pkl = f"{OUTDIR}/usecase_{config_data['usecase']}_nodes_configuration.pkl"

    with open(config_pkl, 'rb') as pkl_file:
       # print "Importing node_classes"
        # from node_classes import Host, Switch
        print "loading data"
        config_data = pickle.load(pkl_file)
        print (config_data)

    execdir = "{}/scripts/custom".format(BASEDIR)
    resdir = os.path.dirname("{}/test.results/{}-case{}".format(BASEDIR, datetimestr, usecase))
    specdir = "{}-case{}".format(datetimestr, usecase)
    resdir = os.path.join(resdir, specdir)
    logsdir = "%s/logs" % (resdir)
    newlinechar ="\r\n"

    print ("resdir: ", resdir)
    print ("Logsdir: {}\n\n".format(logsdir))
    
    try:
        # pass
        # Create directory for raw results.
        mnuid = pwd.getpwnam("ubuntu").pw_uid
        print ("mnuid: {}".format(mnuid) )
        mngid = grp.getgrnam("ubuntu").gr_gid
        print ("mngid: {}".format(mngid))
        original_umask = os.umask(0)
        if not os.path.exists(resdir):
            print ("not exists 1")
            os.mkdir(resdir, 0o775)
            os.chown(resdir, mnuid, mngid)
        if not os.path.exists(logsdir):
            print ("not exists 2")
            os.mkdir(logsdir, 0o775)
            os.chown(logsdir, mnuid, mngid)
        os.umask(original_umask)
        
    except:
        print('Error Creating Directories' % (resdir))
    else:
        # ApacheBench results file initialization.
        abaggregatefile = "%s/test.results/ab-aggregated-run-results-%s-%s-%s.csv" % (BASEDIR, usecase, loadcase, queuecase)
        print ("abaggregatefile: {}\n".format(abaggregatefile))
        if not os.path.isfile(abaggregatefile):
            abdata = "Use Case\tLoad Configuration\tQueue Configuration\tRequest Type\tRun Date\tClient Name\tTransfer Rate(Kbps)\tTotal Time\tCompleted Requests\tFailed Requests\tTotal Transferred\tHTML Transferred\tRequests/Second\tTime/Request\tMean Time/Request%s" % (newlinechar)
            targetad = open(abaggregatefile, 'a')
            targetad.write(abdata)
            targetad.close()
            # os.chown(abaggregatefile, mnuid, mngid)

        # Get an ordered list of hosts from client load configuration file per switch in switch mapping.
        orderedHosts = {}
        switchIds = []
        for csEntry in config_data['client_switch_map']:
            switchId = config_data['client_switch_map'][csEntry][0]
            if switchId not in switchIds:
                switchIds.append(switchId)
            if switchId not in orderedHosts:
                orderedHosts[switchId] = []
            orderedHosts[switchId].append(csEntry)
        
        # Get/formulate host distribution list.
        hostDistributionList = []
        emptyLists = 0
        currentElementNumber = 0
        while emptyLists < len(orderedHosts):
            for switchId in orderedHosts:
                if len(orderedHosts[switchId]) > 0:
                    clientName = orderedHosts[switchId][0]
                    for host in hosts:
                        hostname = host.name
                        if hostname.strip() == clientName.strip():
                            hostDistributionList.append(host)
                            break
                    del orderedHosts[switchId][0]
                else:
                    emptyLists = emptyLists + 1
        
        print ("Host distribution list: ", hostDistributionList)
        # Get number of clients and start server processes on each server.
        cl_cnt = 0
        for host in hosts:
            hostname = host.name
            if hostname.startswith("client"):
                cl_cnt = cl_cnt + 1
            elif hostname == ("server1"):
                # sudo -u ubuntu nohup sh {}/scripts/custom/simulation/server1HTTPStartup.sh
                print('Starting up HTTP Server: {}'.format(host))
                logging.info(host.cmd('sudo -u ubuntu nohup sh {}/scripts/custom/simulation/server1HTTPStartup.sh &'.format(BASEDIR)))
            elif hostname == ("server2"):
                print('Starting up VLC Server: {}'.format(host))
                logging.info(host.cmd('sudo -u ubuntu nohup sh {}/scripts/custom/simulation/serverVLCStartup.sh BBB &'.format(BASEDIR)))
            elif hostname == ("server3"):
                print('Starting up HTTP Server: {}'.format(host))
                logging.info(host.cmd('sudo -u ubuntu nohup sh {}/scripts/custom/simulation/server3HTTPStartup.sh &'.format(BASEDIR)))
            elif hostname == ("server4"):
                print('Starting up VLC Server: {}'.format(host))
                logging.info(host.cmd('sudo -u ubuntu nohup sh {}/scripts/custom/simulation/serverVLCStartup.sh Purl &'.format(BASEDIR)))
            elif hostname == ("server5"):
                print('Starting up HTTP Server: {}'.format(host))
                logging.info(host.cmd('sudo -u ubuntu nohup sh {}/scripts/custom/simulation/server5HTTPStartup.sh &'.format(BASEDIR)))
            elif hostname == ("server6"):
                print('Starting up VLC Server: {}'.format(host))
                logging.info(host.cmd('sudo -u ubuntu nohup sh {}/scripts/custom/simulation/serverVLCStartup.sh Spring &'.format(BASEDIR)))
                time.sleep(10)
          
        # Run VLC software telnet server processes on each client host.
        print ("datetime: {}\tusecase: {}\tvlcport: {}".format(datetimestr, usecase, startingvlcport))
        print('Running VLC Clients')
        for host in hostDistributionList:
            hostname = host.name
            if hostname.startswith("client"):
                if hostname in config_data['load_config']:
                    currentvlcport = startingvlcport
                    for x in range(0, config_data['load_config'][hostname].count("vod-low-1")):
                        # logging.info(host.cmd('sudo -u ubuntu nohup sh {}/scripts/custom/simulation/run-client-vlc-tests.sh %s medium %s %s %s' % (hostname, datetimestr, usecase, currentvlcport)))
                        logging.info(host.cmd('sudo -u ubuntu nohup sh %s/scripts/custom/simulation/run-vlc-client-server2-medium.sh %s %s %s %s &' % (BASEDIR, currentvlcport, hostname, datetimestr, usecase)))
                        currentvlcport = currentvlcport + 1
      
                    for y in range(0, config_data['load_config'][hostname].count("vod-high-1")):
                        # logging.info(host.cmd('sudo -u ubuntu nohup sh {}/scripts/custom/simulation/run-client-vlc-tests.sh %s high %s %s %s' % (hostname, datetimestr, usecase, currentvlcport)))
                        logging.info(host.cmd('sudo -u ubuntu nohup sh %s/scripts/custom/simulation/run-vlc-client-server2-high.sh %s %s %s %s &' % (BASEDIR, currentvlcport, hostname, datetimestr, usecase)))
                        currentvlcport = currentvlcport + 1

                    for x in range(0, config_data['load_config'][hostname].count("vod-low-2")):
                        # logging.info(host.cmd('sudo -u ubuntu nohup sh {}/scripts/custom/simulation/run-client-vlc-tests.sh %s medium %s %s %s' % (hostname, datetimestr, usecase, currentvlcport)))
                        logging.info(host.cmd('sudo -u ubuntu nohup sh %s/scripts/custom/simulation/run-vlc-client-server4-medium.sh %s %s %s %s &' % (BASEDIR, currentvlcport, hostname, datetimestr, usecase)))
                        currentvlcport = currentvlcport + 1
      
                    for y in range(0, config_data['load_config'][hostname].count("vod-high-2")):
                        # logging.info(host.cmd('sudo -u ubuntu nohup sh {}/scripts/custom/simulation/run-client-vlc-tests.sh %s high %s %s %s' % (hostname, datetimestr, usecase, currentvlcport)))
                        logging.info(host.cmd('sudo -u ubuntu nohup sh %s/scripts/custom/simulation/run-vlc-client-server4-high.sh %s %s %s %s &' % (BASEDIR, currentvlcport, hostname, datetimestr, usecase)))
                        currentvlcport = currentvlcport + 1

                    for x in range(0, config_data['load_config'][hostname].count("vod-low-3")):
                        # logging.info(host.cmd('sudo -u ubuntu nohup sh {}/scripts/custom/simulation/run-client-vlc-tests.sh %s medium %s %s %s' % (hostname, datetimestr, usecase, currentvlcport)))
                        logging.info(host.cmd('sudo -u ubuntu nohup sh %s/scripts/custom/simulation/run-vlc-client-server6-medium.sh %s %s %s %s &' % (BASEDIR, currentvlcport, hostname, datetimestr, usecase)))
                        currentvlcport = currentvlcport + 1
      
                    for y in range(0, config_data['load_config'][hostname].count("vod-high-3")):
                        # logging.info(host.cmd('sudo -u ubuntu nohup sh {}/scripts/custom/simulation/run-client-vlc-tests.sh %s high %s %s %s' % (hostname, datetimestr, usecase, currentvlcport)))
                        logging.info(host.cmd('sudo -u ubuntu nohup sh %s/scripts/custom/simulation/run-vlc-client-server6-high.sh %s %s %s %s &' % (BASEDIR, currentvlcport, hostname, datetimestr, usecase)))
                        currentvlcport = currentvlcport + 1
      
        # Run ifstat and ping. Ping and ifstat will do queries every second for the 5-minute duration.
        ipstatduration = secondstorun + 90
      
        print('Running ipstat')
        os.system("sudo -u ubuntu nohup sh %s/scripts/custom/simulation/run-ipstat.sh %s %s %s %s &" %(BASEDIR, usecase, queuecase, loadcase, ipstatduration))
        print('Running ping')
        pingduration = ipstatduration + 30
        print ("Ping Duration: {}".format(pingduration))
        for host in hosts:
            hostname = host.name
            if hostname.startswith("client"):
                info(host.cmd('sudo -u ubuntu nohup ping -i 1 -W 1 -w %s 10.0.1.101 > %s/test.results/%s-case%s/ping-results-%s-10.0.1.101.log &' % (BASEDIR, pingduration, datetimestr, usecase, hostname)))
                info(host.cmd('sudo -u ubuntu nohup ping -i 1 -W 1 -w %s 10.0.1.102 > %s/test.results/%s-case%s/ping-results-%s-10.0.1.102.log &' % (BASEDIR, pingduration, datetimestr, usecase, hostname)))
                info(host.cmd('sudo -u ubuntu nohup ping -i 1 -W 1 -w %s 10.0.1.103 > %s/test.results/%s-case%s/ping-results-%s-10.0.1.103.log &' % (BASEDIR, pingduration, datetimestr, usecase, hostname)))
                info(host.cmd('sudo -u ubuntu nohup ping -i 1 -W 1 -w %s 10.0.1.104 > %s/test.results/%s-case%s/ping-results-%s-10.0.1.104.log &' % (BASEDIR, pingduration, datetimestr, usecase, hostname)))
                info(host.cmd('sudo -u ubuntu nohup ping -i 1 -W 1 -w %s 10.0.1.105 > %s/test.results/%s-case%s/ping-results-%s-10.0.1.105.log &' % (BASEDIR, pingduration, datetimestr, usecase, hostname)))
                info(host.cmd('sudo -u ubuntu nohup ping -i 1 -W 1 -w %s 10.0.1.106 > %s/test.results/%s-case%s/ping-results-%s-10.0.1.106.log &' % (BASEDIR, pingduration, datetimestr, usecase, hostname)))

        time.sleep(30)
        starttime = datetime.now()
        endtime = starttime + timedelta(seconds=secondstorun)
          
        print((starttime.strftime("%m%d%Y%H%M%S")))
        print((endtime.strftime("%m%d%Y%H%M%S")))
          
        # Run ApacheBench clients for each client host.
        print('Running Client AB')
        for host in hostDistributionList:
            hostname = host.name
            if hostname.startswith("client"):
                if hostname in config_data['load_config']:
                    for x in range(0, config_data['load_config'][hostname].count("http-low-1")):
                        print ("\n\nhttp-low-1\tHost: {}".format(hostname))
                        aboutputdir = "{}/test.results/%s-case%s" % (datetimestr, usecase)
                        aboutputfile = "ab-results-%s-med-outfile.txt" % hostname
                        difference = int((endtime - datetime.now()).total_seconds())
                        info(host.cmd('sudo -u ubuntu nohup sh %s/scripts/custom/simulation/ab_tests-server1-med.sh %s %s %s %s %s %s %s %s %s &' % (BASEDIR, difference, aboutputfile, execdir, hostname, datetimestr, usecase, aboutputdir, queuecase, loadcase)))
                        print('ab-low: %s %s' % (hostname, datetimestr))

                    for y in range(0, config_data['load_config'][hostname].count("http-high-1")):
                        print ("\n\nhttp-high-1\tHost: {}".format(hostname))
                        aboutputdir = "{}/test.results/%s-case%s" % (datetimestr, usecase)
                        aboutputfile = "ab-results-%s-high-outfile.txt" % hostname
                        difference = int((endtime - datetime.now()).total_seconds())
                        info(host.cmd('sudo -u ubuntu nohup sh %s/scripts/custom/simulation/ab_tests-server1-med.sh %s %s %s %s %s %s %s %s %s &' % (BASEDIR, difference, aboutputfile, execdir, hostname, datetimestr, usecase, aboutputdir, queuecase, loadcase)))
                        print('ab-high: %s %s' % (hostname, datetimestr))    

                    for x in range(0, config_data['load_config'][hostname].count("http-low-2")):
                        print ("\n\nhttp-low-2\tHost: {}".format(hostname))
                        aboutputdir = "{}/test.results/%s-case%s" % (datetimestr, usecase)
                        aboutputfile = "ab-results-%s-med-outfile.txt" % hostname
                        difference = int((endtime - datetime.now()).total_seconds())
                        info(host.cmd('sudo -u ubuntu nohup sh %s/scripts/custom/simulation/ab_tests-server3-med.sh %s %s %s %s %s %s %s %s %s &' % (BASEDIR, difference, aboutputfile, execdir, hostname, datetimestr, usecase, aboutputdir, queuecase, loadcase)))
                        print('ab-low: %s %s' % (hostname, datetimestr))

                    for y in range(0, config_data['load_config'][hostname].count("http-high-2")):
                        print ("\n\nhttp-high-2\tHost: {}".format(hostname))
                        aboutputdir = "{}/test.results/%s-case%s" % (datetimestr, usecase)
                        aboutputfile = "ab-results-%s-high-outfile.txt" % hostname
                        difference = int((endtime - datetime.now()).total_seconds())
                        info(host.cmd('sudo -u ubuntu nohup sh %s/scripts/custom/simulation/ab_tests-server3-med.sh %s %s %s %s %s %s %s %s %s &' % (BASEDIR, difference, aboutputfile, execdir, hostname, datetimestr, usecase, aboutputdir, queuecase, loadcase)))
                        print('ab-high: %s %s' % (hostname, datetimestr))  

                    for x in range(0, config_data['load_config'][hostname].count("http-low-3")):
                        print ("\n\nhttp-low-3\tHost: {}".format(hostname))
                        aboutputdir = "{}/test.results/%s-case%s" % (datetimestr, usecase)
                        aboutputfile = "ab-results-%s-med-outfile.txt" % hostname
                        difference = int((endtime - datetime.now()).total_seconds())
                        info(host.cmd('sudo -u ubuntu nohup sh %s/scripts/custom/simulation/ab_tests-server5-med.sh %s %s %s %s %s %s %s %s %s &' % (BASEDIR, difference, aboutputfile, execdir, hostname, datetimestr, usecase, aboutputdir, queuecase, loadcase)))
                        print('ab-low: %s %s' % (hostname, datetimestr))

                    for y in range(0, config_data['load_config'][hostname].count("http-high-3")):
                        print ("\n\nhttp-high-3\tHost: {}".format(hostname))
                        aboutputdir = "{}/test.results/%s-case%s" % (datetimestr, usecase)
                        aboutputfile = "ab-results-%s-high-outfile.txt" % hostname
                        difference = int((endtime - datetime.now()).total_seconds())
                        info(host.cmd('sudo -u ubuntu nohup sh %s/scripts/custom/simulation/ab_tests-server5-med.sh %s %s %s %s %s %s %s %s %s &' % (BASEDIR, difference, aboutputfile, execdir, hostname, datetimestr, usecase, aboutputdir, queuecase, loadcase)))
                        print('ab-high: %s %s' % (hostname, datetimestr))  
          

        # Run VLC telnet clients for each client host.
        print('Running Client Telnets')
        for host in hostDistributionList:
            hostname = host.name
            if hostname.startswith("client"):
                if hostname in config_data['load_config']:
                    currentvlcport = startingvlcport
                    for x in range(0, config_data['load_config'][hostname].count("vod-low-1")):
                        logging.info(host.cmd('sudo -u ubuntu nohup sh %s/scripts/custom/simulation/run-client-vlc-telnet-tests.sh %s medium %s %s %s %s %s %s server2 &' % (BASEDIR, hostname, datetimestr, usecase, endtime.strftime("%m%d%Y%H%M%S"), currentvlcport, queuecase, loadcase)))
                        print('vlc-low: %s %s' % (hostname, datetimestr))
                        currentvlcport = currentvlcport + 1
      
                    for y in range(0, config_data['load_config'][hostname].count("vod-high-1")):
                        logging.info(host.cmd('sudo -u ubuntu nohup sh %s/scripts/custom/simulation/run-client-vlc-telnet-tests.sh %s high %s %s %s %s %s %s server2 &' % (BASEDIR, hostname, datetimestr, usecase, endtime.strftime("%m%d%Y%H%M%S"), currentvlcport, queuecase, loadcase)))
                        print('vlc-high: %s %s' % (hostname, datetimestr))
                        currentvlcport = currentvlcport + 1

                    for x in range(0, config_data['load_config'][hostname].count("vod-low-2")):
                        logging.info(host.cmd('sudo -u ubuntu nohup sh %s/scripts/custom/simulation/run-client-vlc-telnet-tests.sh %s medium %s %s %s %s %s %s server4 &' % (BASEDIR, hostname, datetimestr, usecase, endtime.strftime("%m%d%Y%H%M%S"), currentvlcport, queuecase, loadcase)))
                        print('vlc-low: %s %s' % (hostname, datetimestr))
                        currentvlcport = currentvlcport + 1
      
                    for y in range(0, config_data['load_config'][hostname].count("vod-high-2")):
                        logging.info(host.cmd('sudo -u ubuntu nohup sh %s/scripts/custom/simulation/run-client-vlc-telnet-tests.sh %s high %s %s %s %s %s %s server4 &' % (BASEDIR, hostname, datetimestr, usecase, endtime.strftime("%m%d%Y%H%M%S"), currentvlcport, queuecase, loadcase)))
                        print('vlc-high: %s %s' % (hostname, datetimestr))
                        currentvlcport = currentvlcport + 1

                    for x in range(0, config_data['load_config'][hostname].count("vod-low-3")):
                        logging.info(host.cmd('sudo -u ubuntu nohup sh %s/scripts/custom/simulation/run-client-vlc-telnet-tests.sh %s medium %s %s %s %s %s %s server6 &' % (BASEDIR, hostname, datetimestr, usecase, endtime.strftime("%m%d%Y%H%M%S"), currentvlcport, queuecase, loadcase)))
                        print('vlc-low: %s %s' % (hostname, datetimestr))
                        currentvlcport = currentvlcport + 1
      
                    for y in range(0, config_data['load_config'][hostname].count("vod-high-3")):
                        logging.info(host.cmd('sudo -u ubuntu nohup sh %s/scripts/custom/simulation/run-client-vlc-telnet-tests.sh %s high %s %s %s %s %s %s server6 &' % (BASEDIR, hostname, datetimestr, usecase, endtime.strftime("%m%d%Y%H%M%S"), currentvlcport, queuecase, loadcase)))
                        print('vlc-high: %s %s' % (hostname, datetimestr))
                        currentvlcport = currentvlcport + 1

else:
    print("Class Profile invalid. Please refer to:")
    for case in usecases:
        print usecases[case]



        
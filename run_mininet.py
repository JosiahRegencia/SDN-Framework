from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel, info

from scripts import network_topologies

import yaml
import os, sys
import math
import pickle

sys.modules['network_topologies'] = network_topologies
BASEDIR = os.getcwd()
TOPOYML = "{}/config/simulate_topo.yml".format(BASEDIR)

def create_network():

    net = Mininet (controller=RemoteController)

    info('*** Adding controller\n')
    net.addController('c0', controller=RemoteController)

    with open(TOPOYML, 'rb') as yml_file:
        print "\n\n{}\n\n".format(TOPOYML)
        topo = yaml.load(yml_file, Loader=yaml.FullLoader)

    print topo

    key, value = topo['topology'].items()[0] # Python2
    # [[key,value]] = topo['topology'].items()  # Python3
    print key
    topo_pkl = "{}/pkl/topo/topo_{}.pkl".format(BASEDIR, key)
    print topo_pkl

    with open(topo_pkl, 'rb') as func_pkl:
        func_topo = pickle.load(func_pkl)

    func_topo(net, value)

    info ('*** Starting network\n')
    net.start()

    info('*** Running CLI\n')
    CLI(net)

    info('*** Stopping network')
    net.stop()

if __name__ == '__main__':
    setLogLevel ('info')
    create_network()





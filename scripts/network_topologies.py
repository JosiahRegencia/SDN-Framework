"""
    JETR
"""

import pickle
import yaml
import os

BASEDIR = os.getcwd()

def fat_tree(net, topo):

    def divider(clients, leaves):
        divs = int(float(clients)/float(leaves))
        rng = 0
        rng_list = []
        for i in range(1, leaves):
            rng = rng + divs
            if rng <= clients:
                rng_list.append(rng)

        if len(rng_list) < leaves:
            for i in range(0, leaves-len(rng_list)):
                if (rng_list[len(rng_list)-1] + divs) <= clients:
                    rng_list.append(rng_list[len(rng_list)-1] + divs)

        if rng_list[len(rng_list)-1] < clients:
            diff = clients - rng_list[len(rng_list)-1]
            start = len(rng_list) - diff
            rng_list[len(rng_list)-1] = clients
            for i in range(start, len(rng_list)-1):
                rng_list[i] = rng_list[i-1] + (divs + 1)

        return rng_list

    def switch_layers(layers, layer_1, switches):
        fat_tree = {}
        keys = list(switches.keys())
        switches_count = layer_1

        for i in range(1, layers+1):
            layer_switches = []
            for j in range(0, int(switches_count)):
                switch_num = keys.pop(0)
                layer_switches.append(switches[switch_num])
            fat_tree[i] = layer_switches
            switches_count = switches_count / 2

        return fat_tree

    ceil = topo['clients']
    layers = topo['leaf_switch_layers']
    total_switches = 2 ** (layers+1)
    leaf_switches_cnt = 2 ** layers
    ranges = divider (ceil, leaf_switches_cnt)
    index = 0

    # Add hosts and switches
    clients = {}
    for x in range(1, ceil+1):
        clients[x] = net.addHost('client%s' % x)
    server1 = net.addHost( 'server1', ip="10.0.1.101" ) # inNamespace=False
    server2 = net.addHost( 'server2', ip="10.0.1.102" ) 
    server3 = net.addHost( 'server3', ip="10.0.1.103" ) 
    server4 = net.addHost( 'server4', ip="10.0.1.104" ) 
    server5 = net.addHost( 'server5', ip="10.0.1.105" ) 
    server6 = net.addHost( 'server6', ip="10.0.1.106" )

    switches = {}
    for i in range(1, (total_switches+1)):
        # implement similar to clients
        switches[i] = net.addSwitch('switch%s' % i)

    # Add Links for First Layers
    for i in  range (1, ceil+1):
        if i <= ranges[index]:
            net.addLink( clients[i], switches[index+1])
        else:
            index = index + 1
            net.addLink( clients[i], switches[index+1])
    
    fat_tree = switch_layers(layers, leaf_switches_cnt, switches)
    print (fat_tree)
    core_switch = switches[(int(fat_tree[layers][1].name.split('switch')[1])+1)]
    server_switch = switches[(int(fat_tree[layers][1].name.split('h')[1])+2)]

    for i in range(1, layers):
        ranges = divider(len(fat_tree[i]), len(fat_tree[i+1]))
        ranges.append(len(fat_tree[i])) # check this
        index = 0
        layer_min = int(fat_tree[i][0].name.split('h')[1])
        layer_max = int(fat_tree[i][len(fat_tree[i])-1].name.split('h')[1])

        for j in range(0, len(fat_tree[i])):
            if j < ranges[index]:
                net.addLink(switches[int(fat_tree[i][j].name.split('h')[1])], switches[int(fat_tree[i+1][index].name.split('h')[1])])
            else:
                index = index + 1
                net.addLink(switches[int(fat_tree[i][j].name.split('h')[1])], switches[int(fat_tree[i+1][index].name.split('h')[1])])

    # Add Link to Core Switch
    for switch in fat_tree[layers]:
        net.addLink(switch, core_switch)

    # Link Core Switch to Server Switch
    net.addLink(core_switch, server_switch)
    net.addLink( server_switch, server1 )
    net.addLink( server_switch, server2 )
    net.addLink( server_switch, server3 )
    net.addLink( server_switch, server4 )
    net.addLink( server_switch, server5 )
    net.addLink( server_switch, server6 )

def twoway_linear(net, topo):
    left_host = net.addHost('LeftHost')
    right_host = net.addHost('RightHost')

    left_switch = net.addSwitch('src1')
    right_switch = net.addSwitch('dst2')

    core_switch = net.addSwitch('cs3')

    net.addLink(left_host, left_switch)
    net.addLink(right_host, right_switch)
    net.addLink(left_switch, right_switch)












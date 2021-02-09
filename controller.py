# JETR

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.controller import dpset
from ryu.topology.event import EventSwitchEnter, EventSwitchLeave
from ryu.topology.api import get_switch, get_link, get_all_switch, get_host
from ryu.topology import event, switches
from ryu.ofproto import ofproto_v1_3, ofproto_v1_5
from ryu.ofproto.ofproto_v1_3_parser import OFPFlowMod, OFPFlowStatsRequest
from ryu.lib.packet import ethernet, packet, arp, ipv4, tcp, udp, ether_types, ipv6
from ryu.app.ofctl import api
from ryu.app import ofctl_rest
from ryu.lib import hub
from ryu import cfg

from threading import Event
from node_classes import Host, Switch
from scripts import qos_test_cases
from operator import attrgetter

import logging, time, sys, csv, operator, os
import pickle, yaml, json, requests, datetime, logging, pprint

sys.modules['qos_test_cases'] = qos_test_cases
log = logging.getLogger('TESTER')
arp_count = 0

BASEDIR = os.getcwd()


class MySwitch(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self,  *args, **kwargs):
        super(MySwitch, self).__init__(*args, **kwargs)
        self.name = "JETR"
        self.topology_api_app = self
        
        CONF = cfg.CONF
        CONF.register_opts([
            cfg.StrOpt('case', default="0")])
        
        self.case = CONF.case.replace("\"", "")

        self.nodes_config_file = f"{BASEDIR}/config/custom/usecase_{self.case}_nodes_configuration.json"
        self.usecase_yml = f"{BASEDIR}/config/class_profile_functionname.yml"
        self.topo_yml = f"{BASEDIR}/config/simulate_topo.yml"
        self.nodescon_yml = f"{BASEDIR}/pkl/net_data/node_connections.pkl"

        with open(self.topo_yml, "rb") as yml_file:
            self.topo = yaml.load(yml_file)['topology']['fat_tree']
            self.layers = self.topo['leaf_switch_layers']

        with open(self.nodescon_yml, "rb") as pkl_con:
            self.nodes_connect = pickle.load(pkl_con)
        
        with open(self.nodes_config_file, "rb") as pkl_config:
            self.nodes_config = json.load(pkl_config)
            print (f"\n\n\nNODES CONFIG:\n{self.nodes_config}\n\n\n")

        with open(self.usecase_yml, 'rb') as yml_file:
            self.usecases = yaml.load(yml_file)['class_profiles'] # , Loader=yaml.FullLoader
        
        if self.case == self.usecases:
            log.info(self.usecases[self.use_case]['description'])

        self.usecase_func_pkl = f"{BASEDIR}/pkl/algo/usecase_{self.case}_{self.usecases[self.case]['func_name']}_qosprotocol.pkl"

        with open(self.usecase_func_pkl, 'rb') as func_pkl:
            self.qos_func = pickle.load(func_pkl)

        for key in self.nodes_config:
            print(f"Key: {key}\n{self.nodes_config[key]}\n\n")

    @set_ev_cls(event.EventSwitchEnter)
    def get_topology_data(self, ev):
        switch_list = get_switch(self.topology_api_app, None)
        switches=[switch.dp.id for switch in switch_list]
        links_list = get_link(self.topology_api_app, None)
        links=[(link.src.dpid,link.dst.dpid,{'port':link.src.port_no}) for link in links_list]
        print (f"Links List: {links_list}\n")
        print (f"Links: {links}\n")

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler (self, ev):
        dp = ev.msg.datapath
        ofp = dp.ofproto
        ofp_parser = dp.ofproto_parser

        print (f"Switch Events Handler. Datapath: {type(dp)}")

        match = ofp_parser.OFPMatch()
        actions = [ofp_parser.OFPActionOutput(ofp.OFPP_CONTROLLER, ofp.OFPCML_NO_BUFFER)]

        self.add_flow (dp, 0, match, actions)

    def add_flow (self, dp, priority, match, actions, buffer_id=None):
        ofp = dp.ofproto
        ofp_parser = dp.ofproto_parser

        inst = [ofp_parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions)]

        if buffer_id:
            mod = ofp_parser.OFPFlowMod(datapath=dp, buffer_id=buffer_id, priority=priority,
                                        match=match, instructions=inst, table_id=1)
        else:
            mod = ofp_parser.OFPFlowMod(datapath=dp, priority=priority,
                                        match=match, instructions=inst, table_id=1)

        dp.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):

        """
        NOTE TO SELF:
        REFACTOR THIS PART
        AVOID FOR LOOPS AS MUCH AS POSSIBLE
        IF POSSIBLE, CHANGE LISTS TO DICTS
        """
        
        msg = ev.msg
        dp = msg.datapath
        ofp = dp.ofproto
        ofp_parser = dp.ofproto_parser
        in_port = msg.match['in_port']
        pkt = packet.Packet(msg.data)
        ipv4_pkt = pkt.get_protocol(ipv4.ipv4)

        match = ofp_parser.OFPMatch(eth_type=0x0806)
        actions = [ofp_parser.OFPActionOutput(ofp.OFPP_FLOOD)]  # OFPP_ALL
        inst = [ofp_parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions)]
        mod = ofp_parser.OFPFlowMod(datapath=dp, buffer_id=msg.buffer_id, idle_timeout=0, hard_timeout=0,
                                    priority=10, match=match, instructions=inst, table_id=1)
        dp.send_msg(mod)

        match = ofp_parser.OFPMatch(eth_type=0x88CC)
        actions = [ofp_parser.OFPActionOutput(ofp.OFPP_FLOOD)]  # OFPP_ALL
        inst = [ofp_parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions)]
        mod = ofp_parser.OFPFlowMod(datapath=dp, buffer_id=msg.buffer_id, idle_timeout=0, hard_timeout=0,
                                    priority=10, match=match, instructions=inst, table_id=1)
        dp.send_msg(mod)

        # response = requests.get(f"http://localhost:8080/v1.0/topology/switches")
        # # print (response.json()[0])
        # for switch in response.json():
        #     print (f"{switch['ports']}\n")
        # print (f"\n\n")

        # print (f"\n\n{self.nodes_config['switches_list']}\n\n{self.nodes_config['switches_list'][str(dp.id)]}\n\n\n\n")

        if self.nodes_config['switches_list'][str(dp.id)]['type'] == "client-leaf":

            for host_entry in self.nodes_config['switches_list'][str(dp.id)]['hosts_entries']:
                out_port = host_entry['port']
                actions = [ofp_parser.OFPActionOutput(out_port)]
                inst = [ofp_parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions)]
                match = ofp_parser.OFPMatch(in_port=in_port, eth_type=0x0800, ipv4_dst=host_entry['ip'])
                mod = ofp_parser.OFPFlowMod(datapath=dp, buffer_id=msg.buffer_id, priority=10,
                                            match=match, instructions=inst, table_id=1)

                dp.send_msg(mod)

            for client_entry in self.nodes_config['clients_list']:
                if client_entry['switch_id'] != self.nodes_config['switches_list'][str(dp.id)]['id']:
                    out_port = self.nodes_config['switches_list'][str(dp.id)]['core_port']
                    actions = [ofp_parser.OFPActionOutput(out_port)]
                    inst = [ofp_parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions)]
                    match = ofp_parser.OFPMatch(in_port=in_port, eth_type=0x0800, ipv4_dst=client_entry['ip'].strip())
                    mod = ofp_parser.OFPFlowMod(datapath=dp, buffer_id=msg.buffer_id, priority=10,
                                                match=match, instructions=inst, table_id=1)
                    dp.send_msg(mod)

            if self.nodes_config['switches_list'][str(dp.id)]['qos_type'] == 'none':
                for server_entry in self.nodes_config['servers_list']:
                    out_port = self.nodes_config['switches_list'][str(dp.id)]['core_port']
                    actions = [ofp_parser.OFPActionOutput(out_port)]
                    inst = [ofp_parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions)]
                    match = ofp_parser.OFPMatch(in_port=in_port, eth_type=0x0800, ipv4_dst=server_entry['ip'])
                    mod = ofp_parser.OFPFlowMod(datapath=dp, buffer_id=msg.buffer_id, priority=10,
                                                match=match, instructions=inst, table_id=1)
                    dp.send_msg(mod)
            else:
                self.qos_func(ev, self.nodes_config['switches_list'][str(dp.id)], self.nodes_config)

        elif self.nodes_config['switches_list'][str(dp.id)]['type'] == "core" or self.nodes_config['switches_list'][str(dp.id)]['type'] == 'client-leaf-ext':

            if len(self.nodes_config['switches_list'][str(dp.id)]['leaf_ports']) > 1:
                for leaf in self.nodes_config['switches_list'][str(dp.id)]['leaf_ports']:
                    leaf_params = leaf.split(":")
                    leaf_switch_id = -1
                    leaf_switch_port = -1

                    if len(leaf_params) >= 2:
                        try:
                            leaf_switch_id = int(leaf_params[0])
                            leaf_switch_port = int(leaf_params[1])
                        except ValueError:
                            pass
                    if leaf_switch_id > 0 and leaf_switch_port > 0:
                        for client_entry in self.nodes_config['clients_list']:
                            if client_entry['switch_id'] == leaf_switch_id:
                                # check first if for refactor
                                out_port = leaf_switch_port
                                actions = [ofp_parser.OFPActionOutput(out_port)]
                                inst = [ofp_parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions)]
                                match = ofp_parser.OFPMatch(in_port=in_port, eth_type=0x0800, ipv4_dst=client_entry['ip'])
                                mod = ofp_parser.OFPFlowMod(datapath=dp, buffer_id=msg.buffer_id, priority=10,
                                                            match=match, instructions=inst, table_id=1)
                                dp.send_msg(mod)

                            if self.nodes_connect[f"switch{dp.id}:{client_entry['name']}"] == leaf_switch_id:
                                # check first if for refactor
                                out_port = leaf_switch_port
                                actions = [ofp_parser.OFPActionOutput(out_port)]
                                inst = [ofp_parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions)]
                                match = ofp_parser.OFPMatch(in_port=in_port, eth_type=0x0800, ipv4_dst=client_entry['ip'])
                                mod = ofp_parser.OFPFlowMod(datapath=dp, buffer_id=msg.buffer_id, priority=10,
                                                            match=match, instructions=inst, table_id=1)
                                dp.send_msg(mod)

            elif len(self.nodes_config['switches_list'][str(dp.id)]['leaf_ports']) == 1:
                leaf_params = self.nodes_config['switches_list'][str(dp.id)]['leaf_ports'][0].split(":")
                leaf_switch_id = -1
                leaf_switch_port = -1

                if len(leaf_params) >= 2:
                    try:
                        leaf_switch_id = int(leaf_params[0])
                        leaf_switch_port = int(leaf_params[1])
                    except ValueError:
                        pass

                if leaf_switch_port > 0:
                    for client_entry in self.nodes_config['clients_list']:
                        out_port = leaf_switch_port
                        actions = [ofp_parser.OFPActionOutput(out_port)]
                        inst = [ofp_parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions)]
                        match = ofp_parser.OFPMatch(in_port=in_port, eth_type=0x0800, ipv4_dst=client_entry['ip'])
                        mod = ofp_parser.OFPFlowMod(datapath=dp, buffer_id=msg.buffer_id, priority=10,
                                                    match=match, instructions=inst, table_id=1)
                        dp.send_msg(mod)

            if self.nodes_config['switches_list'][str(dp.id)]['qos_type'] == 'none':
                for server_entry in self.nodes_config['servers_list']:
                    if self.nodes_config['switches_list'][str(dp.id)]['type'] == "core":
                        out_port = int(self.nodes_config['switches_list'][str(dp.id)][str(server_port[0])])
                    elif self.nodes_config['switches_list'][str(dp.id)]['type'] == "client-leaf-ext":
                        out_port = self.nodes_config['switches_list'][str(dp.id)]['core_port']
                    actions = [ofp_parser.OFPActionOutput(out_port)]
                    inst = [ofp_parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions)]
                    match = ofp_parser.OFPMatch(in_port=in_port, eth_type=0x0800, ipv4_dst=server_entry['ip'])
                    mod = ofp_parser.OFPFlowMod(datapath=dp, buffer_id=msg.buffer_id, priority=10,
                                                match=match, instructions=inst, table_id=1)
                    dp.send_msg(mod)
            else:
                self.qos_func(ev, self.nodes_config['switches_list'][str(dp.id)], self.nodes_config)

        elif self.nodes_config['switches_list'][str(dp.id)]['type'] == "server-leaf":
            for client_entry in self.nodes_config['clients_list']:
                out_port = self.nodes_config['switches_list'][str(dp.id)]['core_port']
                actions = [ofp_parser.OFPActionOutput(out_port)]
                inst = [ofp_parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions)]
                match = ofp_parser.OFPMatch(in_port=in_port, eth_type=0x0800, ipv4_dst=client_entry['ip'])
                mod = ofp_parser.OFPFlowMod(datapath=dp, buffer_id=msg.buffer_id, priority=10,
                                            match=match, instructions=inst, table_id=1)
                dp.send_msg(mod)

            for server_entry in self.nodes_config['servers_list']:
                out_port = server_entry['port']
                actions = [ofp_parser.OFPActionOutput(out_port)]
                inst = [ofp_parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions)]
                match = ofp_parser.OFPMatch(in_port=in_port, eth_type=0x0800, ipv4_dst=server_entry['ip'])
                mod = ofp_parser.OFPFlowMod(datapath=dp, buffer_id=msg.buffer_id, priority=10,
                                            match=match, instructions=inst, table_id=1)
                dp.send_msg(mod)





















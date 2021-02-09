"""
    JETR
"""

import pickle
import yaml
import os

def basic_cbq_leaves(event, switch, nodes_config):
    msg = event.msg
    dp = msg.datapath
    ofp = dp.ofproto
    ofp_parser = dp.ofproto_parser
    in_port = msg.match['in_port']

    last_queue_id = switch['queue_count'] - 1
    for trcls in nodes_config['traffic']:
        out_port = switch['qos_port']
        actions = [ofp_parser.OFPActionOutput(out_port), 
                                            ofp_parser.OFPActionSetQueue(
                                                queue_id=nodes_config['traffic'][trcls]['proto_queue_id'])]
        inst = [ofp_parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions)]
        match = ofp_parser.OFPMatch(in_port=in_port, eth_type=0x0800, 
                                    ip_proto=nodes_config['traffic'][trcls]['nwproto'], 
                                    tcp_dst=nodes_config['traffic'][trcls]['tpdst'])
        mod = ofp_parser.OFPFlowMod(datapath=dp, buffer_id=msg.buffer_id, 
                                    priority=nodes_config['traffic'][trcls]['proto_priority'], 
                                    match=match, instructions=inst, table_id=1)

        dp.send_msg(mod)

    for server_entry in nodes_config['servers_list']:
        out_port = switch['qos_port']
        actions = [ofp_parser.OFPActionOutput(out_port), ofp_parser.OFPActionSetQueue(queue_id=last_queue_id)]
        inst = [ofp_parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions)]
        match = ofp_parser.OFPMatch(in_port=in_port, eth_type=0x0800, ipv4_dst=server_entry['ip'])
        mod = ofp_parser.OFPFlowMod(datapath=dp, buffer_id=msg.buffer_id, priority=10,
                                    match=match, instructions=inst, table_id=1)
        out = ofp_parser.OFPPacketOut(datapath=dp, buffer_id=ofp.OFP_NO_BUFFER,
                                      in_port=in_port, actions=actions, data=msg.data)
        dp.send_msg(mod)

def basic_cbq_core(event, switch, nodes_config):
    msg = event.msg
    dp = msg.datapath
    ofp = dp.ofproto
    ofp_parser = dp.ofproto_parser
    in_port = msg.match['in_port']

    last_queue_id = switch['queue_count'] - 1
    for trcls in nodes_config['traffic']:
        out_port = switch['qos_port']
        actions = [ofp_parser.OFPActionOutput(out_port), 
                                            ofp_parser.OFPActionSetQueue(
                                                queue_id=nodes_config['traffic'][trcls]['proto_queue_id'])]
        inst = [ofp_parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions)]
        match = ofp_parser.OFPMatch(in_port=in_port, eth_type=0x0800, 
                                    ip_proto=nodes_config['traffic'][trcls]['nwproto'], 
                                    tcp_dst=nodes_config['traffic'][trcls]['tpdst'])
        mod = ofp_parser.OFPFlowMod(datapath=dp, buffer_id=msg.buffer_id, 
                                    priority=nodes_config['traffic'][trcls]['proto_priority'], 
                                    match=match, instructions=inst, table_id=1)

        dp.send_msg(mod)

    for server_entry in nodes_config['servers_list']:
        out_port = switch['qos_port']
        actions = [ofp_parser.OFPActionOutput(out_port), ofp_parser.OFPActionSetQueue(queue_id=last_queue_id)]
        inst = [ofp_parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions)]
        match = ofp_parser.OFPMatch(in_port=in_port, eth_type=0x0800, ipv4_dst=server_entry['ip'])
        mod = ofp_parser.OFPFlowMod(datapath=dp, buffer_id=msg.buffer_id, priority=10,
                                    match=match, instructions=inst, table_id=1)
        out = ofp_parser.OFPPacketOut(datapath=dp, buffer_id=ofp.OFP_NO_BUFFER,
                                      in_port=in_port, actions=actions, data=msg.data)
        dp.send_msg(mod)

def src_cbq_leaves(event, switch, nodes_config):
    msg = event.msg
    dp = msg.datapath
    ofp = dp.ofproto
    ofp_parser = dp.ofproto_parser
    in_port = msg.match['in_port']

    for client_ip in nodes_config['sourceQueueMapDict']:
        queue_to_use = -1
        switch_to_use = -1
        for switch_queue in nodes_config['sourceQueueMapDict'][client_ip]:
            switch_queue_list = switch_queue.split(":")
            if len(switch_queue_list) >= 2:
                try:
                    switch_queue_list[0] = switch_queue_list[0].replace(",", "").replace("[", "").replace("]", "").split(" ")
                    switch_queue_list[0] = list(map(int, switch_queue_list[0]))
                    if switch['id'] in switch_queue_list[0]:
                        switch_to_use = switch['id']
                        queue_to_use = int(switch_queue_list[1])
                        break
                except ValueError as err:
                    print (f"ValueError: {err}")
        if queue_to_use >= 0 and switch_to_use >= 1 and queue_to_use < switch['queue_count']:
            out_port = switch['qos_port']
            actions = [ofp_parser.OFPActionOutput(out_port), ofp_parser.OFPActionSetQueue(queue_id=queue_to_use)]
            inst = [ofp_parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions)]
            match = ofp_parser.OFPMatch(in_port=in_port, eth_type=0x0800, ipv4_src=client_ip.strip()) # , ipv4_dst=serverEntry.ip
            mod = ofp_parser.OFPFlowMod(datapath=dp, buffer_id=msg.buffer_id, priority=100,
                                        match=match, instructions=inst, table_id=1)
            dp.send_msg(mod)

def src_cbq_core(event, switch, nodes_config):
    msg = event.msg
    dp = msg.datapath
    ofp = dp.ofproto
    ofp_parser = dp.ofproto_parser
    in_port = msg.match['in_port']

    for client_ip in nodes_config['sourceQueueMapDict']:
        queue_to_use = -1
        switch_to_use = -1
        for switch_queue in nodes_config['sourceQueueMapDict'][client_ip]:
            switch_queue_list = switch_queue.split(":")
            if len(switch_queue_list) >= 2:
                try:
                    switch_queue_list[0] = switch_queue_list[0].replace(",", "").replace("[", "").replace("]", "").split(" ")
                    switch_queue_list[0] = list(map(int, switch_queue_list[0]))
                    if switch['id'] in switch_queue_list[0]:
                        switch_to_use = switch['id']
                        queue_to_use = int(switch_queue_list[1])
                        break
                except ValueError as err:
                    print (f"ValueError: {err}")
        if queue_to_use >= 0 and switch_to_use >= 1 and queue_to_use < switch['queue_count']:
            out_port = switch['qos_port']
            actions = [ofp_parser.OFPActionOutput(out_port), ofp_parser.OFPActionSetQueue(queue_id=queue_to_use)]
            inst = [ofp_parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions)]
            match = ofp_parser.OFPMatch(in_port=in_port, eth_type=0x0800, ipv4_src=client_ip.strip()) # , ipv4_dst=serverEntry.ip
            mod = ofp_parser.OFPFlowMod(datapath=dp, buffer_id=msg.buffer_id, priority=100,
                                        match=match, instructions=inst, table_id=1)
            dp.send_msg(mod)

def dst_cbq_leaves(event, switch, nodes_config):
    msg = event.msg
    dp = msg.datapath
    ofp = dp.ofproto
    ofp_parser = dp.ofproto_parser
    in_port = msg.match['in_port']

    last_queue_id = switch['queue_count'] - 1
    for server_entry in nodes_config['servers_list']:
        out_port = switch['qos_port']
        actions = [ofp_parser.OFPActionOutput(out_port), ofp_parser.OFPActionSetQueue(queue_id=server_entry['dst_queue_id'])]
        inst = [ofp_parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions)]
        match = ofp_parser.OFPMatch(in_port=in_port, eth_type=0x0800, ipv4_dst=server_entry['ip'].strip())
        mod = ofp_parser.OFPFlowMod(datapath=dp, buffer_id=msg.buffer_id, priority=server_entry['proto_priority'],
                                    match=match, instructions=inst, table_id=1)
        dp.send_msg(mod)

    out_port = switch['qos_port']
    actions = [ofp_parser.OFPActionOutput(out_port), ofp_parser.OFPActionSetQueue(queue_id=last_queue_id)]
    inst = [ofp_parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions)]
    match = ofp_parser.OFPMatch(in_port=in_port, eth_type=0x0800) 
    mod = ofp_parser.OFPFlowMod(datapath=dp, buffer_id=msg.buffer_id, priority=10,
                                match=match, instructions=inst, table_id=1)
    dp.send_msg(mod)

def dst_cbq_core(event, switch, nodes_config):
    msg = event.msg
    dp = msg.datapath
    ofp = dp.ofproto
    ofp_parser = dp.ofproto_parser
    in_port = msg.match['in_port']

    last_queue_id = switch['queue_count'] - 1
    for server_entry in nodes_config['servers_list']:
        out_port = switch['qos_port']
        actions = [ofp_parser.OFPActionOutput(out_port), ofp_parser.OFPActionSetQueue(queue_id=server_entry['dst_queue_id'])]
        inst = [ofp_parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions)]
        match = ofp_parser.OFPMatch(in_port=in_port, eth_type=0x0800, ipv4_dst=server_entry['ip'].strip())
        mod = ofp_parser.OFPFlowMod(datapath=dp, buffer_id=msg.buffer_id, priority=server_entry['proto_priority'],
                                    match=match, instructions=inst, table_id=1)
        dp.send_msg(mod)

    out_port = switch['qos_port']
    actions = [ofp_parser.OFPActionOutput(out_port), ofp_parser.OFPActionSetQueue(queue_id=last_queue_id)]
    inst = [ofp_parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions)]
    match = ofp_parser.OFPMatch(in_port=in_port, eth_type=0x0800) 
    mod = ofp_parser.OFPFlowMod(datapath=dp, buffer_id=msg.buffer_id, priority=10,
                                match=match, instructions=inst, table_id=1)
    dp.send_msg(mod)

def srcdst_cbq_leaves(event, switch, nodes_config):
    msg = event.msg
    dp = msg.datapath
    ofp = dp.ofproto
    ofp_parser = dp.ofproto_parser
    in_port = msg.match['in_port']

    for client_ip in nodes_config['sourceQueueMapDict']:
        queue_to_use = -1
        switch_to_use = -1
        for switch_queue in nodes_config['sourceQueueMapDict'][client_ip]:
            switch_queue_list = switch_queue.split(":")
            if len(switch_queue_list) >= 2:
                try:
                    switch_queue_list[0] = switch_queue_list[0].replace(",", "").replace("[", "").replace("]", "").split(" ")
                    switch_queue_list[0] = list(map(int, switch_queue_list[0]))
                    if switch['id'] in switch_queue_list[0]:
                        switch_to_use = switch['id']
                        queue_to_use = int(switch_queue_list[1])
                        break
                except ValueError as err:
                    print (f"ValueError: {err}")
        if queue_to_use >= 0 and switch_to_use >= 1 and queue_to_use < switch['queue_count']:
            for server_entry in nodes_config['servers_list']:
                out_port = switch['qos_port']
                actions = [ofp_parser.OFPActionOutput(out_port), ofp_parser.OFPActionSetQueue(queue_id=queue_to_use)]
                inst = [ofp_parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions)]
                match = ofp_parser.OFPMatch(in_port=in_port, eth_type=0x0800, ipv4_src=client_ip.strip(), ipv4_dst=server_entry['ip']) # , ipv4_dst=serverEntry.ip
                mod = ofp_parser.OFPFlowMod(datapath=dp, buffer_id=msg.buffer_id, priority=100,
                                            match=match, instructions=inst, table_id=1)
                dp.send_msg(mod)

def srcdst_cbq_core(event, switch, nodes_config):
    msg = event.msg
    dp = msg.datapath
    ofp = dp.ofproto
    ofp_parser = dp.ofproto_parser
    in_port = msg.match['in_port']

    for client_ip in nodes_config['sourceQueueMapDict']:
        queue_to_use = -1
        switch_to_use = -1
        for switch_queue in nodes_config['sourceQueueMapDict'][client_ip]:
            switch_queue_list = switch_queue.split(":")
            if len(switch_queue_list) >= 2:
                try:
                    switch_queue_list[0] = switch_queue_list[0].replace(",", "").replace("[", "").replace("]", "").split(" ")
                    switch_queue_list[0] = list(map(int, switch_queue_list[0]))
                    if switch['id'] in switch_queue_list[0]:
                        switch_to_use = switch['id']
                        queue_to_use = int(switch_queue_list[1])
                        break
                except ValueError as err:
                    print (f"ValueError: {err}")
        if queue_to_use >= 0 and switch_to_use >= 1 and queue_to_use < switch['queue_count']:
            for server_entry in nodes_config['servers_list']:
                out_port = switch['qos_port']
                actions = [ofp_parser.OFPActionOutput(out_port), ofp_parser.OFPActionSetQueue(queue_id=queue_to_use)]
                inst = [ofp_parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions)]
                match = ofp_parser.OFPMatch(in_port=in_port, eth_type=0x0800, ipv4_src=client_ip.strip(), ipv4_dst=server_entry['ip']) # , ipv4_dst=serverEntry.ip
                mod = ofp_parser.OFPFlowMod(datapath=dp, buffer_id=msg.buffer_id, priority=100,
                                            match=match, instructions=inst, table_id=1)
                dp.send_msg(mod)
                
# def functions_serializer():
#     # BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(os.pardir)))
#     BASEDIR = os.getcwd()
#     OUTDIR = f"{BASEDIR}/PKL/ALGO"
#     yml = f"{BASEDIR}/CONFIG/class_profile_functionname.yml"
#     print (yml)
#     with open(yml, 'rb') as yml_file:
#         yml_data = yaml.load(yml_file) # , Loader=yaml.FullLoader
#         print (yml_data)

#     for case in yml_data['class_profiles']:
#         print (case)
#         pkl = f"{OUTDIR}/usecase_{case}_{yml_data['class_profiles'][str(case)]['func_name']}_qosprotocol.pkl"
#         with open(pkl, 'wb') as pkl_file:
#             pickle.dump(eval(yml_data['class_profiles'][case]['func_name']), pkl_file, pickle.DEFAULT_PROTOCOL)



# functions_serializer()




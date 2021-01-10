#JETR

#! /bin/python

import clients
import hosts
import load_conf
import sourcequeue
import switch_configs
import ovs_qosgenerator
import os

OUTDIR = f"{os.getcwd()}/config/custom"
EXECDIR = f"{os.getcwd()}/scripts/custom"
clients.save_to_conf(OUTDIR)
load_conf.save_to_conf(OUTDIR)
sourcequeue.save_to_conf(OUTDIR)
switch_configs.save_to_conf(OUTDIR)
ovs_qosgenerator.save_to_conf(OUTDIR, EXECDIR)
hosts.save_to_conf(OUTDIR)




from network_topologies import *

BASEDIR = os.getcwd()
TOPO_OUTDIR = "{}/pkl/topo".format(BASEDIR)
topo_yml = "{}/config/topology_definitions.yml".format(BASEDIR)

with open(topo_yml) as yml_file:
	yml_data = yaml.load(yml_file)
	print (yml_data)

	for topo in yml_data['topology']:
		print (topo)
		pkl = "{}/topo_{}.pkl".format(TOPO_OUTDIR, topo)
		with open(pkl, 'wb') as pkl_file:
			pickle.dump(eval(topo), pkl_file) # , pickle.DEFAULT_PROTOCOL



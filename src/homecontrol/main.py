import os, sys, argparse, time, traceback, json
import logging as log
from ConfigParser import ConfigParser
from homecontrol.server import Server
from homecontrol.handler import Handler
from homecontrol.device import Device
from homecontrol.common import *

def show_status(devices):

	online = (len(devices) > 0)
	for dev in devices:
		
		info = dev.get_info()
		
		memory_info = ""
		if info["status"] == "online":
			memory_info = ", memory %s free" % info["memory"]

		log.info("Device \"%s\", host %s:%i, features %s, status \"%s\" %s" % (
			dev.name, dev.host, dev.port_cmds, dev.features, info["status"], memory_info))

	return info["status"] == "online"

def rf_send_tristate(device, tristate):

	if device is None:
		raise ValueError("Unkown or non-existing device: \"%s\"" % str(device))

	device.rf_send_tristate(tristate)
		
def send_json(type, device):
	
	if device is None:
		raise ValueError("Unkown or non-existing device: \"%s\"" % str(device))
	
	try:
		
		log.info("Paste json data and press strg-d to send or strg-c to cancel!")
		
		if type == HC_TYPE_RF:
			device.rf_send_json(sys.stdin.readlines())
			
		elif type == HC_TYPE_IR:
			device.ir_send_json(sys.stdin.readlines())
			
		else: raise ValueError("Unkown HC type: %s" % type)
					
	except KeyboardInterrupt:
		pass
			
def listen(device): # TODO: Introduce filters!
	
	if device is None:
		raise ValueError("Unkown or non-existing device: \"%s\"" % str(device))	

	def event_callback(event, event_list):
		log.info(json.dumps(event, cls=JSONEncoder))
	
	device.add_listener(event_callback)
	
	log.info("Listening to events, ctrl-c to stop ...")
	while True:
		time.sleep(1)	

def main(argv):
	 
	default_config = "config.conf";
	default_port = 4000
	default_bind = "localhost"
	default_log = None
	default_log_level = log.DEBUG

	parser = argparse.ArgumentParser(
		description="HomeControl Server V%.3f" % HC_VERSION)

	parser.add_argument("-b", "--bind", type=str, default=default_bind, 
		help="Host to bind server to, default is \"%s\"." % default_bind)
	parser.add_argument("-p", "--port", type=int, default=default_port, 
		help="TCP/IP port to bind server or to connect to via command line, default is %d" % default_port)
	parser.add_argument("-c", "--config", type=str, default=default_config, 
		help="Path to the configuration file, default is \"%s\"" % default_config)
	parser.add_argument("-l", "--log", type=str, default=default_log,
		help="Path to the log file which is \"%s\" by default" % default_log)
	parser.add_argument("-d", "--loglevel", type=int, default=default_log_level,
		help="Log level: DEBUG (%i), INFO (%i), WARNING (%i), ERROR (%i), CRITICAL (%i), "
		"default is %i" %
		(log.DEBUG, log.INFO, log.WARNING, log.ERROR, log.CRITICAL, default_log_level))

	dev_parser = parser.add_argument_group("Device")
	dev_parser.add_argument("--status", action = "store_true",
		help="Display status information about configured devices")
	dev_parser.add_argument("--device", type=str,
		help="Specify a device by using its name or IP address")
	dev_parser.add_argument("--rf_tristate", type=str,
		help="Send tristate (e.g. fff0fff0ffff) via RF module of specified device")
	dev_parser.add_argument("--rf_json", action = "store_true",
		help="Read json code from STDIN and send it via RF module of specified device")
	dev_parser.add_argument("--ir_json", action = "store_true",
		help="Read json code from STDIN and send it via IR module of specified device")	
	dev_parser.add_argument("--listen", action = "store_true",
		help="Listen to events from specified device")

	options = parser.parse_args()
	host = options.bind
	port = options.port
	config = ConfigParser()
	config.read(options.config)

	log.basicConfig(filename=options.log,level=options.loglevel, format="%(message)s")

	# Get configured devices, find specified one if given!
	devices = []
	device = None
	id = 0
	for section in config.sections():
		if section == "global": continue
		d = Device(id, section, config)
		id += 1
		log.debug("Adding device \"%s\", host %s:%i, features: %s" % 
			(d.name, d.host, d.port_cmds, d.features))
		devices.append(d)

		if options.device and (options.device == d.name or options.device == d.host):
			device = d

	retval = 0
	server = None
	
	try:
		if options.status:
			show_status(devices)

		elif options.rf_tristate:
			rf_send_tristate(device, options.rf_tristate)
			
		elif options.rf_json:
			send_json(HC_TYPE_RF, device)
			
		elif options.ir_json:
			send_json(HC_TYPE_IR, device)

		elif options.listen:
			listen(device)

		else:
			server = Server(('', port), Handler)
			server.set_document_root(os.path.dirname(os.path.realpath(__file__)))
			server.sql_connect(config.get("global", "database"))
			server.set_config(config)
			server.add_devices(devices)
			server.load_plugins(os.path.dirname(os.path.realpath(__file__)) + os.sep + "plugins");

			log.info("Starting server to listen on %s:%d" % (host, port))
			server.serve_forever()

	except KeyboardInterrupt:
		
		log.info("Stopping server ...")
		if server is not None:
			server.stop()
		pass

	except:

		log.error("%s: %s" % (sys.exc_info()[0].__name__, sys.exc_info()[1]))
		log.debug("".join(traceback.format_list(traceback.extract_tb(sys.exc_info()[2]))))
		retval = 1
		pass

	for device in devices:
		device.stop_listener()
		
	sys.exit(retval)

if __name__ == "__main__":
	main(sys.argv)
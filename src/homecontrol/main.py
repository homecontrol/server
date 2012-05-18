import os, sys, argparse
import logging as log
from ConfigParser import ConfigParser
from server import HCServer
from handler import HCHandler
from device import HCDevice

__version__ = 1.0

def show_status(devices):

	online = (len(devices) > 0)
	for dev in devices:

		if dev.is_available(): status = "online"
		else:
			status = "offline"
			online = False

		log.info("Device %s, host %s:%i, features %s, status \"%s\"" % (
			dev.name, dev.host, dev.port_cmds, dev.features, status))

	return online

def main(argv):

	default_config = "config.conf";
	default_port = 4000
	default_bind = "localhost"
	default_log = None
	default_log_level = log.DEBUG

	parser = argparse.ArgumentParser(
		description="HomeControl Server V%.3f" % __version__)

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
	dev_parser.add_argument("-s", "--status", action = "store_true",
		help="Display status information about configured devices")

	options = parser.parse_args()
	host = options.bind
	port = options.port
	config = ConfigParser()
	config.read(options.config)

	log.basicConfig(filename=options.log,level=options.loglevel)

	# Get configured devices
	devices = []
	for section in config.sections():
		if section == "global": continue
		device = HCDevice(section, config)
		log.debug("Adding device %s, host %s:%i, features: %s" % 
			(device.slug, device.host, device.port_cmds, device.features))
		devices.append(device)

	if options.status:
		sys.exit(show_status(devices))		

	try:
		server = HCServer(('', port), HCHandler)
		server.set_config(config)
		server.add_devices(devices)

		log.info("Starting server to listen on %s:%d." % (host, port))
		server.serve_forever()
	except KeyboardInterrupt:
		pass

	server.server_close();
	sys.exit(0)

if __name__ == "__main__":
	main(sys.argv)
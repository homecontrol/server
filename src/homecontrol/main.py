import os, sys, argparse
from ConfigParser import ConfigParser
from server import HCServer
from handler import HCHandler

__version__ = 1.0

def main(argv):

	default_config = "config.conf";
	default_port = 4000
	default_bind = "localhost"

	parser = argparse.ArgumentParser(
		description="HomeControl Server V%.3f" % __version__)

	parser.add_argument("-b", "--bind", type=str, default=default_bind, 
		help="Host to bind server to, default is \"%s\"." % default_bind)
	parser.add_argument("-p", "--port", type=int, default=default_port, 
		help="TCP/IP port to bind server or to connect to via command line, default is %d" % default_port)
	parser.add_argument("-c", "--config", type=str, default=default_config, 
		help="Path to the configuration file, default is \"%s\"" % default_config)

	options = parser.parse_args()
	host = options.bind
	port = options.port
	config = ConfigParser()
	config.read(options.config)

	server = HCServer(('', port), HCHandler)
	server.set_config(config)

	try:
		server.serve_forever()
	except KeyboardInterrupt:
		pass

	server.server_close();
	sys.exit(0)

if __name__ == "__main__":
	main(sys.argv)
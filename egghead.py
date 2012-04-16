#!/usr/bin/env python
import sys, time
from daemon import Daemon

from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor

###############################################################################
# Configuration values
###############################################################################

# LISTEN_PORTS
#  You may specify one to many ports that the server will be listening on.
#
LISTEN_PORTS = [5000, 5001, 5002]

# ENCRYPTION_KEY
#  The encryption key that is used in the XOR-based encryption.
#
ENCRYPTION_KEY = "Martina"

# TIMEOUT
#  How long to wait before any line is entered.
#  N.B: The timeout is not reset when input is recevied, only when a complete
#       line is received.
#
TIMEOUT = 15.0

###############################################################################


# This is the actual protocol based on a Telnet line based input protocol.
class EncryptEmailProtocol(LineReceiver):
	def connectionMade(self):
		# Abort after a reasonable time.
		reactor.callLater(self.factory.timeout, self.__timeout)
		self.transport.write("Welcome\nEnter your email: ")

	def lineReceived(self, line):
		self.transport.write("Your secret is: %s\n" % self.__encryptLine(line))
		self.transport.loseConnection()

	def __encryptLine(self, line):
		# Duplicate key depending on length of input.
		key = self.factory.key * (len(line) / len(self.factory.key) + 1)
		# Return a simple XORed result.
		return "".join(map(lambda x: "%02x" % x, [ord(key[i]) ^ ord(c) for i, c in enumerate(line)]))

	def __timeout(self):
		self.sendLine("\nSorry, but you are too slow.")
		self.transport.loseConnection()

class EncryptEmailProtocolFactory(Factory):
	protocol = EncryptEmailProtocol
	def __init__(self, key, timeout=15.0):
		self.key = key
		self.timeout = timeout

# Our daemon
class Egghead(Daemon):
	def run(self):
		instance = EncryptEmailProtocolFactory(ENCRYPTION_KEY, TIMEOUT)
		for port in LISTEN_PORTS:
			reactor.listenTCP(port, instance)
		reactor.run()

if __name__ == "__main__":
	# TODO: Determine the temp directory in an OS agnostic way instead.
	daemon = Egghead("/tmp/egghead.pid")
	if len(sys.argv) == 2:
		if "start" == sys.argv[1]:
			daemon.start()
		elif "stop" == sys.argv[1]:
			daemon.stop()
		elif "restart" == sys.argv[1]:
			daemon.restart()
		else:
			sys.stderr.write("Unknown command.\n")
			sys.exit(2)
		sys.exit(0)
	else:
		sys.stdout.write("usage: {0} start|stop|restart\n".format(sys.argv[0]))
		sys.exit(2)


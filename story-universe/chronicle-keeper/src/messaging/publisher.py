class LogPublisher:
	def __init__(self, address="tcp://192.168.0.84:5555"):
		context = zmq.Context()
		self.socket = context.socket(zmq.PUB)
		self.socket.connect(address)

	def publish_log(self, log_data):
		self.socket.send_json({"type": "log", **log_data})

"""
ZeroMQ Tick Publisher for Chronicle Keeper
------------------------------------------
Publishes tick and event messages to other nodes (e.g., Evo-X2) via ZeroMQ PUB socket.
"""

import zmq

class TickPublisher:
	def __init__(self, address="tcp://*:5555"):
		context = zmq.Context()
		self.socket = context.socket(zmq.PUB)
		self.socket.bind(address)

	def publish_tick(self, tick_data):
		self.socket.send_json({"type": "system_tick", **tick_data})

	def publish_event(self, event_data):
		self.socket.send_json(event_data)

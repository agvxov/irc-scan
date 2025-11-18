#!/usr/bin/env python3
# @BAKE ./$@ --port 6697 --tls --list-file list.list
import re
import ssl
import socket
import argparse
import traceback
from irc.client import SimpleIRCClient, ServerConnectionError
from irc.connection import Factory
from time import time

def iter_listfile(path):
	with open(path, encoding="utf-8") as f:
		for line in f:
			line = line.strip()
			if not line or line.startswith("#"): continue
			yield line

def make_factory(host: str, timeout: float, tls: bool):
	def connect_with_timeout(address):
		s = socket.create_connection(address, timeout=timeout)
		if tls:
			#ctx = ssl.create_default_context()
			ctx = ssl._create_unverified_context()
			s = ctx.wrap_socket(s, server_hostname=host)
		return s
	return connect_with_timeout

class IRCscanner(SimpleIRCClient):
	def __init__(self, filter_re=None):
		super().__init__()
		self.filter_re = filter_re
		self.listed = 0

	def on_welcome(self, connection, event):
		print(f"-- Connected to {connection.server_address} --")
		connection.list()

	def on_list(self, connection, event):
		try:
			channel, users, topic = event.arguments
			users = int(users)
		except ValueError: return
		if self.filter_re and not self.filter_re.search(channel): return
		print(f"{channel:30} {users:4d}  {topic}")
		self.listed += 1

	def on_listend(self, connection, event):
		print(f"\n-- LIST complete ({self.listed} channels) --")
		connection.quit("Nothing ever happens.")

def probe(args):
	filter_re = re.compile(args.filter) if args.filter else None
	port = args.port or (6697 if args.tls else 6667)

	client = IRCscanner(filter_re)
	try:
		if args.tls:
			ssl_ctx = ssl.create_default_context()
			factory = make_factory(args.host, 5.0, args.tls)
			client.connect(args.host, port, args.nick, connect_factory=factory)
		else:
			client.connect(args.host, port, args.nick)
	except ServerConnectionError as e:
		print("Connection failed:", e)

	timeout = 5
	start = time()

	while client.connection.is_connected():
		try: client.reactor.process_once(timeout=0.2)
		except Exception as e:
			traceback.print_exception(type(e), e, e.__traceback__)
			continue
		if time() - start > timeout:
			print(f"Timeout on {args.host}")
			try: client.connection.disconnect("timeout")
			except Exception: pass
			break

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("host", nargs="?")
	parser.add_argument("--port", type=int, default=None)
	parser.add_argument("--tls", action="store_true")
	parser.add_argument("--nick", default="ChudProbe")
	parser.add_argument("--filter", help="regex for channels")
	parser.add_argument("--list-file", help="file containing hosts to probe")

	args = parser.parse_args()

	hosts_to_probe = []

	if args.list_file:	hosts_to_probe.extend(iter_listfile(args.list_file))
	elif args.host:		hosts_to_probe.append(args.host)
	else:				parser.error("Either a host or --list-file must be specified")

	for host in hosts_to_probe:
		print(f"Connecting to {host}...")
		probe(
			argparse.Namespace(
				host=host,
				port=args.port,
				tls=args.tls,
				nick=args.nick,
				filter=args.filter,
			)
		)

if __name__ == "__main__": main()

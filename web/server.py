#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler,HTTPServer

answer="console.log('hello !')";

class HttpProcessor(BaseHTTPRequestHandler):
	def do_GET(self):
		self.send_response(200)
		self.send_header('content-type','application/javascript')
		self.end_headers()
		self.wfile.write(bytes(answer,encoding="utf-8"))


def mainloop():
	serv = HTTPServer(("localhost",6205),HttpProcessor)
	serv.serve_forever()

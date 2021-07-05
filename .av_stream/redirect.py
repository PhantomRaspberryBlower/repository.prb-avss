#!/usr/bin/env python3

'''
Written by: Phantom Raspberry Blower (The PRB)
Date: 01-05-2021
Description: Used to redirect requests on port 80 to port 8000.
This runs at startup under sudo and redirects to the settings page
which runs under the default pi user. Tested on Raspberry Pi.
Usage: sudo /home/pi/.av_stream/redirect.py
'''

import sys
import socket
from http.server import HTTPServer, BaseHTTPRequestHandler

DEST_PORT = 8000

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

class Redirect(BaseHTTPRequestHandler):
   def do_GET(self):
       self.send_response(302)
       self.send_header('Location', 'http://%s:%s/index.html' % (get_ip(), DEST_PORT))
       self.end_headers()

HTTPServer(("", int(80), Redirect().serve_forever()))
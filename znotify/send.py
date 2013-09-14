#!/usr/bin/python

import os
import sys
import argparse
import logging
import shlex
import json
import time

import zmq

from znotify.common import setup_logging

class Sender (object):
    def __init__(self, pub_uri=None):
        self.pub_uri = pub_uri

        assert self.pub_uri is not None

        self.setup_log()
        self.setup_zmq()
        self.setup_sockets()

    def setup_log(self):
        self.log = logging.getLogger('znotify.send')

    def setup_zmq(self):
        self.log.debug('creating zmq context')
        self.context = zmq.Context()

    def setup_sockets(self):
        self.log.debug('creating zmq sockets')
        self.pub = self.context.socket(zmq.PUB)
        self.pub.setsockopt(zmq.LINGER, 500)
        self.log.debug('connecting zmq socket to %s', self.pub_uri)
        self.pub.connect(self.pub_uri)
        time.sleep(0.2)

    def send_event(self, name, message, data):
        self.log.debug('sending %s event', name)
        body = json.dumps({ 'message': message, 'data': data})
        self.pub.send_multipart([name, body])

    def close(self):
        self.pub.close()
        self.pub = None

def parse_args():
    p = argparse.ArgumentParser()

    p.add_argument('--pub', '-p',
        default='tcp://localhost:11111')
    p.add_argument('--verbose', '-v', action='store_true')
    p.add_argument('--debug', action='store_true')

    p.add_argument('event_name')
    p.add_argument('event_message')
    p.add_argument('event_data', nargs='*')

    return p.parse_args()

def main():
    opts = parse_args()

    if opts.debug:
        loglevel = logging.DEBUG
    elif opts.verbose:
        loglevel = logging.INFO
    else:
        loglevel = logging.WARN

    setup_logging(loglevel)

    sender = Sender(pub_uri = opts.pub)
    body = dict(x.split('=') for x in opts.event_data)

    sender.send_event(opts.event_name, opts.event_message, body)

if __name__ == '__main__':
    main()


#!/usr/bin/python

import os
import sys
import argparse
import logging

import zmq

from znotify.common import setup_logging

class Broker (object):
    def __init__(self, sub_uri=None, pub_uri=None):
        self.sub_uri = sub_uri
        self.pub_uri = pub_uri

        assert self.sub_uri is not None
        assert self.pub_uri is not None

        self.setup_log()
        self.setup_zmq()
        self.setup_sockets()

    def setup_log(self):
        self.log = logging.getLogger('znotify.broker')

    def setup_zmq(self):
        self.log.debug('creating zmq context')
        self.context = zmq.Context()

    def setup_sockets(self):
        self.log.debug('creating zmq sockets')
        self.sub = self.context.socket(zmq.SUB)
        self.sub.setsockopt(zmq.SUBSCRIBE, '')
        self.pub = self.context.socket(zmq.PUB)

        self.log.debug('binding zmq sockets')
        self.sub.bind(self.sub_uri)
        self.pub.bind(self.pub_uri)

    def run(self):

        while True:
            self.log.debug('waiting for event')
            try:
                evt = self.sub.recv_multipart()
                assert len(evt) == 2
                self.log.debug('received event %s', evt[0])
                self.pub.send_multipart(evt)
            except Exception, detail:
                self.log.error('failed to recieve event: %s', detail)
                continue
        

def parse_args():
    p = argparse.ArgumentParser()

    p.add_argument('--sub', '-s',
        default='tcp://127.0.0.1:11111')
    p.add_argument('--pub', '-p',
        default='tcp://127.0.0.1:22222')
    p.add_argument('--verbose', '-v', action='store_true')
    p.add_argument('--debug', action='store_true')

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

    broker = Broker(
        sub_uri = opts.sub,
        pub_uri = opts.pub,
    )

    broker.run()

if __name__ == '__main__':
    main()


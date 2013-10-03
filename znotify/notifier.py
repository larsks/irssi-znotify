#!/usr/bin/python

import os
import sys
import argparse
import logging
import json

import pynotify
import zmq
import xidle

from znotify.common import setup_logging

class Notifier (object):
    def __init__(self, sub_uri=None,idle_time=None):
        self.sub_uri = sub_uri
        self.idle_time = int(idle_time)

        assert self.sub_uri is not None

        self.setup_log()
        self.setup_zmq()
        self.setup_sockets()
        self.setup_pynotify()

    def setup_pynotify(self):
        pynotify.init('znotify.notifier')

    def setup_log(self):
        self.log = logging.getLogger('znotify.notifier')

    def setup_zmq(self):
        self.log.debug('creating zmq context')
        self.context = zmq.Context()

    def setup_sockets(self):
        self.log.debug('creating zmq sockets')
        self.sub = self.context.socket(zmq.SUB)
        self.sub.setsockopt(zmq.SUBSCRIBE, '')

    def run(self):
        self.log.debug('connecting zmq sockets')
        self.sub.connect(self.sub_uri)

        while True:
            self.log.debug('waiting for event')
            try:
                evt_name, evt_body = self.sub.recv_multipart()
                self.log.debug('received event %s', evt_name)
                evt_body = json.loads(evt_body)

                assert 'message' in evt_body
                assert 'data' in evt_body
            except Exception, detail:
                self.log.warn('failed to receive event: %s', detail)
                continue

            n = pynotify.Notification(evt_body['message'])

            if self.idle_time is not None and \
                    xidle.idle_time_ms() > (self.idle_time * 1000):
                self.log.debug('persisting notification because user is idle')
                n.set_timeout(pynotify.EXPIRES_NEVER)

            # If there's nothing to receive the notifications, n.show() can
            # throw a glib.GError exception.
            try:
                n.show()
            except:
                pass

def parse_args():
    p = argparse.ArgumentParser()

    p.add_argument('--sub', '-s',
        default='tcp://localhost:22222')
    p.add_argument('--verbose', '-v', action='store_true')
    p.add_argument('--idle-time', '-i',
            default=30)
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

    notifier = Notifier(opts.sub, idle_time=opts.idle_time)
    notifier.run()

if __name__ == '__main__':
    main()


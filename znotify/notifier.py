#!/usr/bin/python

import os
import sys
import argparse
import logging

import json
import pynotify
import zmq

def parse_args():
    p = argparse.ArgumentParser()

    p.add_argument('--sub', '-s',
        default='tcp://localhost:22222')

    return p.parse_args()

def main():
    opts = parse_args()

    pynotify.init('znotify')

    ctx = zmq.Context()
    sub = ctx.socket(zmq.SUB)
    sub.setsockopt(zmq.SUBSCRIBE, '')
    sub.connect(opts.sub)

    while True:
        try:
            evt_name, evt_body = sub.recv_multipart()
            evt_body = json.loads(evt_body)

            assert 'message' in evt_body
            assert 'data' in evt_body
        except:
            continue

        n = pynotify.Notification(evt_body['message'])

        # make the notification persistent if we are away.
        if evt_body['data'].get('away'):
            n.set_timeout(pynotify.EXPIRE_NEVER)
        n.show()

if __name__ == '__main__':
    main()


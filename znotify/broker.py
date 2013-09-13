#!/usr/bin/python

import os
import sys
import argparse

import zmq

def parse_args():
    p = argparse.ArgumentParser()

    p.add_argument('--sub', '-s',
        default='tcp://*:11111')
    p.add_argument('--pub', '-p',
        default='tcp://*:22222')

    return p.parse_args()

def main():
    opts = parse_args()

    ctx = zmq.Context()
    sub = ctx.socket(zmq.SUB)
    sub.setsockopt(zmq.SUBSCRIBE, '')
    sub.bind(opts.sub)

    pub = ctx.socket(zmq.PUB)
    pub.bind(opts.pub)

    while True:
        print 'waiting for event.'
        evt = sub.recv_multipart()
        print evt
        pub.send_multipart(evt)

if __name__ == '__main__':
    main()


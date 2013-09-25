#!/usr/bin/env python

import setuptools

setuptools.setup(
#    install_requires=open('requires.txt').readlines(),
    name = 'znotify',
    packages = ['znotify'],
    entry_points = {
        'console_scripts': [
            'znotify-broker = znotify.broker:main',
            'znotify-notifier = znotify.notifier:main',
            'znotify-send = znotify.send:main',
        ],
    }
)


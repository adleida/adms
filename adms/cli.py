#!/usr/bin/env python
# coding: utf-8

# first of all, load config info
from .config import Config
Config.initialize()

import logging
import argparse
import adms
from adms.app import app


def main():
    ''' set args to provide parameters to users '''

    cli = Config.cfg['cli']
    help = cli['help']
    server = cli['server']
    log = cli['log']

    parser = argparse.ArgumentParser(prog=server['prog'], description=help['overview'])
    parser.add_argument('-v', '--version', help=help['version'], action='version', version=adms.__version__)
    parser.add_argument('-b', '--bind', help=help['bind'], \
            default=server['bind'])
    parser.add_argument('-p', '--port', help=help['port'], type=int, \
            default=server['port'])
    parser.add_argument('-d', '--debug', help=help['debug'], action='store_true', \
            default=False)
    parser.add_argument('-l', '--loglevel', help=help['loglevel'], \
            default=server['loglevel']['default'], choices=server['loglevel']['choices'])
    args = parser.parse_args()
 
    loglev = args.loglevel.upper()
    logging.basicConfig(format=log['format'], \
            datefmt=log['datefmt'], level=loglev)
 
    # entrypoint here
    app.run(host=args.bind, port=args.port, debug=args.debug)

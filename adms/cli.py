#!/usr/bin/env python
# coding: utf-8

import logging
import argparse
import adms


def main():
    ''' set args to provide parameters to users '''

    # first of all, load config info
    from .config import Config
    cli = Config.preset_config()
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
            default=log['loglevel']['default'], choices=log['loglevel']['choices'])
    parser.add_argument('-c', '--config', help=help['config'], \
            default=None)
    args = parser.parse_args()
 
    loglev = args.loglevel.upper()
    logging.basicConfig(format=log['format'], \
            datefmt=log['datefmt'], level=loglev)
 
    cfgpath = args.config
    if not cfgpath:
        logging.error('[PRESET_CONFIG] {}'.\
                format('please show me your config path before all starting'))
        exit()
    Config.initialize(cfgpath=cfgpath)
    from adms.app import app

    # entrypoint here
    app.run(host=args.bind, port=args.port, debug=args.debug)

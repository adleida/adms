# coding: utf-8

import logging
from os import path

from .models.mdsp import Mdsp
from .utils.udefault import load_yaml
from .dao.mongo.daomongo import DaoMongo
from .dao.mongo.daogridfs import DaoGridFS


class Config(object):
    ''' load all info from etc when starting webservice '''

    @staticmethod
    def preset_config():
        cli = {
            'help': {
                'overview': 'use this command could decide to deploy your webserver on variety',
                'bind': 'specify your server host bind',
                'port': 'specify your server port open',
                'version': 'display version of adms',
                'debug': 'switch debug modern to scratch all log output',
                'loglevel': 'adjust more then default level of ouput',
                'config': 'specify config path'
            },
            'server': {
                'prog': 'adms',
                'bind': '0.0.0.0',
                'port': 8008
            },
            'log': {
                'format': '%(asctime)s %(levelname)s %(message)s',
                'datefmt': '%m/%d/%Y %I:%M:%S %p',
                'loglevel': {
                    'default': 'warn',
                    'choices': ['info', 'warn', 'error']
                }
            }
        }
        return cli

    @classmethod
    def initialize(cls, cfgpath):
        ''' classmethod to be done at first '''

        try:
            with open(cfgpath) as file:
                info = load_yaml(file.read())
        except Exception as ex:
            logging.error('[LOAD_CFG] {}'.format(ex))
            exit()

        def init_db(info):
            ''' initialize database after getting all config '''

            mongoinfo = info['db']['mongo']['client']
            gridfsinfo = info['db']['gridfs']['client']

            mongo_db = DaoMongo.get_db(mongoinfo)
            dsp_tabObj = DaoMongo.get_tab(mongo_db, mongoinfo['dsp_tab'])
            adm_tabObj = DaoMongo.get_tab(mongo_db, mongoinfo['adm_tab'])
            media_tabObj = DaoMongo.get_tab(mongo_db, mongoinfo['media_tab'])
            gridfs_db = DaoGridFS.get_db(gridfsinfo)

            mongoinfo['dbObj'] = mongo_db
            mongoinfo['dsp_tabObj'] = dsp_tabObj
            mongoinfo['adm_tabObj'] = adm_tabObj
            mongoinfo['media_tabObj'] = media_tabObj
            gridfsinfo['dbObj'] = gridfs_db

            info['db']['mongo']['client'] = mongoinfo
            info['db']['gridfs']['client'] = gridfsinfo

            return info

        info = init_db(info)
        cls.__set_cfg(info)

    @classmethod
    def __set_cfg(cls, info):
        ''' prevent others to modify this config info '''

        cls.cfg = info

# coding: utf-8

import logging
from os import path

from .models.mdsp import Mdsp
from .utils.udefault import load_yaml
from .dao.mongo.daomongo import DaoMongo


class Config(object):
    ''' load all info from etc when starting webservice '''

    @classmethod
    def initialize(cls, cfgpath=(lambda: path.dirname\
            (path.dirname(path.abspath(__file__)))+'/etc/main.yaml')()):
        ''' classmethod to be done at first '''

        try:
            with open(cfgpath) as file:
                info = load_yaml(file.read())
        except Exception as ex:
            logging.error('[LOAD_CFG] {}'.format(ex))
            exit()

        def init_db(info):
            ''' initialize database after getting all config '''

            client = info['db']['mongo']['client']
            mongo_db = DaoMongo.get_db(client)
            dsp_tabObj = DaoMongo.get_tab(mongo_db, client['dsp_tab'])
            media_tabObj = DaoMongo.get_tab(mongo_db, client['media_tab'])

            client['dbObj'] = mongo_db
            client['dsp_tabObj'] = dsp_tabObj
            client['media_tabObj'] = media_tabObj
            info['db']['mongo']['client'] = client

            return info

        info = init_db(info)
        cls.__set_cfg(info)

    @classmethod
    def __set_cfg(cls, info):
        ''' prevent others to modify this config info '''

        cls.cfg = info

# coding: utf-8

import logging
import pymongo
from pymongo.errors import DuplicateKeyError

class DaoMongo(object):
    ''' data access object via mongo '''

    @classmethod
    def get_db(cls, mongoinfo):
        ''' connect to mongo via mongoinfo '''

        try:
            client = pymongo.MongoClient(mongoinfo['host'], mongoinfo['port'])
            dbObj = client[mongoinfo['db']]
        except Exception as ex:
            # TODO to exceptions.py in the future
            logging.error('[CONNECT_MONGO] {} >>> {} | {}'.format(ex, mongoinfo['host'], mongoinfo['port']))
            exit()
        return dbObj

    @classmethod
    def get_tab(cls, dbObj, tabname):
        ''' get table via tablename '''

        try:
            tabObj = dbObj[tabname]
        except Exception as ex:
            logging.error('[GET_MONGO_TABLE] {} >>> {} | {}'.format(ex, dbObj, tabname))
            exit()
        return tabObj

    @classmethod
    def insert_data(cls, tabObj, data):
        ''' save data to table in disk '''

        _id = None
        try:
            _id = tabObj.insert(data)
        except Exception as ex:
            logging.warn('[SAVE_TO_MONGO] {} >>> {} | {}'.format(ex, tabObj, data))
            if isinstance(ex, DuplicateKeyError):
                return True
            else:
                return False
        return _id

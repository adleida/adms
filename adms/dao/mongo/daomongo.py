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
            dbObj.authenticate(mongoinfo['user'], mongoinfo['pwd'], mechanism='MONGODB-CR')
        except Exception as ex:
            # TODO to exceptions.py in the future
            logging.error('[CONNECT_MONGO] {} >>> {}'.format(ex, mongoinfo))
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
    def insert_one(cls, tabObj, data):
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

    @classmethod
    def remove_one(cls, tabObj, condition, val):
        ''' remove one data via requirement '''

        affirm = {'n': 0}
        try:
            affirm = tabObj.remove({condition: val})
        except Exception as ex:
            logging.error('[DELETE_FROM_MONGO] {} >>> {} | {} {}'.format(ex, \
                    tabObj, condition, val))
            return 2
        if not affirm['n'] is 0:
            return True
        else:
            return False

    @classmethod
    def update_one(cls, tabObj, condition, val, update_info):
        ''' update one data via requirement '''

        affirm = {'nModified': 0}
        try:
            affirm = tabObj.update({condition: val}, {'$set': update_info})
        except Exception as ex:
            logging.error('[UPDATE_FROM_MONGO] {} >>> {} | {} {} | {}'.format(ex, \
                    tabObj, condition, val, update_info))
            return 2
        if not affirm['nModified'] is 0:
            return True
        else:
            return False

    @classmethod
    def update_one_inc(cls, tabObj, condition, val, inc_info):
        ''' update one data via requirement '''

        affirm = {'nModified': 0}
        try:
            affirm = tabObj.update({condition: val}, {'$inc': inc_info})
        except Exception as ex:
            logging.error('[UPDATE_FROM_MONGO] {} >>> {} | {} {} | {}'.format(ex, \
                    tabObj, condition, val, inc_info))
            return 2
        if not affirm['nModified'] is 0:
            return True
        else:
            return False

    @classmethod
    def update_one_sync(cls, tabObj, condition, val, update_info, inc_info):
        ''' update one data with update info and increasement info '''

        affirm = {'nModified': 0}
        try:
            affirm = tabObj.update({condition: val}, {'$set': update_info, '$inc': inc_info})
        except Exception as ex:
            logging.error('[UPDATE_FROM_MONGO] {} >>> {} | {} {} | {} | {}'.format(ex, \
                    tabObj, condition, val, update_info, inc_info))
            return 2
        if not affirm['nModified'] is 0:
            return True
        else:
            return False

    @classmethod
    def find_all(cls, tabObj, limit=None, skip=0):
        ''' find all documents from mongo '''

        try:
            if limit:
                cursor = tabObj.find().limit(limit).skip(skip)
            else:
                cursor = tabObj.find().skip(skip)
        except Exception as ex:
            logging.error('[FIND_ALL_FROM_MONGO] {} >>> {}'.format(ex, tabObj))
            return 2
        res = []
        for per in cursor:
            res.append(per)
        else:
            return res

    @classmethod
    def find_one(cls, tabObj, condition, val):
        ''' find one document from mongo '''

        try:
            res = tabObj.find_one({condition: val})
        except Exception as ex:
            logging.error('[FIND_ONE_FROM_MONGO] {} >>> {} | {} {}'.format(ex, \
                    tabObj, condition, val))
            return 2
        return res

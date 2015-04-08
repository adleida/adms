# coding: utf-8

import logging
import pymongo
from gridfs import GridFS
from gridfs.grid_file import FileExists


class DaoGridFS(object):
    ''' data access object via mongo '''

    @classmethod
    def get_db(cls, gridfsinfo):
        ''' get db object from pymongo '''

        try:
            client = pymongo.MongoClient(gridfsinfo['host'], gridfsinfo['port'])
            dbObj = client[gridfsinfo['db']]
            fsObj = GridFS(dbObj)
        except Exception as ex:
            logging.error('[CONNECT_GRIDFS] {} >>> {}'.format(ex, gridfsinfo))
            exit()
        return fsObj

    @classmethod
    def put(cls, fsObj, binary, _dict):
        ''' put [ file | media ] in gridfs '''

        # TODO fix return in the future
        try:
            _id = fsObj.put(binary, **_dict)
        except Exception as ex:
            logging.warn('[GRIDFS_PUT] {}'.format(ex))
            if isinstance(ex, FileExists):
                return True
            else:
                return False
        return _id

    @classmethod
    def get(cls, fsObj, _id):
        ''' get file by objId from fsObj '''

        try:
            binary = fsObj.get(_id).read()
        except Exception as ex:
            logging.error('[GET_FROM_GRIDFS] {} >>> {} | {}'.format(ex, fsObj, _id))
            # TODO fix in the future
            raise
            return 2
        return binary

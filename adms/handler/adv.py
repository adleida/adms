# coding: utf-8

import time
import logging
from flask import request
from flask.ext.restful import Resource, abort
from werkzeug import secure_filename
from werkzeug.exceptions import HTTPException

# here I get http response error code from global object cfg of Config class
from ..config import Config
from ..utils import udefault
from ..dao.mongo.daomongo import DaoMongo


class AdvHandler(Resource):

    # here build some shortcut variety to provide convenience
    __cfg = Config.cfg
    __param = __cfg['app']['param']
    __res = __cfg['http']['res']
    __dsp_tabObj = __cfg['db']['mongo']['client']['dsp_tabObj']
    __dsp = __cfg['model']['dsp']

    @classmethod
    def set_parser(cls, parser):
        cls.parser = parser
        return cls

    def post(self):
        ''' create advertisers' info '''

        # get data from request object handler and put it to memory in model class
        try:
            json_req = request.get_json()
        except HTTPException as ex:
            # TODO I'll put below bad coding to etc in the future
            abort(self.__res['code'][500], message=ex)

        # check format by using [ jsonschema ] here
        schemapath = Config.cfg['path']['schema']['dsp']
        ok, ex = udefault.check_schema(json_req, schemapath)
        if not ok:
            # TODO put below to etc in the future
            abort(self.__res['code'][400], message=ex.message)

        # insert data here in mongo
        # and first I specify [ id ] >>> [ _id ] in order to ensure primary key
        json_req['_id'] = json_req.pop(self.__dsp['id'])
        json_req.setdefault(self.__dsp['timestamp'], time.time())
        _id = DaoMongo.insert_data(self.__dsp_tabObj, json_req)
        if _id:
            if not _id is True:
                return self.__res['desc']['dsp201']
            else:
                abort(self.__res['code'][417], message=self.__res['desc']['duplicate417'])
        else:
            # TODO when error occured that log is too long
            abort(self.__res['code'][500], message=self.__res['desc']['insert500'])

    def delete(self):
        ''' remove advertisers's info '''

        args = parser.parse_args()
        id = args[__param['id']]

        # TODO connect to mongo and delete this record
        pass

    def put(self):
        ''' modify advertisers' info '''

        return 'put here'

    def get(self):
        ''' query from advertisers' info '''

        return 'get here'


# TODO delete then
class AdvTmp1(Resource):

    def get(self):
        return [
                   {
                       "burl": "http://dsp.ipinyou.com:8089/v1/bid/", 
                       "id": "dsp-0", 
                       "name": "mock dsp0"
                   }, 
                   {
                       "burl": "http://dsp1.adleida.com:6001/bids", 
                       "id": "dsp-1", 
                       "name": "mock dsp1"
                   }, 
                   {
                       "burl": "http://dsp2.adleida.com:6002/bids", 
                       "id": "dsp-2", 
                       "name": "mock dsp2"
                   }, 
                   {
                       "burl": "http://dsp3.adleida.com:6003/bids", 
                       "id": "dsp-3", 
                       "name": "mock dsp3"
                   }, 
                   {
                       "burl": "http://dsp4.adleida.com:6001/bids", 
                       "id": "dsp-4", 
                       "name": "mock dsp4"
                   }, 
                   {
                       "burl": "http://dsp5.adleida.com:6002/bids", 
                       "id": "dsp-5", 
                       "name": "mock dsp5"
                   }, 
                   {
                       "burl": "http://dsp6.adleida.com:6003/bids", 
                       "id": "dsp-6", 
                       "name": "mock dsp6"
                   }
               ]


class AdvTmp2(Resource):

    def get(self, string):
        return {
                   "burl": "http://dsp.ipinyou.com:8089/v1/bid/", 
                   "id": "dsp-0", 
                   "name": "mock dsp0"
               }

# coding: utf-8

import time
import logging
from flask import request
from flask.ext.restful import Resource, abort
from werkzeug.exceptions import HTTPException

# here I get http response error code from global object cfg of Config class
from ..config import Config
from ..utils import udefault
from ..dao.mongo.daomongo import DaoMongo


class DspHandler(Resource):

    # here build some shortcut variety to provide convenience
    __cfg = Config.cfg
    __param = __cfg['app']['param']

    __res = __cfg['http']['res']
    __token = __cfg['http']['req']['token']

    __dsp_tabObj = __cfg['db']['mongo']['client']['dsp_tabObj']
    __dsp = __cfg['model']['dsp']
    __fields = __res['fields']

    _auth = ()

    @classmethod
    def set_parser(cls, parser):
        cls.parser = parser
        return cls

    # TODO I'll implements multiply insert in the future
    def post(self):
        ''' create advertisers' info '''

        self._auth = _assert, _code = Authentication.verify(self.__token, \
                request.headers.get(self.__param['access_token']), self.__res)
        if _code: return self._auth

        # get data from request object handler and put it to memory in model class
        try:
            json_req = request.get_json()
        except HTTPException as ex:
            abort(self.__res['code'][500], message=ex)

        # check format by using [ jsonschema ] here
        schemapath = Config.cfg['path']['schema']['dsp']
        ok, ex = udefault.check_schema(json_req, schemapath)
        if not ok:
            abort(self.__res['code'][400], message=ex.message)

        # insert data here in mongo
        json_req.setdefault(self.__dsp['timestamp'], time.time())
        result = DaoMongo.insert_one(self.__dsp_tabObj, json_req)
        if result:
            if not result is True:
                return {
                           self.__fields['id']: str(result),
                           self.__fields['message']: self.__res['desc']['dsp201']
                       }
            else:
                abort(self.__res['code'][417], message=self.__res['desc']['dup417'])
        else:
            # TODO when error occured that log is too long
            abort(self.__res['code'][500], message=self.__res['desc']['insert500'])

    def delete(self):
        ''' remove advertisers's info '''

        self._auth = _assert, _code = Authentication.verify(self.__token, \
                request.headers.get(self.__param['access_token']), self.__res)
        if _code: return self._auth

        args = self.parser.parse_args()
        try:
            id_val = udefault.get_objId(args[self.__param['id']])
        except:
            abort(self.__res['code'][400], message=self.__res['desc']['del400'])
        result = DaoMongo.remove_one(self.__dsp_tabObj, '_id', id_val)
        if result:
            if result is 2:
                abort(self.__res['code'][500], message=self.__res['desc']['del500'])
            else:
                return self.__res['desc']['del200']
        else:
            return self.__res['desc']['delno200']

    def put(self):
        ''' modify advertisers' info '''

        self._auth = _assert, _code = Authentication.verify(self.__token, \
                request.headers.get(self.__param['access_token']), self.__res)
        if _code: return self._auth

        args = self.parser.parse_args()
        try:
            id_val = udefault.get_objId(args[self.__param['id']])
            name_val = args[self.__param['name']]
            burl_val = args[self.__param['burl']]
        except:
            abort(self.__res['code'][400], message=self.__res['desc']['put400'])
        if name_val and burl_val:
            update_info = {
                self.__dsp['name']: name_val,
                self.__dsp['burl']: burl_val }
        elif name_val:
            update_info = {
                self.__dsp['name']: name_val }
        elif burl_val:
            update_info = {
                self.__dsp['burl']: burl_val }
        else:
            abort(self.__res['code'][400], message=self.__res['desc']['update400'])

        result = DaoMongo.update_one(self.__dsp_tabObj, '_id', id_val, update_info)
        if result:
            if result is 2:
                abort(self.__res['code'][500], message=self.__res['desc']['update500'])
            else:
                return self.__res['desc']['put200']
        else:
            return self.__res['desc']['putno200']

    def get(self):
        ''' query all from advertisers' info '''

        self._auth = _assert, _code = Authentication.verify(self.__token, \
                request.headers.get(self.__param['access_token']), self.__res)
        if _code: return self._auth

        result = DaoMongo.find_all(self.__dsp_tabObj)
        if result:
            if result is 2:
                abort(self.__res['code']['500'], message=self.__res['desc']['getall500'])
            else:
                real_res = []
                for per in result:
                    per.pop(self.__dsp['timestamp'])
                    per[self.__dsp['id']] = str(per.pop('_id'))
                    real_res.append(per)
                return real_res
        else:
            return self.__res['desc']['getall200']


class DspHandlerOne(Resource):

    __cfg = Config.cfg
    __param = __cfg['app']['param']

    __token = __cfg['http']['req']['token']
    __res = __cfg['http']['res']

    __dsp_tabObj = __cfg['db']['mongo']['client']['dsp_tabObj']
    __dsp = __cfg['model']['dsp']

    _auth = ()

    @classmethod
    def set_parser(cls, parser):
        cls.parser = parser
        return cls

    def get(self, id):
        ''' query one dsp info from advertisers' records '''

        self._auth = _assert, _code = Authentication.verify(self.__token, \
                request.headers.get(self.__param['access_token']), self.__res)
        if _code: return self._auth

        try:
            id = udefault.get_objId(id)
        except:
            abort(self.__res['code'][400], message=self.__res['desc']['getone400'])
        result = DaoMongo.find_one(self.__dsp_tabObj, '_id', id)
        if result:
            if result is 2:
                abort(self.__res['code']['500'], message=self.__res['desc']['getone500'])
            else:
                result.pop(self.__dsp['timestamp'])
                result[self.__dsp['id']] = str(result.pop('_id'))
                return result
        else:
            return self.__res['desc']['getone200']

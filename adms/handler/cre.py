# coding: utf-8

import time
import logging
from flask import request, make_response, render_template, jsonify
from flask.ext.restful import Resource, abort
from werkzeug import secure_filename
from werkzeug.exceptions import HTTPException

from ..config import Config
from ..utils import udefault
from ..dao.mongo.daomongo import DaoMongo
from ..dao.mongo.daogridfs import DaoGridFS


class CreHandler(Resource):

    __cfg = Config.cfg
    __param = __cfg['app']['param']
    __url = __cfg['app']['url']
    __req = __cfg['http']['req']
    __res = __cfg['http']['res']
    __adm_tabObj = __cfg['db']['mongo']['client']['adm_tabObj']
    __media_tabObj = __cfg['db']['mongo']['client']['media_tabObj']
    __fsObj = __cfg['db']['gridfs']['client']['dbObj']
    __adm = __cfg['model']['adm']
    __media = __cfg['model']['media']
    __fields = __res['fields']

    @classmethod
    def set_parser(cls, parser):
        cls.parser = parser
        return cls

    # TODO I'll implements multiply insert in the future
    def post(self):
        ''' create advertisers' media info '''

        try:
            json_req = request.get_json()
        except HTTPException as ex:
            abort(self.__res['code'][500], message=ex)

        schemapath = Config.cfg['path']['schema']['adm']
        ok, ex = udefault.check_schema(json_req, schemapath)
        if not ok:
            abort(self.__res['code'][400], message=ex.message)

        # here I gather all fields which I need
        json_req.setdefault(self.__adm['timestamp'], time.time())
        media_id = json_req['data']['img'].rsplit('/', 1)[1]
        json_req.setdefault(self.__adm['media_id'], media_id)
        res = DaoMongo.insert_one(self.__adm_tabObj, json_req)
        if res:
            if not res is True:
                update_info = {
                    self.__media['updated']: time.time()
                }
                inc_info = {
                    self.__media['ref']: 1
                }
                affirm = DaoMongo.update_one_sync(self.__media_tabObj, '_id', media_id, \
                        update_info, inc_info)
                if not affirm is True:
                    abort(self.__res['code'][500], message=self.__res['desc']['sync500'])
                return {
                           self.__fields['id']: str(res),
                           self.__fields['message']: self.__res['desc']['adm201']
                       }
            else:
                abort(self.__res['code'][417], message=self.__res['desc']['dup417'])
        else:
            # TODO when error occured that log is too long
            abort(self.__res['code'][500], message=self.__res['desc']['insert500'])

    def delete(self):
        ''' remove advertisers' media info '''

        args = self.parser.parse_args()
        try:
            id_val = udefault.get_objId(args[self.__param['id']])
        except:
            abort(self.__res['code'][400], message=self.__res['desc']['del400'])
        find_res = DaoMongo.find_one(self.__adm_tabObj, '_id', id_val)
        if find_res:
            if find_res is 2:
                abort(self.__res['code'][500], message=self.__res['desc']['getone500'])
            else:
                media_id = find_res[self.__adm['media_id']]
        else:
            return self.__res['desc']['delno200']

        res = DaoMongo.remove_one(self.__adm_tabObj, '_id', id_val)
        if res:
            if res is 2:
                abort(self.__res['code'][500], message=self.__res['desc']['del500'])
            else:
                inc_info = {
                    self.__media['ref']: -1
                }
                affirm_inc = DaoMongo.update_one_inc(self.__media_tabObj, '_id', media_id, inc_info)
                if not affirm_inc is True:
                    abort(self.__res['code'][500], message=self.__res['desc']['sync500'])
                return self.__res['desc']['del200']
        else:
            return self.__res['desc']['delno200']

    def get(self):
        ''' query from advertisers' media info '''

        res = DaoMongo.find_all(self.__adm_tabObj)
        if res:
            if res is 2:
                abort(self.__res['code']['500'], message=self.__res['desc']['getall500'])
            else:
                real_res = []
                for per in res:
                    per.pop(self.__adm['media_id'])
                    per.pop(self.__adm['timestamp'])
                    per[self.__adm['id']] = str(per.pop('_id'))
                    real_res.append(per)
                return real_res
        else:
            return self.__res['desc']['getall200']

    @classmethod
    def upload(cls, request):

        def allowed_file(cls, filename):
            return '.' in filename and \
                   filename.rsplit('.', 1)[1] in cls.__req['allow_ext']

        if request.method == 'POST':
            # check if the post request has the file part
            if 'accept_file' not in request.files:
                abort(cls.__res['code'][400], message=cls.__res['desc']['part400'])
         
            # I get binary of file from provider here
            files = request.files.getlist('accept_file')

            total_res = {}
            num = 0
            for file in files:

                num += 1
                if file.filename == '':
                    abort(cls.__res['code'][417], message=cls.__res['desc']['selected417'])
             
                if file and allowed_file(cls, file.filename):
                    filename = secure_filename(file.filename)
                    binary = file.read()
                    _id = udefault.get_sha1(binary)

                    # define part of model here before saving to gridfs
                    media = {
                        '_id': _id,
                        'filename': _id,
                        cls.__media['ref']: 0,
                        cls.__media['approved']: False
                    }

                    res = DaoGridFS.put(cls.__fsObj, binary, media)
                    if res:
                        # below url return media location to users
                        # i.e. [ http://192.168.1.232:8008/v1/media/[id] ]
                        total_res.setdefault('{}#{}'.format(filename, num), \
                                '{}{}'.format(cls.__url['prompt'], _id))
                    else:
                        abort(cls.__res['code'][500], message=cls.__res['desc']['upload500'])
                else:
                    abort(cls.__res['code'][400], message=cls.__res['desc']['postfix400'])
            else:
                return jsonify(total_res)
        return render_template(cls.__cfg['path']['templates']['upload'])

    @classmethod
    def display(cls, id):
        ''' return get image via id '''

        # if you change _id from gridfs one day, please fix [ len(id) ] here
        if (not id) or (not len(id) == 40):
            abort(cls.__res['code'][400], message=cls.__res['desc']['getone400'])
        res = DaoMongo.find_one(cls.__media_tabObj, '_id', id)

        # if you debug advanced, commit below two lines
        if res[cls.__media['approved']] is False:
            return cls.__res['desc']['getnoapproved200']

        binary = DaoGridFS.get(cls.__fsObj, id)
        if binary is 2:
            abort(cls.__res['code']['500'], message=cls.__res['desc']['getone500'])
        response = make_response(binary)
        response.headers['Content-Type'] = 'image'
        return response


class CreHandlerOne(Resource):

    __cfg = Config.cfg
    __res = __cfg['http']['res']
    __adm_tabObj = __cfg['db']['mongo']['client']['adm_tabObj']
    __adm = __cfg['model']['adm']

    @classmethod
    def set_parser(cls, parser):
        cls.parser = parser
        return cls

    def get(self, id):
        ''' query one adm info from adm's records '''

        try:
            id = udefault.get_objId(id)
        except:
            abort(self.__res['code'][400], message=self.__res['desc']['getone400'])
        res = DaoMongo.find_one(self.__adm_tabObj, '_id', id)
        if res:
            if res is 2:
                abort(self.__res['code']['500'], message=self.__res['desc']['getone500'])
            else:
                res.pop(self.__adm['media_id'])
                res.pop(self.__adm['timestamp'])
                res[self.__adm['id']] = str(res.pop('_id'))
                return res
        else:
            return self.__res['desc']['getone200']

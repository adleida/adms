# coding: utf-8

import time
import logging
from flask import request, make_response, render_template, jsonify
from flask.ext.restful import Resource, abort
from werkzeug import secure_filename
from werkzeug.exceptions import HTTPException

from ..config import Config
from ..utils import udefault
from ..auth import Authentication
from ..dao.mongo.daomongo import DaoMongo
from ..dao.mongo.daogridfs import DaoGridFS


class CreHandler(Resource):

    __cfg = Config.cfg
    __param = __cfg['app']['param']
    __url = __cfg['app']['url']

    __req = __cfg['http']['req']
    __res = __cfg['http']['res']
    __token = __req['token']
    __fields = __res['fields']

    __adm_tabObj = __cfg['db']['mongo']['client']['adm_tabObj']
    __media_tabObj = __cfg['db']['mongo']['client']['media_tabObj']
    __fsObj = __cfg['db']['gridfs']['client']['dbObj']
    __adm = __cfg['model']['adm']
    __media = __cfg['model']['media']

    _auth = ()

    @classmethod
    def set_parser(cls, parser):
        cls.parser = parser
        return cls

    # TODO I'll implements multiply insert in the future
    def post(self):
        ''' create advertisers' media info '''

        self._auth = _assert, _code = Authentication.verify(self.__token, \
                request.headers.get(self.__param['access_token']), self.__res)
        if _code: return self._auth

        try:
            json_req = request.get_json()
        except HTTPException as ex:
            abort(self.__res['code'][500], message=ex)

        schemapath = Config.cfg['path']['schema']['adm']
        ok, ex = udefault.check_schema(json_req, schemapath)
        if not ok:
            abort(self.__res['code'][400], message=ex.message)

        ##### accept base64 condition #####
        # check the [ img ] field include string which start with [ http:// ] or not
        # and this action occured after checking jsonschema
        # process base64 encoded here!
        def rebase_post_adm(json_req, media_id, __dets, __defs, flag=False):
            ''' here I need rebase post action trace and provide for muliti one '''
            json_req.setdefault(__defs['__adm']['media_id'], media_id)
            json_req.setdefault(__defs['__adm']['timestamp'], time.time())
            if flag:
                json_req[__defs['__adm']['data']][__defs['__adm']['img']] = \
                        '{}{}'.format(__defs['__url']['prompt'], media_id)
            result = DaoMongo.insert_one(__dets['__adm_tabObj'], json_req)
            if result:
                if not result is True:
                    update_info = {
                        __defs['__media']['updated']: time.time()
                    }
                    inc_info = {
                        __defs['__media']['ref']: 1
                    }
                    affirm = DaoMongo.update_one_sync(__dets['__media_tabObj'], \
                            '_id', media_id, \
                            update_info, inc_info)
                    if not affirm is True:
                        abort(__defs['__res']['code'][500], \
                                message=__defs['__res']['desc']['sync500'])
                    return {
                               __defs['__fields']['id']: str(result),
                               __defs['__fields']['message']: __defs['__res']['desc']['adm201']
                           }
                abort(__defs['__res']['code'][417], message=__defs['__res']['desc']['dup417'])
            # TODO when error occured that log is too long
            abort(__defs['__res']['code'][500], message=__defs['__res']['desc']['insert500'])

        # collect some depend fields
        __defs = {
            '__adm': self.__adm,
            '__media': self.__media,
            '__res': self.__res,
            '__fields': self.__fields,
            '__url': self.__url
        }
        # collect some depend tables objects
        __dets = {
            '__adm_tabObj': self.__adm_tabObj,
            '__media_tabObj': self.__media_tabObj
        }

        img = json_req[self.__adm['data']][self.__adm['img']]
        if not img.startswith('http://'):
            try:
                binary = udefault.decode_from_base64(img)
            except HTTPException as ex:
                abort(self.__res['code'][500], message=ex)

            _id = udefault.get_sha1(binary)
            media = {
                '_id': _id,
                'filename': _id,
                self.__media['ref']: 0,
                self.__media['approved']: False
            }

            # if result is True, I'll continue save other adm info to mongo
            media_id = DaoGridFS.put(self.__fsObj, binary, media)
            if media_id:
                if media_id is True:
                    media_id = _id
                return rebase_post_adm(json_req, media_id, __dets, __defs, True)
            abort(self.__res['code'][500], message=self.__res['desc']['upload500'])

        ##### accept url condition #####
        # first of all here I gather all fields which I need
        media_id = img.rsplit('/', 1)[1]
        return rebase_post_adm(json_req, media_id, __dets, __defs)

    def delete(self):
        ''' remove advertisers' media info '''

        self._auth = _assert, _code = Authentication.verify(self.__token, \
                request.headers.get(self.__param['access_token']), self.__res)
        if _code: return self._auth

        args = self.parser.parse_args()
        try:
            id_val = udefault.get_objId(args[self.__param['id']])
        except:
            abort(self.__res['code'][400], message=self.__res['desc']['del400'])
        find_res = DaoMongo.find_one(self.__adm_tabObj, '_id', id_val)
        if find_res:
            if find_res is 2:
                abort(self.__res['code'][500], message=self.__res['desc']['getone500'])
            media_id = find_res[self.__adm['media_id']]
        return self.__res['desc']['delno200']

        result = DaoMongo.remove_one(self.__adm_tabObj, '_id', id_val)
        if result:
            if result is 2:
                abort(self.__res['code'][500], message=self.__res['desc']['del500'])
            inc_info = {
                self.__media['ref']: -1
            }
            affirm_inc = DaoMongo.update_one_inc(self.__media_tabObj, '_id', media_id, inc_info)
            if not affirm_inc is True:
                abort(self.__res['code'][500], message=self.__res['desc']['sync500'])
            return self.__res['desc']['del200']
        return self.__res['desc']['delno200']

    def get(self):
        ''' query from advertisers' media info '''

        self._auth = _assert, _code = Authentication.verify(self.__token, \
                request.headers.get(self.__param['access_token']), self.__res)
        if _code: return self._auth

        result = DaoMongo.find_all(self.__adm_tabObj)
        if result:
            if result is 2:
                abort(self.__res['code']['500'], message=self.__res['desc']['getall500'])
            real_res = []
            for per in result:
                per.pop(self.__adm['media_id'])
                per.pop(self.__adm['timestamp'])
                per[self.__adm['id']] = str(per.pop('_id'))
                real_res.append(per)
            return real_res
        return self.__res['desc']['getall200']

    @classmethod
    def upload(cls, request):

        def allowed_file(cls, filename):
            return '.' in filename and \
                   filename.rsplit('.', 1)[1] in cls.__req['allow_ext']

        if request.method == 'POST':

            # TODO below commited code may allow all people upload
            # TODO if one day use auth, you could discard page and switch uncommit
            # cls._auth = _assert, _code = Authentication.verify(cls.__token, \
            #         request.headers.get(cls.__param['access_token']), cls.__res)
            # if _code: return cls._auth

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

                    # below url return media location to users
                    # i.e. [ http://192.168.1.232:8008/v1/media/<id> ]
                    result = DaoGridFS.put(cls.__fsObj, binary, media)
                    if result:
                        total_res.setdefault('{}#{}'.format(filename, num), \
                                '{}{}'.format(cls.__url['prompt'], _id))
                    abort(cls.__res['code'][500], message=cls.__res['desc']['upload500'])
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
        result = DaoMongo.find_one(cls.__media_tabObj, '_id', id)

        # if you debug advanced, commit below two lines
        # if result[cls.__media['approved']] is False:
        #     return cls.__res['desc']['getnoapproved200']

        binary = DaoGridFS.get(cls.__fsObj, id)
        if binary is 2:
            abort(cls.__res['code']['500'], message=cls.__res['desc']['getone500'])
        response = make_response(binary)
        response.headers['Content-Type'] = 'image'
        return response

    @classmethod
    def verify_init(cls, scroll=False):
        ''' first time load verify.html and display info to template '''

        if not scroll:
            result = DaoMongo.find_all(cls.__adm_tabObj, \
                    cls.__req['init_limit'])
            # TODO I'll do skip number then
        else:
            result = DaoMongo.find_all(cls.__adm_tabObj, \
                    cls.__req['scroll_limit'], skip=0)

        if (result) and (not result is 2):
            for per in result:
                per[cls.__adm['id']] = str(per.pop('_id'))
                affirm = DaoMongo.find_one(cls.__media_tabObj, \
                        '_id', per[cls.__adm['media_id']])
                if affirm is 2:
                    return render_template(cls.__cfg['path']['templates']['verify'])
                per.setdefault(cls.__media['approved'], affirm[cls.__media['approved']])

            if not scroll:
                return render_template(cls.__cfg['path']['templates']['verify'], \
                        result=result)
            return jsonify(result=result)
        return render_template(cls.__cfg['path']['templates']['verify'])

    @classmethod
    def verify_click(cls):
        ''' on click event '''

        try:
            json_req = request.json
        except HTTPException as ex:
            abort(cls.__res['code'][500], message=ex)

        # key [ id ] and [ value ] here mapping js script's variable
        value = False if 'True' in json_req['value'] else True
        id = json_req['id']

        result = DaoMongo.update_one(cls.__media_tabObj, \
                '_id', id, { cls.__media['approved']: value })
        if result:
            if result is 2:
                abort(cls.__res['code'][500], message=cls.__res['desc']['update500'])
            return cls.__res['desc']['put200']
        return cls.__res['desc']['putno200']

    @classmethod
    def verify_scroll(cls):
        ''' on scroll event '''

        return cls.verify_init(scroll=True)


class CreHandlerOne(Resource):

    __cfg = Config.cfg
    __param = __cfg['app']['param']

    __token = __cfg['http']['req']['token']
    __res = __cfg['http']['res']

    __adm_tabObj = __cfg['db']['mongo']['client']['adm_tabObj']
    __adm = __cfg['model']['adm']

    _auth = ()

    @classmethod
    def set_parser(cls, parser):
        cls.parser = parser
        return cls

    def get(self, id):
        ''' query one adm info from adm's records '''

        self._auth = _assert, _code = Authentication.verify(self.__token, \
                request.headers.get(self.__param['access_token']), self.__res)
        if _code: return self._auth

        try:
            id = udefault.get_objId(id)
        except:
            abort(self.__res['code'][400], message=self.__res['desc']['getone400'])
        result = DaoMongo.find_one(self.__adm_tabObj, '_id', id)
        if result:
            if result is 2:
                abort(self.__res['code']['500'], message=self.__res['desc']['getone500'])
            result.pop(self.__adm['media_id'])
            result.pop(self.__adm['timestamp'])
            result[self.__adm['id']] = str(result.pop('_id'))
            return result
        return self.__res['desc']['getone200']

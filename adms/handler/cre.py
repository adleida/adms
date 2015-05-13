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

    def post(self):
        ''' create advertisers' media info '''

        def common_error_response(__defs, code, message, data):
            ''' rebase common error reponse '''

            return {
                       __defs['__fields']['code']: code,
                       __defs['__fields']['message']: message,
                       __defs['__fields']['request_data']: data
                   }

        def commence_post_adm(json_req, schemapath, __dets, __defs, batch_flag=False):
            ''' origin of post adm action '''

            ok, ex = udefault.check_schema(json_req, schemapath)
            if not ok:
                if batch_flag:
                    return common_error_response(__defs, __defs['__res']['code'][400], \
                            ex.message, \
                            json_req[__defs['__adm']['data']].pop(__defs['__adm']['img']))
                abort(__defs['__res']['code'][400], message=ex.message)

            img = json_req[__defs['__adm']['data']][__defs['__adm']['img']]
            if not img.startswith('http://'):
                try:
                    binary = udefault.decode_from_base64(img)
                except HTTPException as ex:
                    if batch_flag:
                        return common_error_response(__defs, __defs['__res']['code'][500], \
                                ex.message, \
                                json_req[__defs['__adm']['data']].pop(__defs['__adm']['img']))
                    abort(__defs['__res']['code'][500], message=ex)

                sha1 = udefault.get_sha1(binary)
                media = {
                    # consider some reason, I dont need use ref here
                    # '_id': _id,
                    # self.__media['ref']: 0,
                    'filename': sha1,
                    __defs['__media']['approved']: False
                }

                # if result is True, I'll continue save other adm info to mongo
                media_id = DaoGridFS.put(self.__fsObj, binary, media)
                if media_id:
                    return rebase_post_adm(json_req, media_id, \
                            __dets, __defs, \
                            base64_flag=True, batch_flag=batch_flag)
                if batch_flag:
                    return common_error_response(__defs, __defs['__res']['code'][500], \
                            __defs['__res']['desc']['upload500'], \
                            json_req[__defs['__adm']['data']].pop(__defs['__adm']['img']))
                abort(__defs['__res']['code'][500], message=__defs['__res']['desc']['upload500'])

            ##### accept url condition #####
            # first of all here I gather all fields which I need
            media_id = img.rsplit('/', 1)[1]
            return rebase_post_adm(json_req, media_id, \
                    __dets, __defs, \
                    batch_flag=batch_flag)

        ##### accept base64 condition #####
        # check the [ img ] field include string which start with [ http:// ] or not
        # and this action occured after checking jsonschema
        # process base64 encoded here!
        def rebase_post_adm(json_req, media_id, __dets, __defs, base64_flag=False, batch_flag=False):
            ''' here I need rebase post action trace and provide for muliti one '''

            json_req.setdefault(__defs['__adm']['media_id'], media_id)
            json_req.setdefault(__defs['__adm']['timestamp'], time.time())
            if base64_flag:
                json_req[__defs['__adm']['data']][__defs['__adm']['img']] = \
                        '{}{}'.format(__defs['__url']['prompt'], media_id)
            result = DaoMongo.insert_one(__dets['__adm_tabObj'], json_req)
            if result:
                update_info = {
                    __defs['__media']['updated']: time.time()
                }

                # this field may not cause more benefit
                # inc_info = {
                #     __defs['__media']['ref']: 1
                # }
                # affirm = DaoMongo.update_one_sync(__dets['__media_tabObj'], \
                #         '_id', media_id, \
                #         update_info, inc_info)
                
                affirm = DaoMongo.update_one(__dets['__media_tabObj'], \
                        '_id', media_id, update_info)
                if not affirm is True:
                    if batch_flag:
                        json_req.pop(__defs['__adm']['media_id'])
                        json_req.pop(__defs['__adm']['timestamp'])
                        if base64_flag:
                            json_req[__defs['__adm']['data']].pop(__defs['__adm']['img'])
                        return common_error_response(__defs, __defs['__res']['code'][500], \
                                __defs['__res']['desc']['sync500'], \
                                json_req)
                    abort(__defs['__res']['code'][500], \
                            message=__defs['__res']['desc']['sync500'])
                return {
                           __defs['__fields']['id']: str(result),
                           __defs['__fields']['message']: __defs['__res']['desc']['adm201']
                       }
            # TODO when error occured that log is too long
            if batch_flag:
                return common_error_response(__defs, __defs['__res']['code'][500], \
                        __defs['__res']['desc']['insert500'], \
                        json_req)
            abort(__defs['__res']['code'][500], message=__defs['__res']['desc']['insert500'])

        # here this API method could begin.
        self._auth = _assert, _code = Authentication.verify(self.__token, \
                request.headers.get(self.__param['access_token']), self.__res)
        if _code: return self._auth

        # collect some depend fields
        schemapath = Config.cfg['path']['schema']['adm']
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

        try:
            json_req = request.get_json()
        except HTTPException as ex:
            abort(self.__res['code'][500], message=ex)

        def iterate_batch_req(json_req):
            ''' here I implement multi post adm data '''

            total_result = []
            for per_req in json_req:
                per_result = commence_post_adm(per_req, schemapath, __dets, __defs, batch_flag=True)
                total_result.append(per_result)
            return total_result

        if type(json_req) is list:
            return iterate_batch_req(json_req)
        return commence_post_adm(json_req, schemapath, __dets, __defs)

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

        # the same reason to below, I commit some lines here
        # find_res = DaoMongo.find_one(self.__adm_tabObj, '_id', id_val)
        # if find_res:
        #     if find_res is 2:
        #         abort(self.__res['code'][500], message=self.__res['desc']['getone500'])
        #     media_id = find_res[self.__adm['media_id']]
        # return self.__res['desc']['delno200']

        result = DaoMongo.remove_one(self.__adm_tabObj, '_id', id_val)
        if result:
            if result is 2:
                abort(self.__res['code'][500], message=self.__res['desc']['del500'])

            # maybe I dont need to minus 1 fo field ref
            # inc_info = {
            #     self.__media['ref']: -1
            # }
            # affirm_inc = DaoMongo.update_one_inc(self.__media_tabObj, '_id', media_id, inc_info)
            # if not affirm_inc is True:
            #     abort(self.__res['code'][500], message=self.__res['desc']['sync500'])
            return self.__res['desc']['del200']
        return self.__res['desc']['delno200']

    def get(self):
        ''' query from advertisers' media info '''

        # TODO during debug time, I ban using of access_token
        # self._auth = _assert, _code = Authentication.verify(self.__token, \
        #         request.headers.get(self.__param['access_token']), self.__res)
        # if _code: return self._auth

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
        return self.__res['desc']['getall200'], self.__res['code'][404]

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
            total_result = {}
            num = 0

            for file in files:
                num += 1
                if file.filename == '':
                    abort(cls.__res['code'][417], message=cls.__res['desc']['selected417'])
             
                if file and allowed_file(cls, file.filename):
                    filename = secure_filename(file.filename)
                    binary = file.read()
                    sha1 = udefault.get_sha1(binary)

                    # define part of model here before saving to gridfs
                    media = {
                        'filename': sha1,
                        cls.__media['approved']: False
                    }

                    # below url return media location to users
                    # i.e. [ http://192.168.1.232:8008/v1/media/<id> ]
                    result = DaoGridFS.put(cls.__fsObj, binary, media)
                    if result:
                        total_result.setdefault('{}#{}'.format(filename, num), \
                                '{}{}'.format(cls.__url['prompt'], result))
                    else:
                        abort(cls.__res['code'][500], message=cls.__res['desc']['upload500'])
                else:
                    abort(cls.__res['code'][400], message=cls.__res['desc']['postfix400'])
            else:
                return jsonify(total_result)
        return render_template(cls.__cfg['path']['templates']['upload'])

    @classmethod
    def display(cls, id):
        ''' return get image via id '''

        # if you change _id from gridfs one day, please fix [ len(id) ] here
        if (not id) or (not len(id) == 24):
            abort(cls.__res['code'][400], message=cls.__res['desc']['getone400'])
        objId_val = udefault.get_objId(id)
        result = DaoMongo.find_one(cls.__media_tabObj, '_id', objId_val)

        # if you debug advanced, commit below two lines
        if result[cls.__media['approved']] is False:
            abort(cls.__res['code'][401], message=cls.__res['desc']['getnoapproved200'])

        binary = DaoGridFS.get(cls.__fsObj, objId_val)
        if binary is 2:
            abort(cls.__res['code'][500], message=cls.__res['desc']['getone500'])
        response = make_response(binary)
        response.headers['Content-Type'] = 'image'
        return response

    @classmethod
    def verify_init(cls, skip_num=None):
        ''' first time load verify.html and display info to template '''

        if skip_num is None:
            result = DaoMongo.find_all(cls.__adm_tabObj, \
                    cls.__req['init_limit'])
        else:
            result = DaoMongo.find_all(cls.__adm_tabObj, \
                    cls.__req['scroll_limit'], skip=skip_num)

        if (result) and (not result is 2):
            for per in result:
                per[cls.__adm['id']] = str(per.pop('_id'))
                affirm = DaoMongo.find_one(cls.__media_tabObj, \
                        '_id', per[cls.__adm['media_id']])
                if affirm is 2:
                    return render_template(cls.__cfg['path']['templates']['verify'])
                per.setdefault(cls.__media['approved'], affirm[cls.__media['approved']])

            if skip_num is None:
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

        # maybe here will bring reusable module
        # import ipdb; ipdb.set_trace()
        try:
            # json_req = request.json
            json_req = udefault.jsonloads(request.args.keys()[0])
        except HTTPException as ex:
            abort(cls.__res['code'][500], message=ex)
        skip_num = json_req['skipNum']
        return cls.verify_init(skip_num=skip_num)


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

        # TODO same reason of up
        # self._auth = _assert, _code = Authentication.verify(self.__token, \
        #         request.headers.get(self.__param['access_token']), self.__res)
        # if _code: return self._auth

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

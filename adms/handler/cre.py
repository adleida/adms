# coding: utf-8

from flask import request, abort, jsonify
from flask.ext.restful import Resource
from werkzeug import secure_filename
from werkzeug.exceptions import HTTPException


class CreHandler(Resource):

    @classmethod
    def set_parser(cls, parser):
        cls.parser = parser
        return cls

    def post(self):
        ''' create advertisers' media info '''

        pass

    def delete(self):
        ''' remove advertisers' media info '''

        pass

    def get(self):
        ''' query from advertisers' media info '''

        return app.args['accept']


# TODO delete then
class CreTmp(Resource):
    
    def get(self, id):
        return {
                   "data": {
                       "app_url": "http://www.app.com/download/", 
                       "img": "http://www.app.com/logo.png", 
                       "text": "app is very good"
                   }, 
                   "did": "dsp-0", 
                   "id": id, 
                   "type": 1
                }

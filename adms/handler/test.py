# coding: utf-8

from flask.ext.restful import Resource


class Test(Resource):

    def get(self):
        return 'Welcome to adleida restful API service!'

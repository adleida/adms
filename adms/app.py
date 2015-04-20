# coding: utf-8

from flask import Flask, request
from flask.ext.restful import reqparse, Api

from . import __version__
from .config import Config
from .handler.dsp import DspHandler, DspHandlerOne
from .handler.cre import CreHandler, CreHandlerOne

from .handler.test import Test


__app = Config.cfg['app']
__param = __app['param']
__url = __app['url']
__req = Config.cfg['http']['req']


app = Flask(__name__)
# return [413] if [ Request Entity Too Large ]
app.config['MAX_CONTENT_LENGTH'] = __req['size'] * 1024 * 1024
api = Api(app, catch_all_404s=True)

# TODO point location in the future
parser = reqparse.RequestParser()
parser.add_argument(__param['access_token'], type=str)
parser.add_argument(__param['id'], type=str)
parser.add_argument(__param['name'], type=str)
parser.add_argument(__param['burl'], type=str)


# just a test method
api.add_resource(Test, '/')

# for advertiser's methods >>> [ /v1/dsp/ ]
DspHandler = DspHandler.set_parser(parser)
api.add_resource(DspHandler, __url['dsp'])
DspHandlerOne = DspHandlerOne.set_parser(parser)
api.add_resource(DspHandlerOne, __url['one_dsp'])

# for adm's method >>> [ /v1/adm/ ]
# get one method >>> [ /v1/adm/<id> ]
CreHandler = CreHandler.set_parser(parser)
api.add_resource(CreHandler, __url['adm'])
CreHandlerOne = CreHandlerOne.set_parser(parser)
api.add_resource(CreHandlerOne, __url['one_adm'])


# for media's method >>> [ /v1/media/upload ]
@app.route(__url['upload'], methods=['GET', 'POST'])
def upload():
    return CreHandler.upload(request)


# for media's display method >>> [ /v1/media/<id> ]
@app.route(__url['media'], methods=['GET'])
def display(id):
    return CreHandler.display(id)

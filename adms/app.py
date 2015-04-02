# coding: utf-8

from flask import Flask
from flask.ext.restful import reqparse, Api

from . import __version__
from .config import Config
from .handler.adv import AdvHandler
from .handler.cre import CreHandler

# TODO delete then
from .handler.test import Test
from .handler.adv import AdvTmp1
from .handler.adv import AdvTmp2
from .handler.cre import CreTmp


app = Flask(__name__)
api = Api(app, catch_all_404s=True)

__app = Config.cfg['app']
__param = __app['param']
__url = __app['url']

# TODO point location in the future
parser = reqparse.RequestParser()
parser.add_argument(__param['id'], type=str)
parser.add_argument(__param['name'], type=str)
parser.add_argument(__param['burl'], type=str)


# just a test method
api.add_resource(Test, '/')

# for advertiser's methods >>> [ /v1/dsp ]
AdvHandler = AdvHandler.set_parser(parser)
api.add_resource(AdvHandler, __url['dsp'])

# for media's methods >>> [ /v1/adm ]
CreHandler = CreHandler.set_parser(parser)
api.add_resource(CreHandler, __url['adm'])

# TODO delete then, tmporary set here
# api.add_resource(AdvTmp1, '/v1/dsp/')
# api.add_resource(AdvTmp2, '/v1/dsp/<string>')
# api.add_resource(CreTmp, '/v1/adm/<id>')

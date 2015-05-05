# coding: utf-8

import io
import logging
import pkgutil
import hashlib
import yaml
import json
import jsonschema
from bson import ObjectId
from os import path
from toolz.functoolz import memoize


def load_yaml(data):
    ''' load yaml file as object ''' 

    try:
        cfg = yaml.load(data)
    except Exception as ex:
        logging.error('[LOAD_YAML] {}'.format(ex))
        exit()
    return cfg


@memoize
def load_resource(schemapath, as_object=True):
    ''' [from kev] parse file data to object format '''
 
    blob = pkgutil.get_data(__package__, schemapath)
    if not blob:
        raise Exception('no such resource: {}'.format(schemapath))
    data = blob.decode()

    if as_object:
        # split ext from file
        ext = path.splitext(schemapath)[-1]
        if ext in ['.json']:
            data = json.loads(data)
        elif ext in ['.yaml', '.yml']:
            data = yaml.load(io.StringIO(data))
        else:
            # TODO to etc in the future
            raise Exception('cannot detect resource type')
    return data


@memoize
def load_schema(schemapath):
    ''' [from kev] load json schema file from resource '''
           
    obj = load_resource(schemapath)
    schema = jsonschema.Draft4Validator(obj)
    return schema


def check_schema(obj, schemapath):
    ''' [from kev] check schema depends on jsonschema '''
 
    try:
        schema = load_schema(schemapath)
        schema.validate(obj)
        return True, None
    except Exception as ex:
        return False, ex


def get_sha1(obj):
    ''' transfer string or buffer to sha1 whose type is string '''

    return hashlib.sha1(obj).hexdigest()


def get_objId(string):
    ''' get objectId from string '''

    return ObjectId(string)


def encode_to_base64(string):
    ''' encode to base64 code from string '''

    return string.encode('base64')


def decode_from_base64(base64_string):
    ''' decode to string from base64 '''

    return base64_string.decode('base64')


def jsonloads(datastr):
    ''' string to json(dict) '''
            
    try: 
        datajson = json.loads(datastr)
    except Exception as ex: 
        logging.warn('[JSON_LOADS] {} --> {}'.format(ex, datastr))
        return []
    return datajson

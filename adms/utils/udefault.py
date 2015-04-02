# coding: utf-8

import io
import logging
import pkgutil
import yaml
import json
import jsonschema
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
        # TODO to etc in the future
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

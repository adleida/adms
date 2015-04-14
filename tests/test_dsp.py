# coding: utf-8

import json
from . import client


def test_get_one_record(client):

    res = client.get('/v1/dsp/5524ff421d41c834d120468e')
    assert json.loads(res.data)['burl'] == 'http://dsp.ipinyou.com:8089/v1/bid/'


def test_get_all_record(client):

    res = client.get('/v1/dsp/')
    assert list is type(json.loads(res.data))

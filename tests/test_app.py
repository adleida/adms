# coding: utf-8

from . import client


def test_index(client):

    res = client.get('/')
    assert 'Welcome' in res.data.decode('utf-8')

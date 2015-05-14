#!/usr/bin/env python
# coding: utf-8

import os
import adms
import pytest


# fixture could collect arguments which will be required of input
@pytest.fixture
def client(request):

    from adms.config import Config
    # Config.initialize(cfgpath=(lambda: os.path.dirname\
    #         (os.path.abspath(__file__))+'/etc/main.yaml')())
    Config.initialize(cfgpath='etc/main.yaml')
    from adms.app import app
    def teardown():
        pass
    return app.test_client()

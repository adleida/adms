#!/usr/bin/env python
# coding: utf-8

import adms
import pytest


# fixture could collect arguments which will be required of input
@pytest.fixture
def client(request):

    from adms import cli
    from adms.app import app
    def teardown():
        pass
    return app.test_client()

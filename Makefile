.PHONY: test, pack, upload

PKG = $(shell python setup.py --fullname).tar.gz
HOST = uc

test:
	py.test

run:
	python adms/cli.py -c etc/main.yaml

prep:
	sed -i '18s/# //g' ./adms/dao/mongo/daomongo.py
	sed -i '19s/# //g' ./adms/dao/mongo/daogridfs.py

local:
	sed -i "18s/dbObj/# dbObj/g" ./adms/dao/mongo/daomongo.py
	sed -i "19s/dbObj/# dbObj/g" ./adms/dao/mongo/daogridfs.py

pack:
	python setup.py sdist --formats=gztar

upload:
	scp dist/$(PKG) $(HOST):adms/;

clean:
	rm -rf adms.egg-info .tox dist
	find . -name '*.pyc' -delete
	find . -name '.*~' -delete
	find . -name '__pycache__' -delete

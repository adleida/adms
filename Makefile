.PHONY: test, pack, upload

PKG = $(shell python setup.py --fullname).tar.gz
HOST_UC = uuloop
HOST_118 = 118

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

upload_uc:
	scp dist/$(PKG) $(HOST_UC):adms/;
	scp etc/main.yaml $(HOST_UC):adms/;

upload_118:
	scp dist/$(PKG) $(HOST_118):adms/;
	scp etc/main.yaml $(HOST_118):adms/;

clean:
	rm -rf adms.egg-info .tox dist
	find . -name '*.pyc' -delete
	find . -name '.*~' -delete
	find . -name '__pycache__' -delete

.PHONY: test, pack, upload

PKG = $(shell python setup.py --fullname).tar.gz
HOST = uc

test:
	py.test

run:
	python adms/cli.py -c etc/main.yaml

prep:
	cat -n ./adms/dao/mongo/daomongo.py | sed -i '18s/# //g'
	cat -n ./adms/dao/mongo/daogridfs.py | sed -i '19s/# //g'

pack:
	python setup.py sdist --formats=gztar

upload:
	scp dist/$(PKG) $(HOST):adms/;

clean:
	rm -rf adms.egg-info .tox dist
	find . -name '*.pyc' -delete
	find . -name '.*~' -delete
	find . -name '__pycache__' -delete

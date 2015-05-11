#!/usr/bin/env python
# coding: utf-8

import os
import json
import argparse


def generate_base64_data(multi):
    num = 2
    total = []
    for root, dir, files in os.walk('./images/'):
        for file in files:
            with open(root+file) as foo:
                base64_val = foo.read().encode('base64')
            data = {
                'type': 1,
                'did': 'dsp-{}'.format(num),
                'data': {
                    'img': base64_val,
                    'text': 'minecraft is very good',
                    'app_url': 'http://www.app.com/download/'
                }
            }
            if not multi:
                with open('./adm-add-base64-samples/adm-add-base64-sample{}.json'.format(num), 'w+') as bar:
                    bar.write(json.dumps(data))
            else:
                total.append(data)
            num += 1

        if multi:
            with open('./adm-add-multi-base64-sample.json', 'w+') as foobar:
                foobar.write(json.dumps(total))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--multi', action='store_true', default=False)
    args = parser.parse_args()
    generate_base64_data(args.multi)

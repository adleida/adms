#!/usr/bin/env python
# coding: utf-8

import os
import yaml
import argparse
import requests
from PIL import Image


class Uploader(object):
    ''' simple script for uploading '''

    total_size = 0.0
    tmp_imgpath = None

    def __init__(self):
        ''' initialize command arguments '''

        parser = argparse.ArgumentParser(description='adleida simple command line uploader')
        parser.add_argument('-o', '--output', \
                help='decide to generate result.yaml from response', \
                action='store_true', default=False)
        parser.add_argument('-t', '--test', \
                help='test to mock local secne', \
                action='store_true', default=False)
        parser.add_argument('-s', '--substitute', \
                help='consider whether script substitute value of field img', \
                action='store_true', default=False)
        self.args = parser.parse_args()

    @staticmethod
    def preset_config(cls):
        ''' set init confgi variety '''

        cls._index_path = './index.yaml'
        cls._local_address = 'http://127.0.0.1:8008/v1/adm/'
        cls._remote_address = 'http://123.59.56.193:8008/v1/adm/'

    @staticmethod
    def preset_threshold(cls):
        ''' preset threshold '''

        cls.__limit_width = 300
        cls.__limit_height = 300
        cls.__limit_bytes = 5

    @classmethod
    def load_index(cls):
        ''' load index.yaml file '''

        try:
            with open(cls._index_path) as file:
                json_req = yaml.load(file.read())
        except:
            print '\nthe file >>> [ index.yaml ] must exist\n'
            exit()
        return json_req

    @classmethod
    def check_images(cls, json_req):
        ''' check image's validation '''

        def check_path(img_path):
            ''' check img's path validation '''

            if os.path.isabs(img_path):
                print 'for security reasons that absolute path is not allowed'
                print 'invalidate path >>> [ {} ], please fix it\n'.format(img_path)
                exit()

        def collect_bytes(img_path, cls):
            ''' check bytes of image '''

            try:
                cls.total_size += float(os.stat(img_path).st_size) / 1048576
            except:
                print 'is this path correctly? >>> [ {} ]\n'.format(img_path)
                exit()

        def read_image(img_path, cls):
            ''' read every request's img '''

            try:
                return Image.open(img_path)
            except:
                print 'this file is not image >>> [ {} ]\n'.format(img_path)
                exit()

        def check_format(img, img_path):
            ''' check image's validation of format '''

            if img.format not in ['GIF', 'JPEG', 'PNG', 'ICO']:
                print 'invalidate image\'s format >>> [ {} ]\n'.format(img_path)
                exit()

        def check_size(img, img_path, cls):
            ''' check image's validation of size '''

            def prompt_size_details(size, limit, img_path, prompt):
                print 'too large {} >>> [ {} ]\n'.format(prompt, img_path)
                exit()

            (width, height) = img.size
            if width > cls.__limit_width:
                prompt_size_details(width, cls.__limit_width, img_path, 'width')
            elif height > cls.__limit_height:
                prompt_size_details(height, cls.__limit_height, img_path, 'height')

        def check_bytes(img_path, cls):
            ''' check bytes of total images '''

            if cls.total_size > cls.__limit_bytes:
                print 'too large image\'s bytes >>> [ {} ]'.format(img_path)
                exit()

        print '\nstart checking validation of images ..\n'
        for per_req in json_req:
            img_path = per_req['data']['img']
            check_path(img_path)
            collect_bytes(img_path, cls)

            img = read_image(img_path, cls)
            check_format(img, img_path)
            check_size(img, img_path, cls)
            check_bytes(img_path, cls)

    def process_request_info(self, json_req):
        ''' after checking all images, start process request info '''

        for per_req in json_req:
            with open(per_req['data']['img']) as file:
                base64_val = file.read().encode('base64')
            per_req['data']['img'] = base64_val
        else:
            return json_req

    def commence_upload(self, json_req):
        ''' after processing, start uploading now '''

        def generate_result_from_response(json_res, index_path, address, substitute_flag):
            ''' consider flag to make decision to generate result.yaml '''

            try:
                with open(index_path) as file:
                    local_req = yaml.load(file.read())
            except:
                print 'in order to generate result.yaml, the file >>> [ index.yaml ] must exist\n'
                exit()

            for index, per_res in enumerate(json_res):
                per_res_id = per_res['id']
                try:
                    handler = requests.get('{}{}'\
                            .format(address, per_res_id))
                except Exception as ex:
                    print 'some unpredictable problem happend on internet >>> {}\n'.format(ex)
                    exit()
                local_req[index]['id'] = str(per_res_id)
                if substitute_flag:
                    local_req[index]['data']['img'] = str(handler.json()['data']['img'])
            else:
                with open('./result.yaml', 'w+') as file:
                    yaml.dump(local_req, file, default_flow_style=False, allow_unicode=True)

        def rebase_common_action(json_req, index_path, address, output_flag, substitute_flag):
            try:
                handler = requests.post(address, \
                        headers={'access_token':'d19a1398-ccf5-4c47-868c-a4abaf24e011'}, \
                        json=json_req)
            except Exception as ex:
                print 'some unpredictable problem happend on internet >>> {}\n'.format(ex)
                exit()
            print 'finish uploading\n\n'

            if output_flag:
                generate_result_from_response(handler.json(), index_path, address, substitute_flag)

        if self.args.test:
            rebase_common_action(json_req, \
                    self._index_path, self._local_address, \
                    self.args.output, self.args.substitute)
        else:
            rebase_common_action(json_req, \
                    self._index_path, self._remote_address, \
                    self.args.output, self.args.substitute)

    def main(self):
        ''' iterate content of request '''

        self.preset_config(Uploader)
        self.preset_threshold(Uploader)
        json_req = self.load_index()

        self.check_images(json_req)
        confirm_val = raw_input('finish checking, upload now?\t[Y/n]')
        if confirm_val in ['n', 'N']:
            print 'abort ..\n'
            exit()
        elif confirm_val in ['y', 'Y', '']:
            print '\nbegin ..\n'
            json_req = self.process_request_info(json_req)
            self.commence_upload(json_req)
        else:
            print 'please type correctly character >>> [Y/y/N/n]'
            print 'abort ..\n'
            exit()


if __name__ == '__main__':
    updr = Uploader()
    updr.main()

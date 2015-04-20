# coding: utf-8


class Authentication(object):
    ''' authentication module '''

    @staticmethod
    def verify(real_token, current_token, res):
        ''' verify current key equal real key '''

        if not current_token:
            return res['desc']['no401'], res['code'][401]
        elif current_token != real_token:
            return res['desc']['err401'], res['code'][401]
        return None, None

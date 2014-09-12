# -*- coding: utf-8 -*-

class YousignError(Exception):
    def __init__(self, message=None, code=None, short_message=None,
                 *args, **kwargs):
        super(YousignError, self).__init__(message, *args, **kwargs)
        self.message = message
        self.code = code
        self.short_message = short_message
